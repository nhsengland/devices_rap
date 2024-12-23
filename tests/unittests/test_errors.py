"""
Tests for the devices_rap/errors.py module.
"""

import pytest
from loguru import logger

import devices_rap
from devices_rap.errors import (
    LoggedException,
    NoFilePathProvidedError,
    NoDatasetsProvidedError,
    NoDataProvidedError,
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


if __name__ == "__main__":
    pytest.main([__file__])
