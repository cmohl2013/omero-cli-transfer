import os
from pathlib import Path
from ome_types import from_xml
import subprocess
import shutil
import yaml
import importlib

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
    def __init__(self, path_to_arc_repo: Path, path_to_xml_source: Path):
        self.path_to_arc_repo = path_to_arc_repo
        self.path_to_xml_source = path_to_xml_source
        self._add_omero_data(path_to_xml_source)
        self._read_mapping_config()

    def _add_omero_data(self, source_folder: Path):
        with open(source_folder / "transfer.xml") as f:
            xmldata = f.read()

        self.ome = from_xml(xmldata)

    def _read_mapping_config(self):
        path = Path(__file__).parent.parent / "arc_mapping.yml"

        with open(path, "r") as f:
            self.mapping_config = yaml.safe_load(f)

    def initialize_arc_repo(self):
        assert self.ome is not None
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
        assert (
            len(self.ome.projects) == 1
        ), "only datasets containing one project are allowed"

        project = self.ome.projects[0]

        args_from_config = self.mapping_config["study"]["arc_commander_args"]
        study_title = project.name
        self.study_identifier = fmt_identifier(study_title)
        args = ["arc", "s", "add"]
        for key in args_from_config:
            option_arg_string = f"--{key}"
            args.append(option_arg_string)
            value = args_from_config[key]
            if isinstance(value, dict):
                for func_arg_name in value.keys():
                    augmentation_func_name = value[func_arg_name][
                        "augmentation_method"
                    ]
                    augmentation_func = eval(augmentation_func_name)
                    augmented_value = augmentation_func(eval(func_arg_name))
                    args.append(augmented_value)

            else:
                args.append(eval(args_from_config[key]))
        subprocess.run(args, cwd=self.path_to_arc_repo)

    def _create_assays(self):
        measurement_type = "Microscopy"

        dataset_ids = [e.id for e in self.ome.projects[0].dataset_refs]
        datasets_selected = [
            e for e in self.ome.datasets if e.id in dataset_ids
        ]

        self.assay_identifiers = {}
        for dataset in datasets_selected:
            assay_identifier = fmt_identifier(dataset.name)
            self.assay_identifiers[assay_identifier] = dataset.id
            subprocess.run(
                [
                    "arc",
                    "a",
                    "add",
                    "--studyidentifier",
                    self.study_identifier,
                    "--assayidentifier",
                    assay_identifier,
                    "--measurementtype",
                    measurement_type,
                ],
                cwd=self.path_to_arc_repo,
            )

    def isa_assay_filename(self, assay_identifier):
        assert assay_identifier in self.assay_identifiers
        path = (
            self.path_to_arc_repo / f"assays/{assay_identifier}/isa.assay.xlsx"
        )
        assert path.exists()
        return path

    def _ome_dataset_info(self, ome_dataset_id):
        dataset_sel = [e for e in self.ome.datasets if e.id == ome_dataset_id]
        assert len(dataset_sel) == 1, "dataset not existing"
        return dataset_sel[0]

    def _image_ids_for_ome_dataset(self, ome_dataset_id):
        dataset_sel = self._ome_dataset_info(ome_dataset_id)

        return [e.id for e in dataset_sel.image_refs]

    def _ome_image_filenames_for_ome_dataset(
        self, ome_dataset_id, img_fmt=".tiff"
    ):
        image_ids = self._image_ids_for_ome_dataset(ome_dataset_id)
        return self._ome_image_filenames_for_ome_image_ids(
            image_ids, img_fmt=img_fmt
        )

    def _ome_image_filename_for_ome_image_id(
        self, ome_image_id, img_fmt=".tiff"
    ):
        img_id = ome_image_id.split(":")[1]
        img_filepath = (
            self.path_to_xml_source / f"pixel_images/{img_id}"
        ).with_suffix(img_fmt)
        return img_filepath

    def _ome_image_filenames_for_ome_image_ids(
        self, ome_image_ids, img_fmt=".tiff"
    ):
        return [
            self._ome_image_filename_for_ome_image_id(id, img_fmt=img_fmt)
            for id in ome_image_ids
        ]

    def _add_image_data_for_assay(self, assay_identifier):
        assert (
            assay_identifier in self.assay_identifiers
        ), f"assay {assay_identifier} does not exist: {self.assay_identifiers}"

        pass
        ome_dataset_id = self.assay_identifiers[assay_identifier]

        dest_image_folder = (
            self.path_to_arc_repo / f"assays/{assay_identifier}/dataset"
        )
        for img_filepath in self._ome_image_filenames_for_ome_dataset(
            ome_dataset_id
        ):
            shutil.copy2(img_filepath, dest_image_folder / img_filepath.name)

    def image_metadata_for_assay(self, assay_identifier):
        ome_dataset_id = self.assay_identifiers[assay_identifier]
        image_ids = self._image_ids_for_ome_dataset(ome_dataset_id)

        image_records_sel = [e for e in self.ome.images if e.id in image_ids]

        img_data = []
        for image_record in image_records_sel:
            img_filename = self._ome_image_filename_for_ome_image_id(
                image_record.id, img_fmt=".tiff"
            )
            metadata = (pd.DataFrame(image_record.pixels).set_index(0)).iloc[
                :, 0
            ]
            img_identifiers = pd.Series(
                {
                    "ome_id": image_record.id,
                    "name": image_record.name,
                    "description": image_record.description,
                    "filename": img_filename.name,
                }
            )
            img_data.append(pd.concat([img_identifiers, metadata]))
        return pd.concat(img_data, axis=1).T.set_index("filename")

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
