import os
from pathlib import Path
from ome_types import from_xml
import subprocess


class ArcPacker(object):
    def __init__(self, folder: Path):
        self.folder = folder
        os.makedirs(folder, exist_ok=False)

        subprocess.run(["arc", "init"], cwd=folder)
        self.ome = None

    def add_omero_data(self, source_folder: Path):
        with open(source_folder / "transfer.xml") as f:
            xmldata = f.read()

        self.ome = from_xml(xmldata)

    def create_investigation(self):
        assert self.ome is not None

        investigation_title = "Test Investigation 1"
        investigation_identifier = investigation_title.lower().replace(
            " ", "-"
        )

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
            cwd=self.folder,
        )
