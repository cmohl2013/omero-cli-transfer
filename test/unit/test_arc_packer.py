import pytest
from pathlib import Path
from omero_cli_transfer import ArcPacker
import pandas as pd


@pytest.fixture()
def path_omero_data_1():
    return Path(__file__).parent.parent / "data/arc_test_data/project_1"


def test_arc_packer_read_omedata(path_omero_data_1, tmp_path):
    ap = ArcPacker(tmp_path / "my_arc")

    ap.add_omero_data(path_omero_data_1)

    assert ap.ome is not None
    print(tmp_path)


def test_arc_packer_create_investigation(path_omero_data_1, tmp_path):
    path_to_arc_repo = tmp_path / "my_arc"
    ap = ArcPacker(path_to_arc_repo)
    ap.add_omero_data(path_omero_data_1)

    ap.create_investigation()
    df = pd.read_excel(
        path_to_arc_repo / "isa.investigation.xlsx",
        index_col=0,
    )

    assert df.loc["Investigation Identifier"].iloc[0] == "test-investigation-1"
    assert df.loc["Investigation Title"].iloc[0] == "Test Investigation 1"
