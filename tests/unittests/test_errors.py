"""
Tests for the devices_rap/errors.py module.
"""

import warnings
import pytest
from loguru import logger

from devices_rap.errors import (
    LoggedException,
    LoggedWarning,
    NoFilePathProvidedError,
    NoDatasetsProvidedError,
    NoDataProvidedError,
    MergeWarning,
)


class TestCustomExceptions:
    """
    Tests for the custom exception classes including:
    - LoggedException
    - NoFilePathProvidedError
    - NoDatasetsProvidedError
    - NoDataProvidedError
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
