"""
This module provides functions to process worksheet data based on provided configurations.
The functions include filtering data, adding subtotals, handling datetime columns, ordering
columns, renaming columns, rounding data, and processing worksheets and regions.

Functions
---------
filter_data(worksheet_data: pd.DataFrame, worksheet_filters: Dict[str, list]) -> pd.DataFrame
    Filter the worksheet data based on the provided filters.

add_subtotals(
) -> pd.DataFrame

handle_datetime_columns(
) -> Tuple[pd.DataFrame, Dict[str, str]]
    Handle the datetime columns in the worksheet data.

order_columns(worksheet_data: pd.DataFrame, worksheet_columns: Dict[str, str]) -> pd.DataFrame
    Order the columns in the worksheet data based on the provided column order.

rename_columns(
) -> pd.DataFrame
    Rename the columns in the worksheet data based on the provided column mapping.

round_data(worksheet_data: pd.DataFrame) -> pd.DataFrame

process_worksheet(worksheet_config: Dict, datasets: Dict[str, pd.DataFrame]) -> pd.DataFrame
    Process the worksheet data based on the provided configuration.

process_region(
) -> Dict[str, pd.DataFrame]
    Process the output instructions for the specified region.

interpret_output_instructions(
) -> Dict[str, Dict[str, pd.DataFrame]]
    Interpret the output instructions for each region.

"""

from typing import Dict, List, Literal, Optional, Tuple

import pandas as pd
import tqdm
from loguru import logger
from nhs_herbot.errors import ColumnsNotFoundError, DataSetNotFoundError
from nhs_herbot.utils import get_datetime_columns

from devices_rap.config import Config


def filter_data(
    worksheet_data: pd.DataFrame, worksheet_filters: Dict[str, list | Dict[Literal["not"], list]]
) -> pd.DataFrame:
    """
    Filter the worksheet data based on the provided filters. The function will filter the data
    based on the columns and values provided in the worksheet_filters dictionary.

    Parameters
    ----------
    worksheet_data : pd.DataFrame
        The data to filter
    worksheet_filters : dict
        The filters to apply to the data

    Returns
    -------
    pd.DataFrame
        The filtered data

    Examples
    --------
    >>> worksheet_data = pd.DataFrame({
    ...     "col1": ["A", "B", "C", "D", "E"],
    ...     "col2": [1, 2, 3, 4, 5],
    ...     "col3": [10, 20, 30, 40, 50]
    ... })
    >>> worksheet_filters = {"col1": ["A", "B", "C"]}
    >>> filter_data(worksheet_data, worksheet_filters)
        col1  col2  col3
    0    A     1    10
    1    B     2    20
    2    C     3    30
    """
    try:
        for column, filter_values in worksheet_filters.items():
            if isinstance(filter_values, dict) and "not" in filter_values:
                worksheet_data = worksheet_data[~worksheet_data[column].isin(filter_values["not"])]
            elif isinstance(filter_values, list):
                worksheet_data = worksheet_data[worksheet_data[column].isin(filter_values)]
            elif isinstance(filter_values, (str, int, float, bool)):
                # If the filter value is a boolean, we assume it is a filter to keep rows with True values.
                worksheet_data = worksheet_data[worksheet_data[column] == filter_values]
            else:
                raise ValueError(f"Invalid filter value for column {column}: {filter_values}")
    except KeyError as e:
        raise ColumnsNotFoundError(
            dataset_columns=worksheet_data.columns, filter_columns=worksheet_filters.keys()
        ) from e
    return worksheet_data


def add_subtotals(
    worksheet_data: pd.DataFrame,
    subtotal_columns: List[str],
    sort_columns: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Adds subtotal rows to a pivoted DataFrame based on specified columns.

    Parameters
    ----------
    worksheet_data : pd.DataFrame
        The pivoted DataFrame to which subtotals will be added.
    subtotal_columns : List[str]
        List of columns to group by and add subtotals for.
    sort_columns : Optional[List[str]], optional
        List of columns to sort the DataFrame by after adding subtotals, by default None.

    Returns
    -------
    pd.DataFrame
        The DataFrame with added subtotal rows.
    """
    try:
        for col in subtotal_columns:
            subtotal = (
                worksheet_data.groupby(subtotal_columns[: subtotal_columns.index(col) + 1])
                .sum(numeric_only=True)
                .reset_index()
            )
            subtotal[col] = subtotal[col].astype(str) + " Total"
            worksheet_data = pd.concat([worksheet_data, subtotal], ignore_index=True)

        # The method we use causes duplicate rows when totaling for the first columns in the
        # subtotal_columns list.
        worksheet_data = worksheet_data[
            ~worksheet_data[subtotal_columns].apply(
                lambda x: x.str.strip().eq("Total").any(), axis=1
            )
        ]
    except KeyError as e:
        raise ColumnsNotFoundError(
            dataset_columns=worksheet_data.columns, subtotal_columns=subtotal_columns
        ) from e

    try:
        if sort_columns:
            worksheet_data = worksheet_data.sort_values(by=sort_columns).reset_index(drop=True)
    except KeyError as e:
        raise ColumnsNotFoundError(
            dataset_columns=worksheet_data.columns, sort_columns=sort_columns
        ) from e

    return worksheet_data


def handle_datetime_columns(
    worksheet_data: pd.DataFrame, worksheet_columns: Dict[str, str | None]
) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    Handle the datetime columns in the worksheet data. The function will check if the datetime
    columns are present in the column_order list and if so, replace the "datetime_columns" element
    with the actual datetime columns. The function will then convert the datetime columns to the
    specified datetime format.
    """
    datetime_columns = get_datetime_columns(worksheet_data)

    altered_worksheet_columns = {}

    for column, value in worksheet_columns.items():
        if column == "datetime_columns":
            for datetime_column in datetime_columns:
                datetime_format = value or "%b %Y"
                altered_worksheet_columns[datetime_column] = datetime_column.strftime(
                    datetime_format
                )
        else:
            altered_worksheet_columns[column] = value

    return worksheet_data, altered_worksheet_columns


def order_columns(worksheet_data: pd.DataFrame, worksheet_columns: Dict[str, str]) -> pd.DataFrame:
    """
    Order the columns in the worksheet data based on the provided column order. The function will
    reindex the columns in the worksheet data based on the order provided in the worksheet_columns
    dictionary.

    Parameters
    ----------
    worksheet_data : pd.DataFrame
        The dataset to arrange the columns in the order specified in the worksheet_columns dictionary
    worksheet_columns : dict
        The columns to order the dataset by

    Returns
    -------
    pd.DataFrame
        The dataset with the columns ordered as specified in the worksheet_columns dictionary

    Raises
    ------
    ColumnsNotFoundError
        If the columns specified in the worksheet_columns dictionary are not found in the dataset
    """
    column_order = list(worksheet_columns.keys())
    try:
        ordered_worksheet_data = worksheet_data[column_order]
    except KeyError as e:
        raise ColumnsNotFoundError(
            dataset_columns=worksheet_data.columns, column_order=column_order
        ) from e

    return ordered_worksheet_data


def rename_columns(
    worksheet_data: pd.DataFrame, worksheet_columns: Dict[str, str]
) -> pd.DataFrame:
    """
    Rename the columns in the worksheet data based on the provided column mapping. Acts as a wrapper
    around the DataFrame.rename method but with error handling to raise a ColumnsNotFoundError if
    the columns specified in the worksheet_columns dictionary are not found in the dataset.

    Parameters
    ----------
    worksheet_data : pd.DataFrame
        The dataset to rename the columns in
    worksheet_columns : dict
        The columns to rename with the new column names

    Returns
    -------
    pd.DataFrame
        The dataset with the columns renamed as specified in the worksheet_columns dictionary

    Raises
    ------
    ColumnsNotFoundError
        If the columns specified in the worksheet_columns dictionary are not found in the dataset
    """
    try:
        renamed_worksheet_data = worksheet_data.rename(columns=worksheet_columns, errors="raise")
    except KeyError as e:
        raise ColumnsNotFoundError(
            dataset_columns=worksheet_data.columns,
            column_rename=worksheet_columns.keys(),
        ) from e
    return renamed_worksheet_data


def round_data(worksheet_data: pd.DataFrame, decimals: int) -> pd.DataFrame:
    """
    Wrapper around the DataFrame.round method to round the data in the worksheet to the specified
    number of decimal places.
    """
    rounded_worksheet_data = worksheet_data.round(decimals)
    return rounded_worksheet_data


def process_worksheet(worksheet_config: Dict, datasets: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Process the worksheet data based on the provided configuration. The function will filter the data
    based on the provided filters, handle the datetime columns, order the columns, rename the columns,
    and round the data to two decimal places.

    Parameters
    ----------
    worksheet_config : dict
        The configuration for the worksheet including the type of dataset to use, the filters to apply,
        and the columns to process
    datasets : dict
        The datasets to use for processing the worksheet.
    """
    worksheet_type = worksheet_config["type"]

    try:
        worksheet_data = datasets[worksheet_type]
    except KeyError as e:
        raise DataSetNotFoundError(
            f"The dataset specified in the worksheet configuration, {worksheet_type}, was not found"
            f" in the datasets: {list(datasets.keys())}"
        ) from e

    worksheet_filters = worksheet_config.get("filters", {})
    filtered_worksheet_data = filter_data(
        worksheet_data=worksheet_data, worksheet_filters=worksheet_filters
    )

    if "sub-totals" in worksheet_config:
        subtotal_columns = worksheet_config["sub-totals"]
        sort_columns = worksheet_config.get("sort_columns", subtotal_columns)
        sub_total_worksheet_data = add_subtotals(
            worksheet_data=filtered_worksheet_data,
            subtotal_columns=subtotal_columns,
            sort_columns=sort_columns,
        )
    else:
        sub_total_worksheet_data = filtered_worksheet_data

    worksheet_columns = worksheet_config.get("columns", {})

    unchanged_worksheet_data, worksheet_columns = handle_datetime_columns(
        worksheet_data=sub_total_worksheet_data, worksheet_columns=worksheet_columns
    )

    ordered_worksheet_data = order_columns(
        worksheet_data=unchanged_worksheet_data, worksheet_columns=worksheet_columns
    )

    renamed_worksheet_data = rename_columns(
        worksheet_data=ordered_worksheet_data, worksheet_columns=worksheet_columns
    )

    decimals = worksheet_config.get("round_to", 0)
    final_worksheet_data = round_data(worksheet_data=renamed_worksheet_data, decimals=decimals)

    return final_worksheet_data


def process_region(
    region: str,
    datasets: Dict[str, pd.DataFrame],
    instructions: Dict[str, Dict],
) -> Dict[str, pd.DataFrame]:
    """
    Process the output instructions for the specified region. The function will process each worksheet
    in the instructions and return a dictionary of the processed worksheets with the worksheet name as
    the key and the processed data as the value ready for writing to an Excel file.
    """
    logger.info(f"Interpreting output instructions for the {region} region")

    output_worksheets = {}
    for worksheet_name, worksheet_config in tqdm.tqdm(instructions.items(), position=1):
        logger.info(f"Processing the {worksheet_name} worksheet for the {region} region")
        output_worksheets[worksheet_name] = process_worksheet(
            worksheet_config=worksheet_config, datasets=datasets
        )

    return output_worksheets


def interpret_output_instructions(
    pipeline_config: Config, region_cuts: Dict[str, Dict[str, pd.DataFrame]]
) -> Dict[str, Dict[str, pd.DataFrame]]:
    """
    Interpret the output instructions for each region. The function will process the output instructions
    for each region and return a dictionary of the processed worksheets with the region name as the key
    and the processed data dictionary as the value ready for writing to an Excel file.
    """
    logger.info("Interpreting output instructions for each region")
    instructions = pipeline_config.amber_report_output_instructions

    output_workbooks = {}

    for region, datasets in tqdm.tqdm(region_cuts.items()):
        output_workbooks[region] = process_region(region, datasets, instructions)

    return output_workbooks
