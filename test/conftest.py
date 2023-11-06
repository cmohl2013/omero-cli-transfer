import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--create-arc-test-data", action="store_true", default=False
    )
