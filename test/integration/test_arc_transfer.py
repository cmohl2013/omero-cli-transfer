from cli import CLITest
from test_transfer import TestTransfer
from omero_cli_transfer import TransferControl
from omero.gateway import BlitzGateway
from omero.model import MapAnnotationI, NamedValue
from omero.rtypes import rstring


class TestArcTransfer(TestTransfer):
    def setup_method(self, method):
        super(TestArcTransfer, self).setup_method(method)
        self.cli.register("transfer", TransferControl, "TEST")
        self.args += ["transfer"]
        self.gw = BlitzGateway(client_obj=self.client)
        self.session = self.client.getSessionId()

    def create_mapped_annotation(
        self, name=None, map_values=None, namespace=None, parent_object=None
    ):
        map_annotation = self.new_object(MapAnnotationI, name=name)
        if map_values is not None:
            map_value_ls = [
                NamedValue(str(key), str(map_values[key])) for key in map_values
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

    def test_pack_arc(self, tmp_path):
        project_1 = self.make_project(name="study_1")
        dataset_1 = self.make_dataset(name="assay_1")
        dataset_2 = self.make_dataset(name="assay_2")

        self.link(project_1, dataset_1)
        self.link(project_1, dataset_2)

        for _ in range(3):
            image = self.create_test_image(100, 100, 1, 1, 1, self.client.getSession())
            self.link(dataset_1, image)

        for _ in range(2):
            image = self.create_test_image(150, 150, 3, 1, 1, self.client.getSession())
            self.link(dataset_2, image)

        project_identifier = f"Project:{project_1.id._val}"
        path_to_arc = tmp_path / "my_arc.tar"
        args = self.args[:8] + ["pack", "--arc", project_identifier, str(path_to_arc)]
        self.cli.invoke(args)

        assert path_to_arc.exists()
        assert (path_to_arc / "assays").exists()
        assert (path_to_arc / "studies").exists()

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
