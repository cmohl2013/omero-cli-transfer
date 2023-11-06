import pytest
from pathlib import Path
from omero_cli_transfer import ArcPacker


@pytest.fixture()
def path_omero_data_1():
    return Path(__file__).parent.parent / "data/arc_test_data/project_1"


def test_arc_packer_read_omedata(path_omero_data_1, tmp_path):
    ap = ArcPacker(tmp_path / "my_arc")

    ap.add_omero_data(path_omero_data_1)

    assert ap.ome is not None
    print(tmp_path)
