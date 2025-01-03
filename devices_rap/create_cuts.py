"""
Functions to create tables by cutting the data based on unique values in specified columns.

Functions
---------
create_table_cuts(data, cut_columns, drop_cut_columns=False)
    Create a collection of tables based on the unique values in the cut_columns.

create_regional_rag_summary_tables_cuts(pivoted_master_data)
    Create a collection of Regional RAG summary tables by cutting the pivoted master data by the
    NHS England Region, `nhs_england_region`, and RAG Status, `rag_status`.
"""

from typing import Any, Dict, List

import pandas as pd
from loguru import logger

from devices_rap.errors import ColumnsNotFoundError


def create_table_cuts(
    data: pd.DataFrame,
    cut_columns: List[str] | str,
    drop_cut_columns: bool = False,
) -> Dict[Any, pd.DataFrame]:
    """
    Create a collection of tables based on the unique values in the cut_columns. The function
    creates a table for each unique value in the cut_columns and separates the data into a
    dictionary with the unique values (or combinations of unique values) as the keys.

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


def create_regional_rag_summary_tables_cuts(
    pivoted_master_data: pd.DataFrame,
) -> Dict[str, pd.DataFrame]:
    """
    Create a collection of Regional RAG summary tables by cutting the pivoted master data by the
    NHS England Region, `nhs_england_region`, and RAG Status, `rag_status`.

    Parameters
    ----------
    pivoted_master_data : pd.DataFrame
        The pivoted master data to cut into Regional RAG summary tables

    Returns
    -------
    dict
        A dictionary of DataFrames with the unique values in the cut_columns as the keys
    """
    logger.info("Creating the Regional RAG summary tables")

    rag_summary_tables = create_table_cuts(
        data=pivoted_master_data, cut_columns=["nhs_england_region", "rag_status"]
    )

    logger.success(
        f"Created the collection of {len(rag_summary_tables.keys())} Regional RAG summary tables"
    )

    return rag_summary_tables
