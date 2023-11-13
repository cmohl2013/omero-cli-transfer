from integration.cli import AbstractArcTest
from omero_cli_transfer import OmeroProject


class TestOmeroProject(AbstractArcTest):
    def test_omero_project_read_omedata(self, path_omero_data_1):
        p = OmeroProject(path_omero_data_1, self.gw)
        assert p.ome is not None

    def test_omero_project_dataset_ids(self, path_omero_data_1):
        p = OmeroProject(path_omero_data_1, self.gw)
        got = p.dataset_ids()
        assert len(got) == 2
        for id in got:
            assert id.split(":")[0] == "Dataset"
        print(p.datasets)

    def test_omero_project_images(self, path_omero_data_1):
        p = OmeroProject(path_omero_data_1, self.gw)
        dataset_id = p.dataset_ids()[0]
        got = p.images(dataset_id)
        assert len(got) == 3

    def test_omero_project_image_filename(self, path_omero_data_1):
        p = OmeroProject(path_omero_data_1, self.gw)
        dataset_id = p.dataset_ids()[0]
        image_id = p.image_ids(dataset_id)[0]
        path_to_file = p.image_filename(image_id, abspath=False)
        assert str(path_to_file.parent) == "pixel_images"
        assert path_to_file.suffix == ".tiff"

    def test_omero_original_image_metadata(
        self,
        path_omero_data_czi,
    ):
        p = OmeroProject(path_omero_data_czi, self.gw)
        dataset_id = p.dataset_ids()[0]
        for image_id in p.image_ids(dataset_id):
            metadata = p.original_image_metadata(image_id)
            if p.image_filename(image_id).suffix == ".czi":
                assert len(metadata["series_metadata"]) == 10129
                assert metadata["global_metadata"] is None
            elif p.image_filename(image_id).suffix == ".tiff":
                assert metadata["global_metadata"] is None
                assert metadata["series_metadata"] is None

            elif p.image_filename(image_id).suffix == ".lif":
                assert metadata["series_metadata"] is None
                assert len(metadata["global_metadata"]) == 432
