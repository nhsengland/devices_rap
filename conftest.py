"""
This module contains fixtures that are used by the test modules in the tests/ directory.
"""

from typing import Any, Dict, Literal
import warnings
import pandas as pd
import pytest
from uuid import uuid4

from devices_rap.config import DATA_DIR
from devices_rap.data_in.load_csv import NA_VALUES

warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*platformdirs.*")

TEST_DATA_DIR = DATA_DIR / "_test"

Logger = Any

MockLoggerDict = Dict[
    Literal["info"]
    | Literal["error"]
    | Literal["warning"]
    | Literal["success"]
    | Literal["debug"],
    Logger,
]


@pytest.fixture
def create_temp_csv_file(tmp_path):
    """
    Fixture to create a temporary CSV file with test data, returning the file path, and then
    deleting the file and the _test directory after the test has run.
    """

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

    test_csv_file_path = tmp_path / f"_{uuid4()}_test_data.csv"

    assert not test_csv_file_path.exists()

    test_csv_df.to_csv(test_csv_file_path, index=False)

    return test_csv_file_path


@pytest.fixture
def mock_info(mocker):
    """
    Fixture to mock the loguru.logger.info method
    """
    return mocker.patch("loguru.logger.info")


@pytest.fixture
def mock_error(mocker):
    """
    Fixture to mock the loguru.logger.error method
    """
    return mocker.patch("loguru.logger.error")


@pytest.fixture
def mock_warning(mocker):
    """
    Fixture to mock the loguru.logger.warning method
    """
    return mocker.patch("loguru.logger.warning")


@pytest.fixture
def mock_success(mocker):
    """
    Fixture to mock the loguru.logger.success method
    """
    return mocker.patch("loguru.logger.success")


@pytest.fixture
def mock_debug(mocker):
    """
    Fixture to mock the loguru.logger.debug method
    """
    return mocker.patch("loguru.logger.debug")


@pytest.fixture(autouse=True)
def mock_log_levels(
    mock_info, mock_error, mock_warning, mock_success, mock_debug
) -> MockLoggerDict:
    """
    Fixture to mock the loguru.logger methods:
    - info
    - error
    - warning
    - success
    - debug
    """
    return {
        "info": mock_info,
        "error": mock_error,
        "warning": mock_warning,
        "success": mock_success,
        "debug": mock_debug,
    }


@pytest.fixture
def empty_df():
    """
    Fixture to return an empty DataFrame
    """
    return pd.DataFrame()
