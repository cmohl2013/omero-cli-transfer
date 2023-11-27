# How to run integration tests

## Run complete build and tests

Tests are run inside docker container

```
sudo .omero/docker cli
```

## Run tests on local machine

1. Start test database in docker container 
  ```
  sudo .omero/compose up
  ```
  Test database web interface can be accessed at `localhost:4080`.

2. Run tests
  ```
  OMERODIR="." ICE_CONFIG=test/integration/ice.config pytest -v
  ```
  Environment variables OMERODIR and ICE_CONFIG have to be set to define the connection to the test database. 
  
  When running tests with VSCode Testing (e.g. for interactive debugging), environment variables have to be set in .env file.