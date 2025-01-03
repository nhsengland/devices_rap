"""
This module contains fixtures that are used by the test modules in the tests/ directory.
"""

import warnings
import pandas as pd
import pytest
import loguru

from devices_rap.config import DATA_DIR
from devices_rap.data_in.load_csv import NA_VALUES

warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*platformdirs.*")

TEST_DATA_DIR = DATA_DIR / "_test"

@pytest.fixture
def create_temp_csv_file():
    """
    Fixture to create a temporary CSV file with test data, returning the file path, and then
    deleting the file and the _test directory after the test has run.
    """
    # Create the _test directory if it doesn't exist
    TEST_DATA_DIR.mkdir(parents=True, exist_ok=False)

    test_csv_data = {
        "columns": ["column_1", "column_2"],
        "data": [
            ("test_valid_1", "foo"),
            ("test_valid_2", "bar"),
            ("test_valid_3", "baz"),
            *[(f"test_{NA_VALUES.index(na_value)}", na_value) for na_value in NA_VALUES],
            (None, None),
            (None, None),
        ],
    }
    test_csv_df = pd.DataFrame(**test_csv_data)

    test_csv_file_path = TEST_DATA_DIR / "_test_data.csv"

    assert not test_csv_file_path.exists()

    test_csv_df.to_csv(test_csv_file_path, index=False)

    yield test_csv_file_path

    # Clean up the _test directory and its contents
    test_csv_file_path.unlink()
    TEST_DATA_DIR.rmdir()

    assert not test_csv_file_path.exists()
    assert not TEST_DATA_DIR.exists()


@pytest.fixture
def mock_info(mocker):
    """
    Fixture to mock the loguru.logger.info method
    """
    return mocker.spy(loguru.logger, "info")


@pytest.fixture
def mock_error(mocker):
    """
    Fixture to mock the loguru.logger.error method
    """
    return mocker.spy(loguru.logger, "error")


@pytest.fixture
def mock_warning(mocker):
    """
    Fixture to mock the loguru.logger.warning method
    """
    return mocker.spy(loguru.logger, "warning")


@pytest.fixture
def mock_success(mocker):
    """
    Fixture to mock the loguru.logger.success method
    """
    return mocker.spy(loguru.logger, "success")


@pytest.fixture
def mock_log_levels(mock_info, mock_error, mock_warning, mock_success):
    """
    Fixture to mock the loguru.logger methods:
    - info
    - error
    - warning
    - success
    """
    return mock_info, mock_error, mock_warning, mock_success


@pytest.fixture
def empty_df():
    """
    Fixture to return an empty DataFrame
    """
    return pd.DataFrame()

