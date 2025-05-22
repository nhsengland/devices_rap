"""
Functions for cleaning and cleansing datasets
"""

import warnings
from typing import Any, Dict, List, Literal, Optional

import pandas as pd
import tqdm
from loguru import logger
from nhs_herbot.errors import (
    ColumnsNotFoundError,
    DuplicateDataError,
    DuplicateDataWarning,
    NoDataProvidedError,
    NoDatasetsProvidedError,
)
from nhs_herbot.utils import (
    convert_fin_dates_vectorised,
    convert_to_numeric_column,
    convert_values_to,
    normalise_column_names,
    parse_dates,
    sort_by_priority,
)

from devices_rap.config import RAG_PRIORITIES


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

        logger.info(
            "Converting total cost values to numeric, removing commas and converting to float"
        )
        master_df["cln_total_cost"] = convert_to_numeric_column(master_df["cln_total_cost"])
    except KeyError as e:
        raise ColumnsNotFoundError(
            dataset_columns=master_df.columns,
            clean_columns=["der_high_level_device_type", "cln_activity_year", "cln_total_cost"],
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

    columns_to_fill = [
        "rag_status",
        "upd_high_level_device_type",
        "cln_manufacturer",
        "cln_manufacturer_device_name",
        # "upd_region",
    ]

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
    exceptions_df: pd.DataFrame, rag_priorities: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Clean the exceptions dataset ready for processing.

    First, it will convert the handover date columns to datetime format. Then, it will remove
    duplicate exceptions by keeping the first occurrence of each provider and device code
    combination with the highest RAG status as defined the rag_priorities variable.

    The rag_priorities variable is a list of RAG status priorities, with the default being:
    - "AMBER"
    - "RED"
    - "YELLOW"

    If the dataset contains additional RAG statuses, they will be added to the end of the list in
    alphabetical order.

    Parameters
    ----------
    exceptions_df : pd.DataFrame
        The exceptions dataset to be cleaned. Must contain the following columns:
        - provider_code
        - dev_code
        - rag_status
    rag_priorities : List[str], optional
        The list of RAG status priorities, by default RAG_PRIORITIES

    Returns
    -------
    pd.DataFrame
        The cleaned exceptions dataset
    """
    rag_priorities = rag_priorities or RAG_PRIORITIES

    logger.info("Cleaning the exceptions dataset ready for processing")

    date_columns = [
        "handover_date_zcm",
        "handover_date_vcm",
    ]

    logger.info("Converting handover date columns to datetime")
    exceptions_df = convert_date_columns_to_datetime(
        data=exceptions_df,
        date_columns=date_columns,
    )

    logger.info("Resolving duplicates in the exceptions dataset.")
    exceptions_df = drop_duplicates_on_priority(
        data=exceptions_df,
        subset=["provider_code", "dev_code"],
        priority_column="rag_status",
        priority_order=rag_priorities,
    )

    return exceptions_df


def convert_date_columns_to_datetime(data: pd.DataFrame, date_columns: List[str]) -> pd.DataFrame:
    """
    Convert specified date columns in the dataframe to datetime format using the parse_dates
    function. This function will raise an error if any of the specified date columns are not present
    in the dataframe. The function will log the conversion process for each date column.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe containing the date columns to be converted.
    date_columns : List[str]
        A list of column names to be converted to datetime.

    Returns
    -------
    pd.DataFrame
        The dataframe with specified date columns converted to datetime.

    Raises
    ------
    ColumnsNotFoundError
        If any of the specified date columns are not present in the dataframe.
    """
    for date_col in tqdm.tqdm(date_columns):
        try:
            logger.info(f"Converting {date_col} values to datetime")
            data[date_col] = data[date_col].apply(parse_dates)
        except KeyError as e:
            raise ColumnsNotFoundError(
                dataset_columns=data.columns,
                date_column=date_columns,
            ) from e
    return data


def drop_duplicates_on_priority(
    data: pd.DataFrame, subset: str | List[str], priority_column: str, priority_order: List[str]
) -> pd.DataFrame:
    """
    This function will remove duplicate rows from the dataset by keeping the first occurrence of
    each unique value in the subset column(s) with the highest priority value in the
    priority_columns as defined in the priority_order variable.

    If the dataset contains additional values in the priority_column not already specified in the
    priority_order variable, they will be added to the end of the list in alphabetical order.

    Parameters
    ----------
    data : pd.DataFrame
        The dataset with duplicates to be removed. Must contain the columns specified in the
        subset and priority_column variables.
    subset : str | List[str]
        The column(s) to use to identify duplicates
    priority_column : str
        The column to use to determine the priority of the duplicates
    priority_order : List[str]
        The list of priority values to use when determining which duplicates to keep

    Returns
    -------
    pd.DataFrame
        The dataset with duplicates removed

    Raises
    ------
    ColumnsNotFoundError
        If the required columns are not present in the dataset
    """
    if isinstance(subset, str):
        subset = [subset]

    check_duplicates(data=data, duplicate_severity="INFO", subset=subset)

    if not {*subset, priority_column}.issubset(data.columns):
        raise ColumnsNotFoundError(
            dataset_columns=data.columns,
            drop_duplicate_columns=[*subset, priority_column],
        )

    unique_values = data[priority_column].astype(str).unique()

    additional_values = sorted(set(unique_values) - set(priority_order))
    complete_priorities = priority_order + additional_values

    data = (
        data.pipe(sort_by_priority, priority_column, complete_priorities)
        .drop_duplicates(subset=subset, keep="first")
        .reset_index(drop=True)
    )

    check_duplicates(data=data, duplicate_severity="ERROR", subset=subset)

    return data


def check_duplicates(
    data: pd.DataFrame,
    duplicate_severity: Literal["ERROR"] | Literal["WARNING"] | Literal["INFO"] = "INFO",
    subset: Optional[str | List[str]] = None,
) -> None:
    """
    Function checks for duplicates in the dataset and raises an error, warning or logs an info
    with information about the number of duplicates found. The level of the message can be
    controlled by the duplicate_severity variable.

    Parameters
    ----------
    data : pd.DataFrame
        The dataset to check for duplicates
    duplicate_severity : Literal["ERROR"] | Literal["WARNING"] | Literal["INFO"], optional
        The severity of the message to raise, by default "INFO"
    subset : str | List[str], optional
        The column(s) to use to identify duplicates, by default None

    Raises
    ------
    DuplicateDataError
        If the severity is set to "ERROR" and duplicates are found
    DuplicateDataWarning
        If the severity is set to "WARNING" and duplicates are found

    Side Effects
    ------------
    Logs a message with the number of duplicates found if severity is set to "INFO"
    """
    duplicate_data = data[data.duplicated(subset=subset, keep=False)]
    duplicate_amount = duplicate_data.shape[0]

    if duplicate_amount > 0:
        message = f"Found {duplicate_amount} duplicated rows in the dataset"
        message += f" with subset columns: {subset}" if subset else ""
        if duplicate_severity == "ERROR":
            raise DuplicateDataError(message=message)
        elif duplicate_severity == "WARNING":
            warnings.warn(message, DuplicateDataWarning)
        else:
            logger.info(message)
