from integration.cli import AbstractArcTest
import pytest
from omero_cli_transfer import ArcPacker, OmeroProject
import pandas as pd


class TestArcPacker(AbstractArcTest):
    def test_arc_packer_initialize(self, path_omero_data_1, tmp_path):
        path_to_arc_repo = tmp_path / "my_arc"
        p = OmeroProject(path_omero_data_1, self.gw)
        ap = ArcPacker(
            path_to_arc_repo=path_to_arc_repo,
            omero_project=p,
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

    def test_arc_packer_create_studies(self, path_omero_data_1, tmp_path):
        path_to_arc_repo = tmp_path / "my_arc"
        p = OmeroProject(path_omero_data_1, self.gw)
        ap = ArcPacker(
            path_to_arc_repo=path_to_arc_repo,
            omero_project=p,
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

    def test_arc_packer_create_assays(self, path_omero_data_1, tmp_path):
        path_to_arc_repo = tmp_path / "my_arc"
        p = OmeroProject(path_omero_data_1, self.gw)
        ap = ArcPacker(
            path_to_arc_repo=path_to_arc_repo,
            omero_project=p,
        )
        ap.initialize_arc_repo()

        ap._create_study()
        ap._create_assays()

        assert (path_to_arc_repo / "assays/my-first-assay").exists()
        assert (path_to_arc_repo / "assays/my-second-assay").exists()
        # assert (path_to_arc_repo / "studies/study_1/isa.study.xlsx").exists()

    def test_arc_packer_add_image_data_for_assay(
        self, path_omero_data_czi, tmp_path
    ):
        path_to_arc_repo = tmp_path / "my_arc"
        p = OmeroProject(path_omero_data_czi, self.gw)
        ap = ArcPacker(
            path_to_arc_repo=path_to_arc_repo,
            omero_project=p,
        )
        ap.initialize_arc_repo()

        ap._create_study()
        ap._create_assays()
        ap._add_image_data_for_assay(assay_identifier="my-first-assay")
        ap._add_image_data_for_assay(
            assay_identifier="my-assay-with-czi-images"
        )

        dataset_id = ap.assay_identifiers["my-first-assay"]
        for image_id in ap.omero_project.image_ids(dataset_id):
            relpath = ap.omero_project.image_filename(image_id, abspath=False)
            abspath = (
                tmp_path / "my_arc/assays/my-first-assay/dataset" / relpath
            )
            assert abspath.exists()

        dataset_id = ap.assay_identifiers["my-assay-with-czi-images"]
        for image_id in ap.omero_project.image_ids(dataset_id):
            relpath = ap.omero_project.image_filename(image_id, abspath=False)
            abspath = (
                tmp_path
                / "my_arc/assays/my-assay-with-czi-images/dataset"
                / relpath
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

    def test_arc_packer_image_metadata(self, arc_repo_1):
        ap = arc_repo_1
        ap.image_metadata_for_assay("my-first-assay")
        ap._add_image_metadata()

        pass

    def test_arc_packer_read_mapping_config(self, arc_repo_1):
        ap = arc_repo_1

        ap._read_mapping_config()
        assert ap.mapping_config is not None

    def test_original_metadata(self, path_omero_data_czi, tmp_path):
        path_to_arc_repo = tmp_path / "my_arc"
        p = OmeroProject(path_omero_data_czi, self.gw)
        ap = ArcPacker(
            path_to_arc_repo=path_to_arc_repo,
            omero_project=p,
        )
        ap.create_arc_repo()
        ap._add_original_metadata()

        for dataset_id in p.dataset_ids():
            dataset = p.dataset(dataset_id)
            folder = (
                path_to_arc_repo
                / f"assays/{dataset.name.lower().replace(' ','-')}/protocols"
            )
            for image_id in p.image_ids(dataset_id):
                id = image_id.split(":")[1]
                metadata_filepath = folder / f"ImageID{id}_metadata.json"
                print(metadata_filepath)
                assert metadata_filepath.exists()
