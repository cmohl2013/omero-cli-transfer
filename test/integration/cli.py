# Copyright (C) 2022 The Jackson Laboratory
# All rights reserved.
#
# Use is subject to license terms supplied in LICENSE.

from builtins import object
import pytest

import omero
from omero.cli import CLI
from omero.plugins.sessions import SessionsControl
from omero.rtypes import rstring

from omero.testlib import ITest
from mox3 import mox
from omero_cli_transfer import TransferControl
from omero.model import MapAnnotationI, NamedValue
from omero.gateway import BlitzGateway
from pathlib import Path
import os
import tarfile
import shutil


class AbstractCLITest(ITest):
    @classmethod
    def setup_class(cls):
        super(AbstractCLITest, cls).setup_class()
        cls.cli = CLI()
        cls.cli.register("sessions", SessionsControl, "TEST")

    def setup_mock(self):
        self.mox = mox.Mox()

    def teardown_mock(self):
        self.mox.UnsetStubs()
        self.mox.VerifyAll()


class CLITest(AbstractCLITest):
    def setup_method(self, method):
        self.args = self.login_args()

    def create_object(self, object_type, name=""):
        # create object
        if object_type == "Dataset":
            new_object = omero.model.DatasetI()
        elif object_type == "Project":
            new_object = omero.model.ProjectI()
        elif object_type == "Plate":
            new_object = omero.model.PlateI()
        elif object_type == "Screen":
            new_object = omero.model.ScreenI()
        elif object_type == "Image":
            new_object = self.new_image()
        new_object.name = rstring(name)
        new_object = self.update.saveAndReturnObject(new_object)

        # check object has been created
        found_object = self.query.get(object_type, new_object.id.val)
        assert found_object.id.val == new_object.id.val

        return new_object.id.val

    @pytest.fixture()
    def simple_hierarchy(self):
        proj = self.make_project()
        dset = self.make_dataset()
        img = self.update.saveAndReturnObject(self.new_image())
        self.link(proj, dset)
        self.link(dset, img)
        return proj, dset, img


class AbstractArcTest(AbstractCLITest):
    def setup_method(self, method):
        self.args = self.login_args()
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

    @pytest.fixture(scope="function")
    def dataset_1(self):
        dataset_1 = self.make_dataset(name="My First Assay")

        for i in range(3):
            img_name = f"assay 2 image {i}"
            image = self.create_test_image(
                80, 40, 3, 4, 2, self.client.getSession(), name=img_name
            )
            self.link(dataset_1, image)

        return dataset_1

    @pytest.fixture(scope="function")
    def dataset_2(self):
        dataset_2 = self.make_dataset(name="My Second Assay")

        for i in range(3):
            img_name = f"assay 2 image {i}"
            image = self.create_test_image(
                100, 100, 1, 1, 1, self.client.getSession(), name=img_name
            )
            self.link(dataset_2, image)

        return dataset_2

    @pytest.fixture(scope="function")
    def project_1(self, dataset_1, dataset_2):
        project_1 = self.make_project(name="My First Study")

        self.link(project_1, dataset_1)
        self.link(project_1, dataset_2)

        return project_1

    @pytest.fixture(scope="function")
    def dataset_czi_1(self):
        dataset = self.make_dataset(name="My Assay with CZI Images")

        def _add_local_image_file(path_to_img_file):
            assert path_to_img_file.exists()

            id = self.import_image(path_to_img_file)[0]

            container_service = self.client.getSession().getContainerService()
            image = container_service.getImages("Image", [int(id)], None)[0]
            self.link(dataset, image)

        path_to_img_file = (
            Path(__file__).parent.parent
            / "data/arc_test_data/img_files/CD_s_1_t_3_c_2_z_5.czi"
        )
        _add_local_image_file(path_to_img_file=path_to_img_file)

        image_tif = self.create_test_image(
            100,
            100,
            1,
            1,
            1,
            self.client.getSession(),
            name="another pixel image",
        )
        self.link(dataset, image_tif)

        path_to_img_file = (
            Path(__file__).parent.parent
            / "data/arc_test_data/img_files/sted-confocal.lif"
        )
        _add_local_image_file(path_to_img_file=path_to_img_file)

        return dataset

    @pytest.fixture(scope="function")
    def project_czi(self, dataset_czi_1, dataset_1):
        project_czi = self.make_project(name="My Study with a CZI Image")

        self.link(project_czi, dataset_czi_1)
        self.link(project_czi, dataset_1)

        return project_czi

    @pytest.fixture(scope="function")
    def path_arc_test_data(self, project_1, project_czi, request):
        path_to_arc_test_data = (
            Path(__file__).parent.parent / "data/arc_test_data/packed_projects"
        )
        os.makedirs(path_to_arc_test_data, exist_ok=True)

        if request.config.option.skip_create_arc_test_data:
            # if pytest is used with option --not-create-arc-test-data
            return path_to_arc_test_data

        shutil.rmtree(path_to_arc_test_data)
        os.makedirs(path_to_arc_test_data, exist_ok=True)

        for project, project_name in [
            (project_1, "project_1"),
            (project_czi, "project_czi"),
        ]:
            project_identifier = f"Project:{project.id._val}"
            path_to_arc_test_dataset = path_to_arc_test_data / project_name
            args = self.args + [
                "pack",
                project_identifier,
                str(path_to_arc_test_dataset),
            ]
            self.cli.invoke(args)

            with tarfile.open(
                path_to_arc_test_dataset.with_suffix(".tar")
            ) as f:
                f.extractall(path_to_arc_test_dataset)
            os.remove(path_to_arc_test_dataset.with_suffix(".tar"))

        return path_to_arc_test_data

    @pytest.fixture(scope="function")
    def path_omero_data_1(self, path_arc_test_data):
        return path_arc_test_data / "project_1"

    @pytest.fixture(scope="function")
    def path_omero_data_czi(self, path_arc_test_data):
        return path_arc_test_data / "project_czi"


class RootCLITest(AbstractCLITest):
    def setup_method(self, method):
        self.args = self.root_login_args()


class ArgumentFixture(object):

    """
    Used to test the user/group argument
    """

    def __init__(self, prefix, attr):
        self.prefix = prefix
        self.attr = attr

    def get_arguments(self, obj):
        args = []
        if self.prefix:
            args += [self.prefix]
        if self.attr:
            args += ["%s" % getattr(obj, self.attr).val]
        return args

    def __repr__(self):
        if self.prefix:
            return "%s" % self.prefix
        else:
            return "%s" % self.attr


UserIdNameFixtures = (
    ArgumentFixture("--id", "id"),
    ArgumentFixture("--name", "omeName"),
)

UserFixtures = (
    ArgumentFixture(None, "id"),
    ArgumentFixture(None, "omeName"),
    ArgumentFixture("--user-id", "id"),
    ArgumentFixture("--user-name", "omeName"),
)

GroupIdNameFixtures = (
    ArgumentFixture("--id", "id"),
    ArgumentFixture("--name", "name"),
)

GroupFixtures = (
    ArgumentFixture(None, "id"),
    ArgumentFixture(None, "name"),
    ArgumentFixture("--group-id", "id"),
    ArgumentFixture("--group-name", "name"),
)


def get_user_ids(out, sort_key=None):
    columns = {"login": 1, "first-name": 2, "last-name": 3, "email": 4}
    lines = out.split("\n")
    ids = []
    last_value = None
    for line in lines[2:]:
        elements = line.split("|")
        if len(elements) < 8:
            continue

        ids.append(int(elements[0].strip()))
        if sort_key:
            if sort_key == "id":
                new_value = ids[-1]
            else:
                new_value = elements[columns[sort_key]].strip()
            assert new_value >= last_value
            last_value = new_value
    return ids


def get_group_ids(out, sort_key=None):
    lines = out.split("\n")
    ids = []
    last_value = None
    for line in lines[2:]:
        elements = line.split("|")
        if len(elements) < 4:
            continue

        ids.append(int(elements[0].strip()))
        if sort_key:
            if sort_key == "id":
                new_value = ids[-1]
            else:
                new_value = elements[1].strip()
            assert new_value >= last_value
            last_value = new_value
    return ids
