from integration.cli import AbstractArcTest
import pytest
from omero_cli_transfer import ArcPacker
import pandas as pd


class TestArcPacker(AbstractArcTest):
    def test_arc_packer_initialize(self, project_czi, tmp_path):
        path_to_arc_repo = tmp_path / "my_arc"
        ap = ArcPacker(
            ome_object=project_czi,
            path_to_arc_repo=path_to_arc_repo,
            path_to_image_files=None,
            image_filenames_mapping=None,
            conn=self.client,
        )
        ap.initialize_arc_repo()
        df = pd.read_excel(
            path_to_arc_repo / "isa.investigation.xlsx",
            index_col=0,
        )

        assert (
            df.loc["Investigation Identifier"].iloc[0]
            == "test-investigation-1"
        )
        assert df.loc["Investigation Title"].iloc[0] == "Test Investigation 1"

    def test_arc_packer_create_study(self, project_1, tmp_path):
        path_to_arc_repo = tmp_path / "my_arc"
        ap = ArcPacker(
            ome_object=project_1,
            path_to_arc_repo=path_to_arc_repo,
            path_to_image_files=None,
            image_filenames_mapping=None,
            conn=self.gw,
        )
        ap.initialize_arc_repo()

        ap._create_study()

        assert (path_to_arc_repo / "studies/my-first-study").exists()
        assert (
            path_to_arc_repo / "studies/my-first-study/isa.study.xlsx"
        ).exists()

        df = pd.read_excel(
            path_to_arc_repo / "studies/my-first-study/isa.study.xlsx",
            sheet_name="Study",
            index_col=0,
        )

        assert df.loc["Study Title"].iloc[0] == "My First Study"
        assert df.loc["Study Identifier"].iloc[0] == "my-first-study"

    def test_arc_packer_create_assays(self, project_1, tmp_path):
        path_to_arc_repo = tmp_path / "my_arc"
        ap = ArcPacker(
            ome_object=project_1,
            path_to_arc_repo=path_to_arc_repo,
            path_to_image_files=None,
            image_filenames_mapping=None,
            conn=self.gw,
        )
        ap.initialize_arc_repo()

        ap._create_study()
        ap._create_assays()

        assert (path_to_arc_repo / "assays/my-first-assay").exists()
        assert (path_to_arc_repo / "assays/my-second-assay").exists()

    def test_arc_packer_add_image_data_for_assay(
        self,
        project_czi,
        path_omero_data_czi,
        omero_data_czi_image_filenames_mapping,
        tmp_path,
    ):
        path_to_arc_repo = tmp_path / "my_arc"

        ap = ArcPacker(
            ome_object=project_czi,
            path_to_arc_repo=path_to_arc_repo,
            path_to_image_files=path_omero_data_czi,
            image_filenames_mapping=omero_data_czi_image_filenames_mapping,
            conn=self.gw,
        )
        ap.initialize_arc_repo()

        ap._create_study()
        ap._create_assays()
        ap._add_image_data_for_assay(assay_identifier="my-first-assay")
        ap._add_image_data_for_assay(
            assay_identifier="my-assay-with-czi-images"
        )

        dataset = ap.ome_dataset_for_isa_assay["my-first-assay"]
        for image in self.gw.getObjects(
            "Image", opts={"dataset": dataset.getId()}
        ):
            relpath = ap.image_filename(image.getId(), abspath=False)
            abspath = (
                tmp_path / "my_arc/assays/my-first-assay/dataset" / relpath
            )
            assert abspath.exists()

    @pytest.fixture()
    def arc_repo_1(self, path_omero_data_1, tmp_path):
        path_to_arc_repo = tmp_path / "my_arc"
        p = OmeroProject(path_omero_data_1, self.gw)
        ap = ArcPacker(
            path_to_arc_repo=path_to_arc_repo,
            omero_project=p,
        )
        ap.create_arc_repo()

        return ap

    def test_original_metadata(
        self,
        project_czi,
        omero_data_czi_image_filenames_mapping,
        path_omero_data_czi,
        tmp_path,
    ):
        path_to_arc_repo = tmp_path / "my_arc"

        ap = ArcPacker(
            ome_object=project_czi,
            path_to_arc_repo=path_to_arc_repo,
            path_to_image_files=path_omero_data_czi,
            image_filenames_mapping=omero_data_czi_image_filenames_mapping,
            conn=self.gw,
        )

        ap.create_arc_repo()

        # ap._add_original_metadata()
        datasets = self.gw.getObjects(
            "Dataset", opts={"project": project_czi.getId()}
        )

        for dataset in datasets:
            folder = (
                path_to_arc_repo
                / f"assays/{dataset.name.lower().replace(' ','-')}/protocols"
            )
            images = self.gw.getObjects(
                "Image", opts={"dataset": dataset.getId()}
            )
            for image in images:
                metadata_filepath = (
                    folder / f"ImageID{image.getId()}_metadata.json"
                )
                print(metadata_filepath)
                assert metadata_filepath.exists()

    def test_generate_isa_assay_tables(
        self,
        project_czi,
        omero_data_czi_image_filenames_mapping,
        path_omero_data_czi,
        tmp_path,
    ):
        path_to_arc_repo = tmp_path / "my_arc"

        ap = ArcPacker(
            ome_object=project_czi,
            path_to_arc_repo=path_to_arc_repo,
            path_to_image_files=path_omero_data_czi,
            image_filenames_mapping=omero_data_czi_image_filenames_mapping,
            conn=self.gw,
        )

        ap.create_arc_repo()

        dfs = ap.isa_assay_tables(assay_identifier="my-assay-with-czi-images")
        pass
