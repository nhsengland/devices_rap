"""
Module for loading data from either CSV files or SQL queries based on dataset configuration.

This module provides a flexible data loading function that can handle both CSV files
and SQL queries based on the configuration keys present in the dataset configuration.
"""

from typing import Any, Dict

import tqdm
from loguru import logger
from nhs_herbot.errors import NoDatasetsProvidedError
from nhs_herbot.load_csv import load_csv_data

from devices_rap.config import Config
from devices_rap.data_io.utils import NA_VALUES


def load_devices_datasets(pipeline_config: Config) -> Dict[str, Dict[str, Any]]:
    """
    Load device datasets from either CSV files or SQL queries based on configuration.

    This function dynamically determines the loading method based on the configuration
    keys present in each dataset configuration:
    - "filepath_or_buffer": Loads from CSV file
    - "sql_query_path": Loads from SQL query

    Parameters
    ----------
    pipeline_config : Config
        The configuration object containing dataset information and SQL server connection.

    Returns
    -------
    dict of dict
        Dictionary containing dataset names as keys and dictionaries with "data" key
        containing the loaded DataFrame.

    Raises
    ------
    NoDatasetsProvidedError
        If the `datasets` dictionary is empty.
    ValueError
        If SQL query path is provided but no SQL server connection exists.
    FileNotFoundError
        If a SQL query file cannot be found or read.
    """
    datasets = pipeline_config.dataset_config
    if not datasets:
        raise NoDatasetsProvidedError("No datasets provided in the configuration.")

    for dataset_name, dataset_kwargs in tqdm.tqdm(datasets.items(), desc="Loading datasets"):
        # Remove any existing data key
        if "data" in dataset_kwargs:
            dataset_kwargs.pop("data")

        # Determine loading method based on configuration keys
        if "sql_query_path" in dataset_kwargs:
            # Load from SQL query
            logger.info(f"Loading {dataset_name} from SQL query")

            sql_server = pipeline_config.sql_server

            dataset_df = sql_server.load_from_sql_query(  # type: ignore
                file_path=dataset_kwargs["sql_query_path"],
                replacements=dataset_kwargs.get("replacements", {}),
            )
        elif "filepath_or_buffer" in dataset_kwargs:
            # Load from CSV file
            logger.info(f"Loading {dataset_name} from CSV file")
            dataset_df = load_csv_data(dataset_name, na_values=NA_VALUES, **dataset_kwargs)
        else:
            raise ValueError(
                f"Dataset {dataset_name} configuration must contain either "
                "'filepath_or_buffer' or 'sql_query_path' key"
            )

        datasets[dataset_name]["data"] = dataset_df

    return datasets
