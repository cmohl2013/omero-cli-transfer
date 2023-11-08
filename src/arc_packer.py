import os
from pathlib import Path
from ome_types import from_xml
import subprocess
import shutil


def fmt_identifier(title: str) -> str:
    return title.lower().replace(" ", "-")


class ArcPacker(object):
    def __init__(self, path_to_arc_repo: Path, path_to_xml_source: Path):
        self.path_to_arc_repo = path_to_arc_repo
        self.path_to_xml_source = path_to_xml_source
        self._add_omero_data(path_to_xml_source)

    def _add_omero_data(self, source_folder: Path):
        with open(source_folder / "transfer.xml") as f:
            xmldata = f.read()

        self.ome = from_xml(xmldata)

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

        project_info = self.ome.projects[0]
        study_title = project_info.name
        self.study_identifier = fmt_identifier(study_title)

        subprocess.run(
            [
                "arc",
                "s",
                "add",
                "--identifier",
                self.study_identifier,
                "--title",
                study_title,
            ],
            cwd=self.path_to_arc_repo,
        )

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

    def _ome_dataset_info(self, ome_dataset_id):
        dataset_sel = [e for e in self.ome.datasets if e.id == ome_dataset_id]
        assert len(dataset_sel) == 1, "dataset not existing"
        return dataset_sel[0]

    def _ome_image_filenames_for_ome_dataset(
        self, ome_dataset_id, img_fmt=".tiff"
    ):
        dataset_sel = self._ome_dataset_info(ome_dataset_id)

        image_ids = [e.id.split(":")[1] for e in dataset_sel.image_refs]
        out = []
        for image_id in image_ids:
            img_filepath = (
                self.path_to_xml_source / f"pixel_images/{image_id}"
            ).with_suffix(img_fmt)
            assert img_filepath.exists()
            out.append(img_filepath)
        return out

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
