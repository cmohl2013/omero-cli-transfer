import os
from pathlib import Path
import subprocess
import shutil
import yaml
import importlib
import json
from arc_mapping import IsaStudyMapper, IsaAssayMapper

if importlib.util.find_spec("pandas"):
    import pandas as pd
else:
    raise ImportError(
        "Could not import pandas library. Make sure to "
        "install omero-cli-transfer with the optional "
        "[arc] addition"
    )


def fmt_identifier(title: str) -> str:
    return title.lower().replace(" ", "-")


class ArcPacker(object):
    def __init__(
        self, ome_object, path_to_arc_repo: Path, image_filenames_mapping, conn
    ):
        self.obj = ome_object  # must be a project
        self.path_to_arc_repo = path_to_arc_repo
        self.conn = conn
        self.image_filenames_mapping = image_filenames_mapping

        self.isa_assay_mappers = []

    def create_arc_repo(self):
        self.initialize_arc_repo()
        self._create_study()
        self._create_assays()
        for assay_mapper in self.isa_assay_mappers:
            assay_identifier = assay_mapper.isa_attributes_mapping[
                "assayidentifier"
            ]
            self._add_image_data_for_assay(assay_identifier)
            self._add_original_metadata_for_assay(assay_identifier)

    def initialize_arc_repo(self):
        os.makedirs(self.path_to_arc_repo, exist_ok=False)

        subprocess.run(["arc", "init"], cwd=self.path_to_arc_repo)

        investigation_title = "Test Investigation 1"
        investigation_identifier = fmt_identifier(investigation_title)

        subprocess.run(
            [
                "arc",
                "investigation",
                "create",
                "--identifier",
                investigation_identifier,
                "--title",
                investigation_title,
            ],
            cwd=self.path_to_arc_repo,
        )

    def _create_study(self):
        ome_project = self.obj

        mapper = IsaStudyMapper(ome_project)

        args = ["arc", "s", "add"]
        for isa_attribute in mapper.isa_attributes:
            option = f"--{isa_attribute}"
            value = mapper.isa_attributes[isa_attribute]
            args.append(option)
            args.append(value)

        subprocess.run(args, cwd=self.path_to_arc_repo)

    def isa_assay_tables(self, dataset_id):
        tables = []
        for sheetname in self.mapping_config["assay"]["sheets"]:
            col_mapping = self.mapping_config["assay"]["sheets"][sheetname][
                "target_columns"
            ]
            source_object_name = self.mapping_config["assay"]["sheets"][
                sheetname
            ]["source_objects"]

            obj_getter_func = self.omero_project.__getattribute__(
                source_object_name
            )
            objs = obj_getter_func(dataset_id)

            tbl = {}
            for col_spec in col_mapping:
                target_vals = []
                for obj in objs:
                    source_attribute = obj.__getattribute__(
                        col_spec["source_attribute"]
                    )
                    augmentation_method_name = col_spec.get(
                        "augmentation_method", None
                    )
                    if augmentation_method_name is not None:
                        augmentation_method = (
                            self.omero_project.__getattribute__(
                                augmentation_method_name
                            )
                        )
                        kwargs = col_spec.get("args", {})
                        target_val = augmentation_method(
                            source_attribute, **kwargs
                        )
                    else:
                        target_val = source_attribute
                    target_vals.append(target_val)
                tbl[col_spec["target_colname"]] = target_vals
            tables.append(pd.DataFrame(tbl))
        return tables

    def _create_assays(self):
        ome_project = self.obj
        project_id = ome_project.getId()
        study_mapper = IsaStudyMapper(ome_project)

        def _filename_for_image(image_id):
            return self.image_filenames_mapping[f"Image:{image_id}"]

        ome_datasets = self.conn.getObjects(
            "Dataset", opts={"Project": project_id}
        )
        for dataset in ome_datasets:
            mapper = IsaAssayMapper(dataset, _filename_for_image)
            self.isa_assay_mappers.append(mapper)
            args = ["arc", "a", "add"]
            args.append("--studyidentifier")
            args.append(study_mapper.isa_attributes["identifier"])
            for isa_attribute in mapper.isa_attributes_mapping:
                option = f"--{isa_attribute}"
                value = mapper.isa_attributes_mapping[isa_attribute]
                args.append(option)
                args.append(value)
            subprocess.run(args, cwd=self.path_to_arc_repo)

    def isa_assay_filename(self, assay_identifier):
        assert assay_identifier in self.assay_identifiers
        path = (
            self.path_to_arc_repo / f"assays/{assay_identifier}/isa.assay.xlsx"
        )
        assert path.exists()
        return path

    def _add_image_data_for_assay(self, assay_identifier):
        assert (
            assay_identifier in self.assay_identifiers
        ), f"assay {assay_identifier} does not exist: {self.assay_identifiers}"

        pass
        ome_dataset_id = self.assay_identifiers[assay_identifier]

        dest_image_folder = (
            self.path_to_arc_repo / f"assays/{assay_identifier}/dataset"
        )
        for image_id in self.omero_project.image_ids(ome_dataset_id):
            img_filepath_abs = self.omero_project.image_filename(
                image_id, abspath=True
            )
            img_fileppath_rel = self.omero_project.image_filename(
                image_id, abspath=False
            )
            target_path = dest_image_folder / img_fileppath_rel
            os.makedirs(target_path.parent, exist_ok=True)
            shutil.copy2(img_filepath_abs, target_path)

    def image_metadata_for_assay(self, assay_identifier):
        ome_dataset_id = self.assay_identifiers[assay_identifier]
        img_data = []
        for image_record in self.omero_project.images(ome_dataset_id):
            img_filename = self.omero_project.image_filename(
                image_record.id, abspath=False
            )
            metadata = (pd.DataFrame(image_record.pixels).set_index(0)).iloc[
                :, 0
            ]
            img_identifiers = pd.Series(
                {
                    "ome_id": image_record.id,
                    "name": image_record.name,
                    "description": image_record.description,
                    "filename": img_filename,
                }
            )
            img_data.append(pd.concat([img_identifiers, metadata]))
        return pd.concat(img_data, axis=1).T.set_index("filename")

    def _add_original_metadata_for_assay(self, assay_identifier):
        """writes json files with original metadata"""

        ome_dataset_id = self.assay_identifiers[assay_identifier]
        for ome_image_id in self.omero_project.image_ids(ome_dataset_id):
            metadata = self.omero_project.original_image_metadata(ome_image_id)
            id = ome_image_id.split(":")[1]
            savepath = self.path_to_arc_repo / (
                f"assays/{assay_identifier}"
                f"/protocols/ImageID{id}_metadata.json"
            )
            with open(savepath, "w") as f:
                json.dump(metadata, f, indent=4)

    def _add_image_metadata(self):
        for assay_identifier in self.assay_identifiers:
            df = self.image_metadata_for_assay(
                assay_identifier=assay_identifier
            )

            path = self.isa_assay_filename(assay_identifier)

            # book = load_workbook(path)
            writer = pd.ExcelWriter(path, engine="openpyxl", mode="a")
            # writer.book = book

            df.to_excel(writer, sheet_name="Image Metadata")
            writer.close()
