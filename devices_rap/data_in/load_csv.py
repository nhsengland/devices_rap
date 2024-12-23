"""
Module for loading CSV data into pandas DataFrames with custom error handling and logging.

This module provides functionality to load CSV data into pandas DataFrames, with support for
custom NA values and logging. It also includes custom exceptions for handling cases where
no file path or datasets are provided.

Classes
NoFilePathProvidedError(Exception)
NoDatasetsProvidedError(Exception)

Functions
---------
load_csv_data(dataset_name: str, **read_csv_kwargs) -> pd.DataFrame
load_devices_datasets(datasets: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]

Constants
---------
NA_VALUES : list
    A list of strings representing custom NA values to be used when loading CSV data.
DATASETS : dict
    A dictionary containing dataset names and their corresponding file paths and read_csv arguments.

"""

from typing import Any, Dict

import pandas as pd
from loguru import logger

NA_VALUES = [
    "(blank)",
    "tbc",
    "-",
    "......................",
    "NA",
    "n/a",
    "Not Specified",
    "tbc ",
    "…...................",
    # "00:00.0",
    "(NOT KNOWN)",
    "unknown",
    "UNKNOWN",
    "na",
    "Not Known",
    "N/a",
    "NOT KNOWN",
    "<r>",
    "Not known",
    "***NOT LISTED/UNKNOWN/999999***",
]


class NoFilePathProvidedError(Exception):
    """
    Exception raised when no file path is provided to the `load_csv_data` function.
    """

    def __init__(self, message="No file path provided."):
        self.message = message
        logger.error(self.message)
        super().__init__(self.message)


class NoDatasetsProvidedError(Exception):
    """
    Exception raised when no datasets are provided to the `load_devices_datasets` function.
    """

    def __init__(self, message="No datasets provided."):
        self.message = message
        logger.error(self.message)
        super().__init__(self.message)


def load_csv_data(dataset_name: str, **read_csv_kwargs) -> pd.DataFrame:
    """
    Load CSV data into a pandas DataFrame.

    Parameters
    ----------
    dataset_name : str
        The name of the dataset being loaded.
    **read_csv_kwargs : dict
        Additional keyword arguments to pass to `pd.read_csv`. Must include `filepath_or_buffer`.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the loaded CSV data.

    Raises
    ------
    NoFilePathProvidedError
        If `filepath_or_buffer` is not provided in `read_csv_kwargs`.

    Notes
    -----
    This function logs the dataset name and file path before loading the data.
    """
    try:
        filepath_or_buffer = read_csv_kwargs["filepath_or_buffer"]
    except KeyError as e:
        raise NoFilePathProvidedError("No file path provided.") from e

    logger.info(f"Loading {dataset_name} data from: {filepath_or_buffer}")

    data_df = pd.read_csv(
        na_values=NA_VALUES,
        skip_blank_lines=True,
        **read_csv_kwargs,
    ).dropna(how="all")

    return data_df


def load_devices_datasets(datasets: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Load device datasets from CSV files.

    Parameters
    ----------
    datasets : dict of dict
        A dictionary where the key is the dataset name (str) and the value is another dictionary
        containing keyword arguments to be passed to the `load_csv_data` function.

    Returns
    -------
    dict of dict
        The input dictionary with an additional key "data" in each inner dictionary,
        containing the loaded DataFrame.

    Raises
    ------
    NoDatasetsProvidedError
        If the `datasets` dictionary is empty.

    Notes
    -----
    The `load_csv_data` function is expected to be defined elsewhere and should handle the
    actual loading of the CSV data based on the provided keyword arguments.
    """
    if not datasets:
        raise NoDatasetsProvidedError("No datasets provided.")

    for dataset_name, dataset_kwargs in datasets.items():
        dataset_df = load_csv_data(dataset_name, **dataset_kwargs)
        datasets[dataset_name]["data"] = dataset_df

    return datasets
