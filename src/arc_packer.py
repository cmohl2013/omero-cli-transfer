import os
from pathlib import Path


class ArcPacker(object):
    def __init__(self, folder: Path):
        self.folder = folder
        os.makedirs(folder, exist_ok=False)

    def add_omero_data(self, source_folder: Path):
        pass
