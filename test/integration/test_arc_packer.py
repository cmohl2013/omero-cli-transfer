from integration.cli import AbstractArcTest
import pytest
from omero_cli_transfer import ArcPacker
import pandas as pd

import os


class TestArcPacker(AbstractArcTest):
    def test_arc_packer_read_omedata(self, path_omero_data_1, tmp_path):
        ap = ArcPacker(tmp_path / "my_arc", path_omero_data_1)
        assert ap.ome is not None
        print(tmp_path)

    def test_arc_packer_initialize(self, path_omero_data_1, tmp_path):
        path_to_arc_repo = tmp_path / "my_arc"
        ap = ArcPacker(
            path_to_arc_repo=path_to_arc_repo,
            path_to_xml_source=path_omero_data_1,
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
        ap = ArcPacker(
            path_to_arc_repo=path_to_arc_repo,
            path_to_xml_source=path_omero_data_1,
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
        ap = ArcPacker(
            path_to_arc_repo=path_to_arc_repo,
            path_to_xml_source=path_omero_data_1,
        )
        ap.initialize_arc_repo()

        ap._create_study()
        ap._create_assays()

        assert (path_to_arc_repo / "assays/my-first-assay").exists()
        assert (path_to_arc_repo / "assays/my-second-assay").exists()
        # assert (path_to_arc_repo / "studies/study_1/isa.study.xlsx").exists()

    def test_arc_packer_add_image_data_for_assay(
        self, path_omero_data_1, tmp_path
    ):
        path_to_arc_repo = tmp_path / "my_arc"
        ap = ArcPacker(
            path_to_arc_repo=path_to_arc_repo,
            path_to_xml_source=path_omero_data_1,
        )
        ap.initialize_arc_repo()

        ap._create_study()
        ap._create_assays()
        ap._add_image_data_for_assay(assay_identifier="my-first-assay")

        ome_dataset_id = ap.assay_identifiers["my-first-assay"]

        img_filenames_in_arc = os.listdir(
            tmp_path / "my_arc/assays/my-first-assay/dataset"
        )

        for img_filename in ap._ome_image_filenames_for_ome_dataset(
            ome_dataset_id
        ):
            assert img_filename.name in img_filenames_in_arc

    @pytest.fixture()
    def arc_repo_1(self, path_omero_data_1, tmp_path):
        path_to_arc_repo = tmp_path / "my_arc"
        ap = ArcPacker(
            path_to_arc_repo=path_to_arc_repo,
            path_to_xml_source=path_omero_data_1,
        )
        ap.initialize_arc_repo()

        ap._create_study()
        ap._create_assays()
        ap._add_image_data_for_assay(assay_identifier="my-first-assay")
        ap._add_image_data_for_assay(assay_identifier="my-second-assay")
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

    def test_czi(self, path_omero_data_czi):
        pass
