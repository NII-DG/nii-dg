# Tests for NII-DG Library

This directory contains tests for the NII-DG library.

## Types of Tests

The `tests` directory contains the following types of tests:

```
tests
├── example
├── functional_test
├── lint_and_style_check
├── load_test.sh
├── test_with_sapporo.sh
└── unit_test
```

### `example`

This directory contains scripts, sample data, and documents that illustrate how to use the library. Users can use these examples for quick starts. Please also refer to [../api-quick-start.md](../api-quick-start.md) as a document for quick starts.

### `functional_test`

This directory contains comprehensive test files that use the scripts in the example directory and other scenarios, such as using an API server. These tests are executed with `pytest`.

To run the tests, please execute the following command:

```bash
$ pytest -s ./tests/functional_test
```

### `unit_test`

This directory contains unit tests for the library. These tests are executed with `pytest`.

To run the tests, please execute the following command:

```bash
$ pytest -s ./tests/unit_test
```

### `lint_and_style_check`

This directory contains scripts to perform lint and style checks using `flake8`, `isort`, and `mypy`.

To run these checks, please execute the following command:

```bash
$ bash ./tests/lint_and_style_check/flake8.sh
$ bash ./tests/lint_and_style_check/isort.sh
$ bash ./tests/lint_and_style_check/mypy.sh

# or run all checks at once
$ bash ./tests/lint_and_style_check/run_all.sh
```

### `load_test.sh`

This is a script to perform load tests on the REST API Server. It uses Docker Compose to start the API server. It is designed to test various conditions such as when the API server is Flask, when it is waitless, or when waitless is launched with 3 threads.

To run the tests, please execute the following command:

```bash
$ bash ./tests/load_test.sh
```

### `test_with_sapporo.sh`

This is a script to perform tests in conjunction with Sapporo. It uses Docker Compose to both the NII-DG server and Sapporo's API server. For details about the Sapporo integration, please refer to [../sapporo_example/README.md](../sapporo_example/README.md).

To run the tests, please execute the following command:

```bash
$ bash ./tests/test_with_sapporo.sh
```

## Test Coverage

To evaluate the test coverage, please execute the following command:

```bash
$ coverage run --source=nii_dg -m pytest ./tests
$ coverage report
```

To view the coverage report in HTML, please execute the following command:

```bash
$ coverage html
$ open ./htmlcov/index.html
```

TO view the coverage report in HTML with a web server, please execute the following command:

```bash
$ python3 -m http.server --directory ./htmlcov 8080
```

## GitHub Actions

We have corresponding GitHub Actions for each test and lint check set up as Continuous Integration (CI) tools. Check out the [../.github/workflows](../.github/workflows) directory for details.

```
.github
└── workflows
    ├── flake8.yml
    ├── isort.yml
    ├── load_test.yml
    ├── mypy.yml
    ├── pytest.yml
    └── test_with_sapporo.yml
```

For each push and pull request, these workflows will be triggered to ensure the code quality and correctness of the library.

Please remember to run these tests locally before committing your changes.
