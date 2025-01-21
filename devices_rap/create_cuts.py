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
import tqdm
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

        for index in tqdm.tqdm(cut_data.index.unique(), desc="Creating cut tables"):
            cut_data_dict[index] = cut_data.loc[index].reset_index(drop=True)

    except KeyError as e:
        raise ColumnsNotFoundError(dataset_columns=data.columns, cut_columns=cut_columns) from e

    return dict(cut_data_dict)


def create_regional_table_cuts(
    tables: Dict[str, pd.DataFrame]
) -> Dict[str, Dict[str, pd.DataFrame]]:
    """
    Create a collection of Regional RAG summary tables by cutting the provided tables by the
    'Region' column.

    Parameters
    ----------
    tables : dict
        A dictionary where keys are table types (e.g., 'summary', 'detailed') and values are
        the corresponding DataFrames.

    Returns
    -------
    dict
        A dictionary where keys are regions and values are dictionaries of table types and
        their corresponding filtered DataFrames.
    """
    rag_summary_tables = {}

    for table_type, data in tqdm.tqdm(tables.items(), position=0):
        logger.info(f"Creating the Regional RAG {table_type} summary tables")
        regional_summary_tables = create_table_cuts(data=data, cut_columns=["upd_region"])
        for region, region_data in tqdm.tqdm(regional_summary_tables.items(), position=1):
            if region not in rag_summary_tables:
                rag_summary_tables[region] = {}
            rag_summary_tables[region][table_type] = region_data

    return rag_summary_tables
