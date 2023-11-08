def pytest_addoption(parser):
    parser.addoption(
        "--skip-create-arc-test-data", action="store_true", default=False
    )
