from pathlib import Path
from ome_types import from_xml


class OmeroProject(object):
    def __init__(self, path_to_xml_source: Path):
        self.path_to_xml_source = path_to_xml_source
        self.ome = None
        self._add_omero_data(path_to_xml_source)

    def _add_omero_data(self, source_folder: Path):
        with open(source_folder / "transfer.xml") as f:
            xmldata = f.read()
        self.ome = from_xml(xmldata)
