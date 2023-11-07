from integration.cli import AbstractArcTest
import pytest
from pathlib import Path
from omero_cli_transfer import ArcPacker
import pandas as pd

import os
import tarfile
import shutil


class TestArcPacker(AbstractArcTest):
    @pytest.fixture(scope="function")
    def path_arc_test_data(self, project_1, request):
        path_to_arc_test_data = (
            Path(__file__).parent.parent / "data/arc_test_data"
        )
        os.makedirs(path_to_arc_test_data, exist_ok=True)

        if request.config.option.not_create_arc_test_data:
            # if pytest is used with option --not-create-arc-test-data
            return path_to_arc_test_data

        shutil.rmtree(path_to_arc_test_data)
        os.makedirs(path_to_arc_test_data, exist_ok=True)
        project_identifier = f"Project:{project_1.id._val}"
        path_to_arc_test_dataset_1 = path_to_arc_test_data / "project_1"
        args = self.args + [
            "pack",
            project_identifier,
            str(path_to_arc_test_dataset_1),
        ]
        self.cli.invoke(args)

        with tarfile.open(path_to_arc_test_dataset_1.with_suffix(".tar")) as f:
            f.extractall(path_to_arc_test_dataset_1)
        os.remove(path_to_arc_test_dataset_1.with_suffix(".tar"))

        return path_to_arc_test_data

    @pytest.fixture(scope="function")
    def path_omero_data_1(self, path_arc_test_data):
        return path_arc_test_data / "project_1"

    def test_arc_packer_read_omedata(self, path_omero_data_1, tmp_path):
        ap = ArcPacker(tmp_path / "my_arc")

        ap.add_omero_data(path_omero_data_1)

        assert ap.ome is not None
        print(tmp_path)

    def test_arc_packer_create_investigation(
        self, path_omero_data_1, tmp_path
    ):
        path_to_arc_repo = tmp_path / "my_arc"
        ap = ArcPacker(path_to_arc_repo)
        ap.add_omero_data(path_omero_data_1)

        ap.create_investigation()
        df = pd.read_excel(
            path_to_arc_repo / "isa.investigation.xlsx",
            index_col=0,
        )

        assert (
            df.loc["Investigation Identifier"].iloc[0]
            == "test-investigation-1"
        )
        assert df.loc["Investigation Title"].iloc[0] == "Test Investigation 1"
