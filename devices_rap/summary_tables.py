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

from typing import List, Optional

import pandas as pd
from loguru import logger

from devices_rap.errors import ColumnsNotFoundError
from devices_rap.utils import calc_change_from_previous_month_column


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


def create_device_category_summary_table(
    master_devices_data: pd.DataFrame,
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

    logger.info(
        "Calculating the change in cost between the latest and second latest activity dates"
    )
    device_category_summary = calc_change_from_previous_month_column(device_category_summary)

    return device_category_summary


def create_device_summary_table(
    master_devices_data: pd.DataFrame,
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

    return device_summary
