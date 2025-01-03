"""
Functions for cleaning and cleansing datasets
"""

from typing import Any, Dict

import pandas as pd
import tqdm
from loguru import logger

from devices_rap.errors import NoDataProvidedError, NoDatasetsProvidedError
from devices_rap.utils import (
    convert_fin_dates,
    convert_values_to,
    normalise_column_names,
)


def batch_normalise_column_names(datasets: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Normalise the column names for all datasets in the provided dictionary

    Parameters
    ----------
    datasets : Dict[str, Dict[str, Any]]
        A dictionary containing dataset names and their corresponding dataframes

    Returns
    -------
    Dict[str, Dict[str, Any]]
        The dictionary containing the normalised dataframes
    """
    if not datasets:
        raise NoDatasetsProvidedError("No datasets provided.")

    dataset_items = tqdm.tqdm(datasets.items(), desc="Normalising column names")

    for name, df in dataset_items:
        logger.info(f"Normalising column names for the {name} dataset")
        try:
            df = datasets[name]["data"]
            assert isinstance(df, pd.DataFrame)
            datasets[name]["data"] = normalise_column_names(df)
        except (KeyError, AssertionError) as e:
            raise NoDataProvidedError(f"No data provided for the {name} dataset.") from e

    return datasets


def cleanse_master_data(master_df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the master dataset ready for processing. This function will:
    - Normalise the column names
    - Convert high level device type values
    - Convert activity year values without century
    - Convert activity date values to datetime

    Parameters
    ----------
    master_df : pd.DataFrame
        The master dataset to be cleaned

    Returns
    -------
    pd.DataFrame
        The cleaned master dataset
    """
    logger.info("Cleaning the master dataset ready for processing")

    tqdm.tqdm.pandas()

    logger.info("Converting high level device type values")
    master_df["upd_high_level_device_type"] = master_df[
        "der_high_level_device_type"
    ].progress_apply(convert_values_to)

    logger.info("Converting activity year values without century")
    master_df["upd_activity_year"] = master_df["cln_activity_year"].progress_apply(
        convert_values_to, match=[2425], to=202425
    )

    logger.info("Converting activity date values to datetime")
    master_df["activity_date"] = master_df.progress_apply(
        lambda df: convert_fin_dates(df["cln_activity_month"], df["upd_activity_year"]), axis=1
    )

    return master_df
