"""
Defines custom exceptions for the devices_rap package.
"""

from loguru import logger


class LoggedException(Exception):
    """
    Custom exception class that logs the error message using the logger.
    """

    def __init__(self, message):
        self.message = message
        logger.error(self.message)
        super().__init__(self.message)


class NoFilePathProvidedError(LoggedException):
    """
    Exception raised when no file path is provided to the `load_csv_data` function.
    """


class NoDatasetsProvidedError(LoggedException):
    """
    Exception raised when no datasets are provided to the `load_devices_datasets` function.
    """


class NoDataProvidedError(LoggedException):
    """
    Exception raised when no data is provided to the `batch_normalise_column_names` function.
    """
