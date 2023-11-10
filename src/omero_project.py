from pathlib import Path
from ome_types import from_xml
from generate_xml import list_file_ids


class OmeroProject(object):
    """
    Omero Project is a connector to packed omero data
    (xml with metadata and image files)
    """

    def __init__(self, path_to_xml_source: Path):
        self.path_to_xml_source = path_to_xml_source
        self.ome = None
        self._add_omero_data(path_to_xml_source)
        assert (
            len(self.ome.projects) == 1
        ), "ome dataset must contain exactly one project"

        self.project = self.ome.projects[0]
        self.datasets = [
            d for d in self.ome.datasets if d.id in self.dataset_ids()
        ]

        self._img_id_file_mapping = list_file_ids(self.ome)

    def _add_omero_data(self, source_folder: Path):
        with open(source_folder / "transfer.xml") as f:
            xmldata = f.read()
        self.ome = from_xml(xmldata)

    def dataset_ids(self):
        return [e.id for e in self.project.dataset_refs]

    def dataset(self, dataset_id):
        assert dataset_id in self.dataset_ids()
        for dataset in self.datasets:
            if dataset.id == dataset_id:
                return dataset

    def image_ids(self, dataset_id: str):
        dataset = self.dataset(dataset_id)
        return [i.id for i in dataset.image_refs]

    def _all_image_ids(self):
        all_image_ids = []
        for dataset_id in self.dataset_ids():
            all_image_ids += self.image_ids(dataset_id)
        return list(set(all_image_ids))

    def image(self, image_id: str):
        assert image_id in self._all_image_ids()
        for image in self.ome.images:
            if image.id == image_id:
                return image

    def images(self, dataset_id: str):
        return [
            self.image(image_id) for image_id in self.image_ids(dataset_id)
        ]

    def image_filename(self, image_id: str, abspath=True):
        rel_path = Path(self._img_id_file_mapping[image_id])
        if not abspath:
            return rel_path
        return self.path_to_xml_source / rel_path
