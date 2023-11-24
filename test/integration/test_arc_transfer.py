from abstract_arc_test import AbstractArcTest
import pytest


class TestArcTransfer(AbstractArcTest):
    def test_pack_arc_fails_for_dataset(self, dataset_1, tmp_path):
        # only projects can be packed as arc
        dataset_identifier = f"Dataset:{dataset_1.id._val}"
        path_to_arc = tmp_path / "my_arc"
        args = self.args + [
            "pack",
            "--arc",
            dataset_identifier,
            str(path_to_arc),
        ]

        with pytest.raises(ValueError):
            self.cli.invoke(args)

    def test_pack_arc(self, project_1, tmp_path):
        project_identifier = f"Project:{project_1.getId()}"
        path_to_arc = tmp_path / "my_arc"
        args = self.args + [
            "pack",
            "--arc",
            project_identifier,
            str(path_to_arc),
        ]
        self.cli.invoke(args)

        assert path_to_arc.exists()
        assert (path_to_arc / "assays").exists()
        assert (path_to_arc / "studies").exists()
