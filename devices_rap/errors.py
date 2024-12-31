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


class ColumnsNotFoundError(LoggedException):
    """
    Exception raised when the columns are not found in the dataset. Works out which columns are
    missing and builds a message to display.

    Parameters
    ----------
    left_columns : list
        The columns in the left dataset.
    right_columns : list
        The columns in the right dataset.
    left_on : list
        The columns to merge on in the left dataset.
    right_on : list
        The columns to merge on in the right dataset.

    Raises
    ------
    ColumnsNotFoundError
        If the columns are not found in the dataset
    """

    def __init__(self, left_columns, right_columns, left_on, right_on):
        if isinstance(left_on, str):
            left_on = [left_on]
        if isinstance(right_on, str):
            right_on = [right_on]
        self.bad_left = sorted(list(set(left_on) - set(left_columns)))
        self.bad_right = sorted(list(set(right_on) - set(right_columns)))
        parts = []
        if self.bad_left:
            parts.append(f"The column(s) {self.bad_left} were not found in the left dataset.")
        if self.bad_right:
            parts.append(f"The column(s) {self.bad_right} were not found in the right dataset.")
        self.message = " ".join(parts)
        super().__init__(self.message)


class LoggedWarning(Warning):
    """
    Custom exception class that logs the warning message using the logger.
    """

    def __init__(self, message):
        self.message = message
        logger.warning(self.message)
        super().__init__(self.message)


class MergeWarning(LoggedWarning):
    """Custom warning for merge validation"""
