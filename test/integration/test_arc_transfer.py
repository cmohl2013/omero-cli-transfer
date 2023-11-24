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

    def test_mito_data(self, tmp_path):
        path_to_arc = tmp_path / "mito_arc"
        args = [
            "/home/christoph/miniconda3/envs/omcli/bin/omero",
            "--server",
            "localhost",
            "--user",
            "root",
            "--password",
            "omero",
            "transfer",
            "pack",
            "--arc",
            "Project:807",
            str(path_to_arc),
        ]

        self.cli.invoke(args[1:])

    def test_annotation(self):
        print(self.login_args())

        dataset_1 = self.make_dataset(name="dataset_1")
        self.create_mapped_annotation(
            name="dataset_annotations",
            map_values={"dataset_key1": 10, "dataset_key2": 20},
            namespace="isa_specifiaction",
            parent_object=dataset_1,
        )

        dataset_2 = self.make_dataset(name="dataset_2")
        self.create_mapped_annotation(
            name="dataset_annotations",
            map_values={"dataset_key1": 100, "dataset_key2": 200},
            namespace="isa_specifiaction",
            parent_object=dataset_2,
        )

        project = self.make_project(name="project_1")
        self.create_mapped_annotation(
            name="project_annotations",
            map_values={"project_key1": 100, "project_key2": 200},
            namespace="isa_specifiaction",
            parent_object=project,
        )

        self.link(project, dataset_1)
        self.link(project, dataset_2)

        pass
