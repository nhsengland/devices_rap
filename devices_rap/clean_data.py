"""
Functions for cleaning and cleansing datasets
"""

import warnings
from typing import Any, Dict, List

import pandas as pd
import tqdm
from loguru import logger

from devices_rap.config import RAG_PRIORITIES
from devices_rap.errors import (
    ColumnsNotFoundError,
    DuplicateExceptionsWarning,
    NoDataProvidedError,
    NoDatasetsProvidedError,
)
from devices_rap.utils import (
    convert_fin_dates_vectorised,
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
    - Convert high level device type values
    - Convert activity year values without century
    - Convert activity date values to datetime

    Parameters
    ----------
    master_df : pd.DataFrame
        The master dataset to be cleaned. Must contain the following columns:
        - der_high_level_device_type
        - cln_activity_year

    Returns
    -------
    pd.DataFrame
        The cleaned master dataset

    Raises
    ------
    ColumnsNotFoundError
        If the required columns are not present in the dataset
    """
    logger.info("Cleaning the master dataset ready for processing")

    tqdm.tqdm.pandas()

    try:
        logger.info("Converting high level device type values")
        master_df["upd_high_level_device_type"] = master_df[
            "der_high_level_device_type"
        ].progress_apply(convert_values_to)

        logger.info("Converting activity year values without century")
        master_df["upd_activity_year"] = master_df["cln_activity_year"].progress_apply(
            convert_values_to, match=[2425], to=202425
        )

        logger.info("Converting activity date values to datetime")
        master_df["activity_date"] = convert_fin_dates_vectorised(master_df)
    except KeyError as e:
        raise ColumnsNotFoundError(
            dataset_columns=master_df.columns,
            clean_columns=["der_high_level_device_type", "cln_activity_year"],
        ) from e

    return master_df


def cleanse_master_joined_dataset(master_joined_df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the joined dataset ready for pivoting. This function will:
    - Consolidate region columns into a single column, 'upd_region'
    - Fix inconsistent 'upd_region' values by replacing '&' with 'and'
    - Fill missing 'rag_status' values with 'RED' where 'upd_high_level_device_type' is missing
    - Fill missing values with 'NULL' in the columns:
        - rag_status
        - upd_high_level_device
        - cln_manufacturer
        - cln_manufacturer_device_name

    Parameters
    ----------
    master_df : pd.DataFrame
        The joined dataset to be cleaned. Must contain the following columns:
        - region
        - nhs_england_region
        - rag_status
        - upd_high_level_device_type
        - cln_manufacturer
        - cln_manufacturer_device_name

    Returns
    -------
    pd.DataFrame
        The cleaned joined dataset

    Raises
    ------
    ColumnsNotFoundError
        If the required columns are not present in the dataset
    """

    logger.info("Cleaning the joined dataset ready for pivoting")

    try:
        logger.info(
            "Consolidating region columns into a single column, preferring 'region' over 'nhs_england_region'"
        )
        master_joined_df["upd_region"] = master_joined_df["region"].combine_first(
            master_joined_df["nhs_england_region"]
        )
        master_joined_df = master_joined_df.drop(columns=["region", "nhs_england_region"])

        logger.info("Fixing inconsistent 'upd_region' values")
        master_joined_df["upd_region"] = master_joined_df["upd_region"].str.replace("&", "and")

        logger.info(
            "Filling missing 'rag_status' values with 'RED' where 'upd_high_level_device_type' is missing"
        )
        master_joined_df.loc[
            master_joined_df["upd_high_level_device_type"].isna()
            & master_joined_df["rag_status"].isna(),
            "rag_status",
        ] = "RED"

        columns_to_fill = [
            "rag_status",
            "upd_high_level_device_type",
            "cln_manufacturer",
            "cln_manufacturer_device_name",
        ]
        logger.info(f"Filling missing values with 'NULL' in the columns: {columns_to_fill}")
        master_joined_df[columns_to_fill] = master_joined_df[columns_to_fill].fillna("NULL")

    except KeyError as e:
        raise ColumnsNotFoundError(
            dataset_columns=master_joined_df.columns,
            clean_columns=[
                "region",
                "nhs_england_region",
                *columns_to_fill,
            ],
        ) from e

    return master_joined_df


def cleanse_exceptions(
    exceptions_df: pd.DataFrame, rag_priorities: List[str] = RAG_PRIORITIES
) -> pd.DataFrame:
    """
    Clean the exceptions dataset ready for processing. This function will:
    - Deduplicate merged providers with conflicting rag_status values

    Parameters
    ----------
    exceptions_df : pd.DataFrame
        The exceptions dataset to be cleaned.

    Returns
    -------
    pd.DataFrame
        The cleaned exceptions dataset

    Raises
    ------
    ColumnsNotFoundError
        If the required columns are not present in the dataset
    """

    logger.info("Cleaning the exceptions dataset ready for processing")

    pre_duplicated_exceptions = exceptions_df[
        exceptions_df.duplicated(subset=["provider_code", "dev_code"], keep=False)
    ]
    logger.debug(
        f"Found {pre_duplicated_exceptions.shape[0]} duplicated exceptions before cleaning"
    )

    unique_rag_statuses = exceptions_df["rag_status"].astype(str).unique()

    additional_rag_statuses = sorted(set(unique_rag_statuses) - set(rag_priorities))
    RAG_PRIORITIES = rag_priorities + additional_rag_statuses

    if not {"provider_code", "dev_code", "rag_status"}.issubset(exceptions_df.columns):
        raise ColumnsNotFoundError(
            dataset_columns=exceptions_df.columns,
            clean_columns=["provider_code", "dev_code", "rag_status"],
        )

    exceptions_df["rag_status"] = pd.Categorical(
        exceptions_df["rag_status"], categories=RAG_PRIORITIES, ordered=True
    )

    exceptions_df = exceptions_df.sort_values("rag_status").drop_duplicates(
        subset=["provider_code", "dev_code"], keep="first"
    )

    exceptions_df["rag_status"] = exceptions_df["rag_status"].astype(str)

    post_duplicated_exceptions = exceptions_df[
        exceptions_df.duplicated(subset=["provider_code", "dev_code"], keep=False)
    ]

    if not post_duplicated_exceptions.empty:
        warnings.warn(
            f"Found {post_duplicated_exceptions.shape[0]} duplicated exceptions after cleaning",
            DuplicateExceptionsWarning,
        )

    return exceptions_df
