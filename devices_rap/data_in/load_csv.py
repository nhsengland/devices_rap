"""
Module for loading CSV data into pandas DataFrames with custom error handling and logging.

Functions
-------
load_devices_datasets(pipeline_config: Config) -> Dict[str, Dict[str, Any]]
    Loads device datasets from CSV files specified in the pipeline configuration.

Constants
-------
NA_VALUES : List[str]
    A list of strings that should be treated as NA values when loading CSV files.
"""

from typing import Any, Dict

import tqdm
from nhs_herbot.errors import NoDatasetsProvidedError
from nhs_herbot.load_csv import load_csv_data

from devices_rap.config import Config

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
    " -   ",
    " - ",
    " -",
    "-  ",
    "- ",
    " -  ",
]


def load_devices_datasets(pipeline_config: Config) -> Dict[str, Dict[str, Any]]:
    """
    Loads the device datasets from CSV files specified in the pipeline configuration.

    Expected the `pipeline_config` to contain a `dataset_config` dictionary with dataset names as
    keys and their respective loading parameters as values, for example:

    ```python
    pipeline_config.dataset_config = {
        "dataset_name": {
            "file_path": "path/to/csv_file.csv",
            # Additional parameters for loading the CSV file can be included here.
        },
        ...
    }
    ```

    The function will load each dataset into a pandas DataFrame and add it to the `datasets`
    dictionary under the key "data". If a dataset already contains a "data" key, it will be removed
    before loading the new DataFrame.

    Parameters
    ----------
    pipeline_config : Config
        The configuration object containing dataset information.

    Returns
    -------
    Dict[str, Dict[str, Any]]
        The input dictionary with an additional key "data" in each inner dictionary,
        containing the loaded DataFrame.

    Raises
    ------
    NoDatasetsProvidedError
        If the `datasets` dictionary is empty.
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
