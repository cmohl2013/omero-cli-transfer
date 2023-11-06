from cli import CLITest
from omero_cli_transfer import TransferControl
from omero.gateway import BlitzGateway
from omero.model import MapAnnotationI, NamedValue
from omero.rtypes import rstring
from pathlib import Path
import os
import pytest


class TestArcTransfer(CLITest):
    def setup_method(self, method):
        super(TestArcTransfer, self).setup_method(method)
        self.cli.register("transfer", TransferControl, "TEST")
        self.args += ["transfer"]

        self.session = self.client.getSessionId()

    def create_mapped_annotation(
        self, name=None, map_values=None, namespace=None, parent_object=None
    ):
        map_annotation = self.new_object(MapAnnotationI, name=name)
        if map_values is not None:
            map_value_ls = [
                NamedValue(str(key), str(map_values[key]))
                for key in map_values
            ]
            map_annotation.setMapValue(map_value_ls)
        if namespace is not None:
            map_annotation.setNs(rstring(namespace))

        map_annotation = self.client.sf.getUpdateService().saveAndReturnObject(
            map_annotation
        )
        if parent_object is not None:
            self.link(parent_object, map_annotation)

        return map_annotation

    @pytest.fixture()
    def dataset_1(self):
        dataset_1 = self.make_dataset(name="assay_1")

        for _ in range(3):
            image = self.create_test_image(
                100, 100, 1, 1, 1, self.client.getSession()
            )
            self.link(dataset_1, image)

        return dataset_1

    @pytest.fixture()
    def dataset_2(self):
        dataset_2 = self.make_dataset(name="assay_2")

        for _ in range(3):
            image = self.create_test_image(
                100, 100, 1, 1, 1, self.client.getSession()
            )
            self.link(dataset_2, image)

        return dataset_2

    @pytest.fixture()
    def project_1(self, dataset_1, dataset_2):
        project_1 = self.make_project(name="study_1")

        self.link(project_1, dataset_1)
        self.link(project_1, dataset_2)

        return project_1

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
        project_identifier = f"Project:{project_1.id._val}"
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

    def test_create_arc_test_data(self, project_1, request):
        path_to_arc_test_data = (
            Path(__file__).parent.parent / "data/arc_test_data"
        )
        os.makedirs(path_to_arc_test_data, exist_ok=True)

        if request.config.option.create_arc_test_data:
            project_identifier = f"Project:{project_1.id._val}"
            path_to_arc_test_dataset_1 = path_to_arc_test_data / "project_1"
            args = self.args + [
                "pack",
                project_identifier,
                str(path_to_arc_test_dataset_1),
            ]
            self.cli.invoke(args)
            import tarfile

            with tarfile.open(
                path_to_arc_test_dataset_1.with_suffix(".tar")
            ) as f:
                f.extractall(path_to_arc_test_dataset_1)
            os.remove(path_to_arc_test_dataset_1.with_suffix(".tar"))

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
