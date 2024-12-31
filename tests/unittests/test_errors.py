"""
Tests for the devices_rap/errors.py module.
"""

import re
from unittest import mock
import warnings
import pytest
from loguru import logger

from devices_rap.errors import (
    LoggedException,
    LoggedWarning,
    NoFilePathProvidedError,
    NoDatasetsProvidedError,
    NoDataProvidedError,
    ColumnsNotFoundError,
    MergeWarning,
)


class TestCustomExceptions:
    """
    Tests for the custom exception classes including:
    - LoggedException
    - NoFilePathProvidedError
    - NoDatasetsProvidedError
    - NoDataProvidedError
    - ColumnsNotFoundError
    """

    @pytest.mark.parametrize(
        "exception_class, message",
        [
            (LoggedException, "Test error message"),
            (NoFilePathProvidedError, "No file path provided"),
            (NoDatasetsProvidedError, "No datasets provided"),
            (NoDataProvidedError, "No data provided"),
        ],
    )
    def test_error(self, mocker, exception_class, message):
        """
        Test that the LoggedException logs the error message.
        """
        mock_logger = mocker.spy(logger, "error")
        with pytest.raises(exception_class, match=message):
            raise exception_class(message)
        mock_logger.assert_called_with(message)

    @pytest.mark.parametrize(
        "left_columns, right_columns, left_on, right_on, expected_message",
        [
            (
                ["col1", "col2"],
                ["col1", "col3"],
                ["col1"],
                ["col4"],
                "The column(s) ['col4'] were not found in the right dataset.",
            ),
            (
                ["col1", "col2"],
                ["col1", "col3"],
                ["col1"],
                ["col4", "col5"],
                "The column(s) ['col4', 'col5'] were not found in the right dataset.",
            ),
            (
                ["col1", "col2"],
                ["col1", "col3"],
                ["col1"],
                "col4",
                "The column(s) ['col4'] were not found in the right dataset.",
            ),
            (
                ["col1", "col2"],
                ["col1", "col3"],
                ["col4"],
                ["col1"],
                "The column(s) ['col4'] were not found in the left dataset.",
            ),
            (
                ["col1", "col2"],
                ["col1", "col3"],
                "col4",
                ["col1"],
                "The column(s) ['col4'] were not found in the left dataset.",
            ),
            (
                ["col1", "col2"],
                ["col1", "col3"],
                ["col4"],
                ["col4"],
                "The column(s) ['col4'] were not found in the left dataset. The column(s) ['col4'] were not found in the right dataset.",
            ),
        ],
    )
    def test_columns_not_found_error(self, mocker, left_columns, right_columns, left_on, right_on, expected_message):
        """
        Test that the ColumnsNotFoundError raises the correct message. Cases include:
        - One column in a list not found in the right columns
        - Two columns in a list not found in  the right columns
        - One column as a string not found in the right columns
        - One column in a list not found in the left columns
        - One column as a string not found in the left columns
        - One column in a list not found in the left columns and one column in a list not found in the right columns
        """
        mock_logger = mocker.patch.object(logger, "error")
        with pytest.raises(ColumnsNotFoundError, match=re.escape(expected_message)):
            raise ColumnsNotFoundError(left_columns, right_columns, left_on, right_on)
        mock_logger.assert_called_with(expected_message)


class TestCustomWarnings:
    """
    Tests for the custom warning classes including:
    - LoggedWarning
    - MergeWarning
    """

    @pytest.mark.parametrize(
        "warning_class, message",
        [
            (LoggedWarning, "Test warning message"),
            (MergeWarning, "Merge warning message"),
        ],
    )
    def test_warning(self, mocker, warning_class, message):
        """
        Test that the LoggedWarning logs the warning message.
        """
        mock_logger = mocker.spy(logger, "warning")
        with pytest.warns(warning_class, match=message):
            warnings.warn(message, warning_class)
        mock_logger.assert_called_with(message)


if __name__ == "__main__":
    pytest.main([__file__])
