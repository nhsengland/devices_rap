"""
_summary_
"""

from typing import Any, Dict, List, Optional

import pandas as pd
from loguru import logger

from devices_rap.errors import ColumnsNotFoundError


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
    - base_index: ["nhs_england_region", "der_provider_code", "der_high_level_device_type",
    "rag_status"]
    - extended_index: []

    Use the extended_index parameter to add additional columns to the index (e.g.
    ["der_device_code"] when creating the Amber Detail table).

    Parameters
    ----------
    data : pd.DataFrame
        The data to pivot. By default should include the columns: [
            "nhs_england_region",
            "der_provider_code",
            "der_high_level_device_type",
            "rag_status",
            "cln_total_cost",
            "activity_date",
        ]
    values : list, optional
        The values to sum, by default "cln_total_cost"
    columns : list, optional
        The columns to pivot on, by default "activity_date"
    base_index : list, optional
        The base index columns, by default [
            "nhs_england_region",
            "der_provider_code",
            "der_high_level_device_type",
            "rag_status",
        ]
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
        "nhs_england_region",
        "der_provider_code",
        "der_high_level_device_type",
        "rag_status",
    ]
    extended_index = extended_index or []
    if isinstance(extended_index, str):
        extended_index = [extended_index]
    index = base_index + extended_index

    logger.info(
        "Creating a pivot table with the sum of the values for the given columns."
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


def create_device_category_summary_table():
    """
    _summary_
    """
    logger.info("Creating the device category summary (pivot) table")


def create_device_summary_table():
    """
    _summary_
    """
    logger.info("Creating the device summary (pivot) table")


def create_table_cuts(
    data: pd.DataFrame,
    cut_columns: List[str] | str,
    drop_cut_columns: bool = False,
) -> Dict[Any, pd.DataFrame]:
    """
    Create a collection of tables based on the unique values in the cut_columns. The function
    creates a table for each unique value in the cut_columns and filters the data to only include
    rows where the cut_columns value is equal to the unique value.

    Parameters
    ----------
    data : pd.DataFrame
        The data to cut
    cut_columns : list or str
        The column(s) to cut the data by
    drop_cut_columns : bool, optional
        Whether to drop the cut columns from the DataFrame, by default False

    Returns
    -------
    dict
        A dictionary of DataFrames with the unique values in the cut_columns as the keys

    Raises
    ------
    ColumnsNotFoundError
        If the cut_columns specified are not found in the dataset
    """
    logger.info(
        "Creating a collection of tables based on the unique values in the cut_columns. "
        f"CUT COLUMNS: {cut_columns}"
    )
    if isinstance(cut_columns, str):
        cut_columns = [cut_columns]

    try:
        cut_data = data.copy()
        cut_data = cut_data.set_index(cut_columns, drop=drop_cut_columns)
        cut_data = cut_data.sort_index()

        cut_data_dict = {}

        for index in cut_data.index.unique():
            cut_data_dict[index] = cut_data.loc[index].reset_index(drop=True)

    except KeyError as e:
        raise ColumnsNotFoundError(dataset_columns=data.columns, cut_columns=cut_columns) from e

    return dict(cut_data_dict)


def create_rag_summary_tables_cuts():
    """
    _summary_
    """
    logger.info("Creating the RAG summary tables")


def create_regional_data_cuts():
    """
    _summary_
    """
    logger.info("Creating the Regional summary tables")
