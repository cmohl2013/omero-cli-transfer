import os
from pathlib import Path
from ome_types import from_xml
import subprocess


def fmt_identifier(title: str) -> str:
    return title.lower().replace(" ", "-")


class ArcPacker(object):
    def __init__(self, path_to_arc_repo: Path, path_to_xml_source: Path):
        self.path_to_arc_repo = path_to_arc_repo
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
        study_identifier = fmt_identifier(study_title)

        subprocess.run(
            [
                "arc",
                "s",
                "add",
                "--identifier",
                study_identifier,
                "--title",
                study_title,
            ],
            cwd=self.path_to_arc_repo,
        )
