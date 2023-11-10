from integration.cli import AbstractArcTest
import pytest
from omero_cli_transfer import OmeroProject
import pandas as pd

import os


class TestOmeroProject(AbstractArcTest):
    def test_omero_project_read_omedata(self, path_omero_data_1):
        p = OmeroProject(path_omero_data_1)
        assert p.ome is not None
