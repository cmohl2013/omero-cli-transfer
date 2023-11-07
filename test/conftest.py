def pytest_addoption(parser):
    parser.addoption(
        "--not-create-arc-test-data", action="store_true", default=False
    )
