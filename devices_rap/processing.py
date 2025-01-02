"""
Functions for processing the datasets for the pipeline.
"""

import warnings
from typing import Literal, Optional

import pandas as pd
from loguru import logger

from devices_rap.errors import MergeColumnsNotFoundError, MergeWarning

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

    Raises
    ------
    MergeColumnsNotFoundError
        If the columns to join on are not found in the datasets. Reports which columns are missing.
    """
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
        raise MergeColumnsNotFoundError(left.columns, right.columns, left_on, right_on) from e

    if check_merge:
        keep_merge = check_merge == "keep"
        merged_data = check_merge_health(
            merged_data, merge_column=indicator_override, keep_merge=keep_merge
        )

    return merged_data


def join_provider_codes_lookup(
    master_devices: pd.DataFrame, provider_codes_lookup: pd.DataFrame
) -> pd.DataFrame:
    """
    This function is a wrapper around the join_datasets function. It joins on the
    'der_provider_code' column in the master_devices dataset and the 'org_code' column in the
    provider_codes_lookup dataset. The join type is a 'many_to_one' left join.

    join_datasets by defaults checks the merge health to ensure that there is not a 'left_only' or
    'right_only' merge. If there are any 'left_only' or 'right_only' merges, a MergeWarning is
    raised. The merge column is dropped from the merged DataFrame by default.

    Parameters
    ----------
    master_devices : pd.DataFrame
        The master_devices table. Must have the "der_provider_code" column.
    provider_codes_lookup : pd.DataFrame
        The provider_codes_lookup table. Must have the "org_code" column.

    Returns
    -------
    pd.DataFrame
        The master_devices table with the provider_codes_lookup table joined on.
    """
    logger.info("Joining the provider_codes_lookup table onto the master_devices table")

    merged_master_devices = join_datasets(
        left=master_devices,
        right=provider_codes_lookup,
        left_on="der_provider_code",
        right_on="org_code",
        validate="many_to_one",
    )

    return merged_master_devices


def join_device_taxonomy(
    master_devices: pd.DataFrame, device_taxonomy: pd.DataFrame
) -> pd.DataFrame:
    """
    This function is a wrapper around the join_datasets function. It joins on the
    'upd_high_level_device_type' column in the master_devices dataset and the 'dev_code' column in
    the device_taxonomy dataset. The join type is a 'many_to_one' left join.

    join_datasets by defaults checks the merge health to ensure that there is not a 'left_only' or
    'right_only' merge. If there are any 'left_only' or 'right_only' merges, a MergeWarning is
    raised. The merge column is dropped from the merged DataFrame by default.

    Parameters
    ----------
    master_devices : pd.DataFrame
        The master_devices table. Must have the "upd_high_level_device_type" column.
    device_taxonomy : pd.DataFrame
        The device_taxonomy table. Must have the "device_type" column.

    Returns
    -------
    pd.DataFrame
        The master_devices table with the device_taxonomy table joined on.
    """
    logger.info("Joining the device_taxonomy table onto the master_devices table")

    merged_master_devices = join_datasets(
        left=master_devices,
        right=device_taxonomy,
        left_on="upd_high_level_device_type",
        right_on="dev_code",
        validate="many_to_one",
    )

    return merged_master_devices


def join_exceptions(
    master_devices: pd.DataFrame, exceptions: pd.DataFrame, strict_validate: bool = False
) -> pd.DataFrame:
    """
    This function is a wrapper around the join_datasets function. It joins on the
    'upd_high_level_device_type' and 'der_provider_code' columns in the master_devices dataset and
    the 'dev_code' and 'provider_code' column in the exceptions data. The join type is a
    'many_to_many' left join (if strict_validate is false).

    join_datasets by defaults checks the merge health to ensure that there is not a 'left_only' or
    'right_only' merge. If there are any 'left_only' or 'right_only' merges, a MergeWarning is
    raised. The merge column is dropped from the merged DataFrame by default.

    The strict_validate setting should be used when we are more confident in the exceptions data and
    want to validate a 'many-to-one' merge instead of a 'many-to-many' merge.

    Parameters
    ----------
    master_devices : pd.DataFrame
        The master_devices table. Must have the ["upd_high_level_device_type", "der_provider_code"]
        columns.
    exceptions : pd.DataFrame
        The exceptions table. Must have the ["dev_code", "provider_code"] columns.

    Returns
    -------
    pd.DataFrame
        The master_devices table with the exceptions table joined on.
    """
    logger.info("Joining the exceptions table onto the master_devices table")

    validate = "many_to_one" if strict_validate else "many_to_many"

    merged_master_devices = join_datasets(
        left=master_devices,
        right=exceptions,
        left_on=["upd_high_level_device_type", "der_provider_code"],
        right_on=["dev_code", "provider_code"],
        validate=validate,
    )

    return merged_master_devices
