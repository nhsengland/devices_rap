"""
Functions for processing the datasets for the pipeline.
"""

import warnings
from typing import Literal, Optional

import pandas as pd
from loguru import logger

from devices_rap.errors import ColumnsNotFoundError, MergeWarning

MergeHow = Literal["left", "right", "outer", "inner"]


def check_merge_health(
    merged_df: pd.DataFrame, merge_column: Optional[str] = "_merge", keep_merge: bool = False
) -> pd.DataFrame:
    """
    Check the merge for any issues and return the merged DataFrame.

    Parameters
    ----------
    merged_df : pd.DataFrame
        The merged DataFrame to check.
    merge_column : str, optional
        The column to check for issues, by default "_merge"

    Returns
    -------
    pd.DataFrame
        The merged DataFrame.
    """
    merge_column = merge_column or "_merge"

    if merge_column not in merged_df.columns:
        logger.info(f"The merge column, {merge_column}, was not found in the merged dataframe")
        return merged_df

    bad_merge_found = False
    for bad_merge in ("left_only", "right_only"):
        bad_merge_count = merged_df[merge_column].value_counts().get(bad_merge, 0)
        if bad_merge_count:
            warnings.warn(
                f"There are {bad_merge_count} '{bad_merge}' rows in the merged data", MergeWarning
            )
            bad_merge_found = True

    if not bad_merge_found:
        logger.info("The merge was healthy.")

    if keep_merge:
        return merged_df

    merged_df = merged_df.drop(columns=merge_column)

    return merged_df


def join_datasets(
    left: pd.DataFrame,
    right: pd.DataFrame,
    left_on,
    right_on,
    how: MergeHow = "left",
    check_merge: bool | Literal["keep"] = True,
    indicator_override: Optional[str] = None,
    **merge_kwargs,
) -> pd.DataFrame:
    """
    Join two datasets together.

    Parameters
    ----------
    left : pd.DataFrame
        The left dataset to join.
    right : pd.DataFrame
        The right dataset to join.
    left_on : str | list[str]
        The column to join on in the left dataset.
    right_on : str | list[str]
        The column to join on in the right dataset.
    how : MergeHow, optional
        The type of join to perform, by default "inner"
    check_merge : bool | Literal["keep"], optional
        Whether to check the merge for issues, by default True. If "keep" is passed, the merge
        column will be kept in the merged DataFrame.
    indicator_override : Optional[str], optional
        Override the indicator parameter in the merge function, by default None
    merge_kwargs : dict
        Additional keyword arguments to pass to the pandas.merge function.

    Returns
    -------
    pd.DataFrame
        The joined dataset.
    """
    # if left_on not in left.columns:
    #     raise ColumnsNotFoundError(f"The column, {left_on}, was not found in the left dataset")
    # if right_on not in right.columns:
    #     raise ColumnsNotFoundError(f"The column, {right_on}, was not found in the right dataset")

    logger.info(f"Joining the datasets on {left_on} and {right_on}")

    indicator = False
    if check_merge:
        indicator = indicator_override or True

    try:
        merged_data = pd.merge(
            left=left,
            right=right,
            left_on=left_on,
            right_on=right_on,
            how=how,
            indicator=indicator,
            **merge_kwargs,
        )
    except KeyError as e:
        # TODO - could this be done in ColumnsNotFoundError?
        bad_columns = {"left": [], "right": []}
        for side, column_set in {"left": left_on, "right": right_on}.items():
            if isinstance(column_set, str):
                column_set = [column_set]
            for column in column_set:
                if side == "left" and column not in left.columns:
                    bad_columns["left"].append(column)
                if side == "right" and column not in right.columns:
                    bad_columns["right"].append(column)
        raise ColumnsNotFoundError(
            f"The column(s) {bad_columns} were not found in the respective datasets"
        ) from e

    if check_merge:
        keep_merge = check_merge == "keep"
        merged_data = check_merge_health(
            merged_data, merge_column=indicator_override, keep_merge=keep_merge
        )

    return merged_data


def lookup_provider_codes(master_df: pd.DataFrame, provider_codes: pd.DataFrame) -> pd.DataFrame:
    """
    _summary_

    Parameters
    ----------
    master_df : pd.DataFrame
        _description_
    provider_codes : pd.DataFrame
        _description_

    Returns
    -------
    pd.DataFrame
        _description_
    """
    logger.info("Joining the provider_codes table onto the master_df table")
    assert provider_codes.empty
    return master_df


def lookup_taxonomy_tariff(master_df: pd.DataFrame, taxonomy_tariff: pd.DataFrame) -> pd.DataFrame:
    """
    _summary_

    Parameters
    ----------
    master_df : pd.DataFrame
        _description_
    taxonomy_tariff : pd.DataFrame
        _description_

    Returns
    -------
    pd.DataFrame
        _description_
    """
    logger.info("Joining the taxonomy_tariff table onto the master_df table")
    assert taxonomy_tariff.empty
    return master_df


def merge_exceptions_data(master_df: pd.DataFrame, exceptions: pd.DataFrame) -> pd.DataFrame:
    """
    _summary_

    Parameters
    ----------
    master_df : pd.DataFrame
        _description_
    exceptions : pd.DataFrame
        _description_

    Returns
    -------
    pd.DataFrame
        _description_
    """
    logger.info("Joining the exceptions table onto the master_df table")
    assert exceptions.empty
    return master_df
