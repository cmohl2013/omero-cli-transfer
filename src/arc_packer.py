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
