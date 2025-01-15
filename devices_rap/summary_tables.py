"""
This module contains functions to create pivot tables for summarizing device data.

Functions
---------
create_pivot_sum_table(data, values=None, columns=None, base_index=None, extended_index=None)
    Create a pivot table with the sum of the values for the given columns.

create_device_category_summary_table(master_devices_data)
    Creates the device category summary table by pivoting the master devices data.

create_device_summary_table(master_devices_data)
    Creates the device summary table by pivoting the master devices data with an extended index.

"""

from typing import List, Optional, Sequence, Tuple

import pandas as pd
from loguru import logger

from devices_rap.errors import ColumnsNotFoundError
from devices_rap.joins import join_mini_tables
from devices_rap.utils import (
    convert_datetime_column_headers,
    order_columns,
    rename_columns,
)


def create_pivot_sum_table(
    data: pd.DataFrame,
    values: Optional[str | List[str]] = None,
    columns: Optional[str | List[str]] = None,
    base_index: Optional[List[str]] = None,
    extended_index: Optional[str | List[str]] = None,
) -> pd.DataFrame:
    """
    Create a pivot table with the sum of the values for the given columns. The function is
    pre-loaded with the following default values that represent the columns that make up the
    Amber Summary table:
    - values: ["cln_total_cost"]
    - columns: ["activity_date"]
    - base_index: ["upd_region", "der_provider_code", "upd_high_level_device_type",
    "rag_status"]
    - extended_index: []

    Use the extended_index parameter to add additional columns to the index (e.g.
    ["der_device_code"] when creating the Amber Detail table).

    Parameters
    ----------
    data : pd.DataFrame
        The data to pivot. By default should include the columns: ["upd_region",
        "der_provider_code", "upd_high_level_device_type", "rag_status", "cln_total_cost",
        "activity_date"]

    values : list, optional
        The values to sum, by default "cln_total_cost"

    columns : list, optional
        The columns to pivot on, by default "activity_date"

    base_index : list, optional
        The base index columns, by default ["upd_region", "der_provider_code",
        "upd_high_level_device_type", "rag_status"]

    extended_index : list, optional
        The extended index columns, by default []

    Returns
    -------
    pd.DataFrame
        The pivoted data with the index reset

    Raises
    ------
    ColumnsNotFoundError
        If the columns specified in the parameters are not found in the dataset.
    """
    values = values or "cln_total_cost"
    columns = columns or "activity_date"
    base_index = base_index or [
        "upd_region",
        "der_provider_code",
        "upd_high_level_device_type",
        "rag_status",
    ]
    extended_index = extended_index or []
    if isinstance(extended_index, str):
        extended_index = [extended_index]
    index = base_index + extended_index

    logger.info(
        "Creating a pivot table with the sum of the values for the given columns. "
        f"VALUES: {values}, "
        f"COLUMNS: {columns}, "
        f"INDEX: {index}"
    )
    try:
        pivoted_data = pd.pivot_table(
            data=data, values=values, columns=columns, index=index, aggfunc="sum"
        )
    except KeyError as e:
        raise ColumnsNotFoundError(
            dataset_columns=data.columns,
            values=values,
            columns=columns,
            base_index=base_index,
            extended_index=extended_index,
        ) from e

    # Pandas pivot_table returns a multi-index DataFrame, so we reset the index and remove the
    # columns name (the name given to collection of values that make up the column not the column
    # names themselves) to make it easier to work with the data in later steps.
    pivoted_data.reset_index(inplace=True)
    pivoted_data.columns.name = None

    return pivoted_data


def get_datetime_columns(data: pd.DataFrame) -> List[str | pd.Timestamp]:
    """
    Get the datetime columns from the data.

    Parameters
    ----------
    data : pd.DataFrame
        The data to get the datetime columns from

    Returns
    -------
    Sequence[str | pd.Timestamp]
        The datetime columns in the data
    """
    return [col for col in data.columns if isinstance(col, pd.Timestamp)]


def calc_change_from_previous_month_column(
    monthly_summary_table: pd.DataFrame,
    most_recent_col: Optional[str] = None,
    second_most_recent_col: Optional[str] = None,
) -> Tuple[pd.DataFrame, Sequence[str | pd.Timestamp]]:
    """
    Calculate the change from the previous month for the most recent and second most recent columns
    in the monthly_summary_table. The function takes the last two columns in the table by default,
    but the most_recent_col and second_most_recent_col can be specified.

    Parameters
    ----------
    monthly_summary_table : pd.DataFrame
        The monthly summary table to calculate the change from the previous month
    most_recent_col : str, optional
        The most recent column to calculate the change from, by default None
    second_most_recent_col : str, optional
        The second most recent column to calculate the change from, by default None

    Returns
    -------
    pd.DataFrame
        The monthly summary table with the change from the previous month column added

    Raises
    ------
    ColumnsNotFoundError
        If the most_recent_col or second_most_recent_col specified are not found in the dataset
    """
    datetime_columns = get_datetime_columns(monthly_summary_table)
    most_recent_col = most_recent_col or datetime_columns[-1]  # type: ignore
    second_most_recent_col = second_most_recent_col or datetime_columns[-2]  # type: ignore

    try:
        monthly_summary_table["change_from_previous_month"] = monthly_summary_table[
            most_recent_col
        ].fillna(0) - monthly_summary_table[second_most_recent_col].fillna(0)
    except KeyError as e:
        raise ColumnsNotFoundError(
            dataset_columns=monthly_summary_table.columns,
            most_recent_col=most_recent_col,
            second_most_recent_col=second_most_recent_col,
        ) from e

    return monthly_summary_table, datetime_columns


def create_device_category_summary_table(
    master_devices_data: pd.DataFrame,
    provider_codes_lookup: pd.DataFrame,
    device_taxonomy: pd.DataFrame,
    exceptions: pd.DataFrame,
) -> pd.DataFrame:
    """
    This function creates the device category summary table by pivoting the master devices data.
    It is functionally a wrapper around the `create_pivot_sum_table` function utilising the default
    values set in `create_pivot_sum_table`.

    ! WARNING: This function is highly coupled to create_pivot_sum_table.

    Parameters
    ----------
    master_devices_data : pd.DataFrame
        The master devices data to pivot

    Returns
    -------
    pd.DataFrame
        The device category summary table
    """
    logger.info("Creating the device category summary (pivot) table")
    device_category_summary = create_pivot_sum_table(data=master_devices_data)

    logger.info("Joining on additional columns to the device category summary table")
    device_category_summary = join_mini_tables(
        summary_table=device_category_summary,
        provider_codes_lookup=provider_codes_lookup,
        device_taxonomy=device_taxonomy,
        exceptions=exceptions,
        include_exception_notes=True,
    )

    logger.info(
        "Calculating the change from the previous month for the device category summary table"
    )
    device_category_summary, datetime_columns = calc_change_from_previous_month_column(
        device_category_summary
    )

    logger.info("Reordering the columns in the device category summary table")
    column_order = [
        "upd_region",
        "der_provider_code",
        "current_name_in_proper_case",
        "upd_high_level_device_type",
        "description_in_title_case",
        "rag_status",
        "handover_date_zcm",
        "handover_date_vcm",
        *datetime_columns,
        "exception_notes",
        "change_from_previous_month",
    ]
    device_category_summary_ordered = order_columns(device_category_summary, column_order)

    logger.info("Renaming the columns in the device category summary table")
    renaming_dict = {
        "upd_region": "Region",
        "der_provider_code": "Provider Code",
        "current_name_in_proper_case": "Provider Name",
        "upd_high_level_device_type": "High Level Device Type",
        "description_in_title_case": "Device Category",
        "rag_status": "RAG Status",
        "handover_date_zcm": "ZCM Handover Date",
        "handover_date_vcm": "VCM Handover Date",
        "exception_notes": "Exception Notes",
        "change_from_previous_month": "Change from Previous Month",
    }
    device_category_summary_renamed = rename_columns(
        device_category_summary_ordered, renaming_dict
    )

    logger.info("Converting the datetime column headers to easier to read format")
    device_category_summary_renamed = convert_datetime_column_headers(
        device_category_summary_renamed
    )

    logger.info("Rounding the device category summary table to 2 decimal places")
    device_category_summary_rounded = device_category_summary_renamed.round(2)

    return device_category_summary_rounded


def create_device_summary_table(
    master_devices_data: pd.DataFrame,
    provider_codes_lookup: pd.DataFrame,
    device_taxonomy: pd.DataFrame,
    exceptions: pd.DataFrame,
) -> pd.DataFrame:
    """
    This function creates the device summary table by pivoting the master devices data. It is
    functionally a wrapper around the `create_pivot_sum_table` function utilising the default values
    set in `create_pivot_sum_table`, but with the extended_index parameter set to the device name,
    `cln_manufacturer_device_name`.

    ! WARNING: This function is highly coupled to create_pivot_sum_table.

    Parameters
    ----------
    master_devices_data : pd.DataFrame
        The master devices data to pivot

    Returns
    -------
    pd.DataFrame
        The device summary table
    """
    logger.info("Creating the device summary (pivot) table")

    device_summary = create_pivot_sum_table(
        data=master_devices_data,
        extended_index=["cln_manufacturer", "cln_manufacturer_device_name"],
    )

    logger.info("Joining on additional columns to the device category summary table")
    device_summary = join_mini_tables(
        summary_table=device_summary,
        provider_codes_lookup=provider_codes_lookup,
        device_taxonomy=device_taxonomy,
        exceptions=exceptions,
        include_exception_notes=True,
    )

    # We only want to get the datetime columns from the device summary table
    datetime_columns = get_datetime_columns(device_summary)

    logger.info("Reordering the columns in the device category summary table")
    column_order = [
        "upd_region",
        "der_provider_code",
        "current_name_in_proper_case",
        "upd_high_level_device_type",
        "description_in_title_case",
        "cln_manufacturer",
        "cln_manufacturer_device_name",
        "rag_status",
        *datetime_columns,
    ]
    device_summary_ordered = order_columns(device_summary, column_order)

    logger.info(
        "Renaming the columns in the device category summary table and converting the datetime "
        "column headers to easier to read format"
    )
    renaming_dict = {
        "upd_region": "Region",
        "der_provider_code": "Provider Code",
        "current_name_in_proper_case": "Provider Name",
        "upd_high_level_device_type": "High Level Device Type",
        "description_in_title_case": "Device Category",
        "cln_manufacturer": "Manufacturer",
        "cln_manufacturer_device_name": "Manufacturer Device Name",
        "rag_status": "RAG Status",
    }
    device_summary_renamed = rename_columns(device_summary_ordered, renaming_dict)

    logger.info("Rounding the device category summary table to 2 decimal places")
    device_summary_rounded = device_summary_renamed.round(2)

    return device_summary_rounded
