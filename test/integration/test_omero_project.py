from integration.cli import AbstractArcTest
from omero_cli_transfer import OmeroProject


class TestOmeroProject(AbstractArcTest):
    def test_omero_project_read_omedata(self, path_omero_data_1):
        p = OmeroProject(path_omero_data_1)
        assert p.ome is not None

    def test_omero_project_dataset_ids(self, path_omero_data_1):
        p = OmeroProject(path_omero_data_1)
        got = p.dataset_ids()
        assert len(got) == 2
        for id in got:
            assert id.split(":")[0] == "Dataset"
        print(p.datasets)

    def test_omero_project_images(self, path_omero_data_1):
        p = OmeroProject(path_omero_data_1)
        dataset_id = p.dataset_ids()[0]
        got = p.images(dataset_id)
        assert len(got) == 3

    def test_omero_project_image_filename(self, path_omero_data_1):
        p = OmeroProject(path_omero_data_1)
        dataset_id = p.dataset_ids()[0]
        image_id = p.image_ids(dataset_id)[0]
        path_to_file = p.image_filename(image_id, abspath=False)
        assert str(path_to_file.parent) == "pixel_images"
        assert path_to_file.suffix == ".tiff"
