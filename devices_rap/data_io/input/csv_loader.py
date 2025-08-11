"""
Module for loading CSV data into pandas DataFrames with custom error handling and logging.

This module provides functionality to load CSV data into pandas DataFrames, with support for
custom NA values and logging. It also includes custom exceptions for handling cases where
no file path or datasets are provided.
"""

from typing import Any, Dict

import tqdm
from nhs_herbot.errors import NoDatasetsProvidedError
from nhs_herbot.load_csv import load_csv_data

from devices_rap.config import Config
from devices_rap.data_io.utils import NA_VALUES


def load_devices_datasets(pipeline_config: Config) -> Dict[str, Dict[str, Any]]:
    """
    Load device datasets from CSV files.

    Parameters
    ----------
    pipeline_config : Config
        The configuration object containing dataset information.

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
    datasets = pipeline_config.dataset_config
    if not datasets:
        raise NoDatasetsProvidedError("No datasets provided in the configuration.")

    for dataset_name, dataset_kwargs in tqdm.tqdm(datasets.items(), desc="Loading datasets"):
        if "data" in dataset_kwargs:
            dataset_kwargs.pop("data")
        dataset_df = load_csv_data(dataset_name, na_values=NA_VALUES, **dataset_kwargs)
        datasets[dataset_name]["data"] = dataset_df

    return datasets
