"""
Functions for processing the datasets for the pipeline.
"""

import warnings
from typing import Literal, Optional

import pandas as pd
from loguru import logger

from devices_rap.errors import (
    ColumnsNotFoundError,
    MergeColumnsNotFoundError,
    MergeWarning,
)
from devices_rap.exception_notes import create_exception_notes

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

    ! WARNING: This function is highly coupled to the join_datasets function.

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

    merged_master_devices = merged_master_devices.drop(columns=["org_code"])

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

    ! WARNING: This function is highly coupled to the join_datasets function.

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

    merged_master_devices = merged_master_devices.drop(columns=["dev_code"])

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

    ! WARNING: This function is highly coupled to the join_datasets function.

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

    merged_master_devices = merged_master_devices.drop(columns=["dev_code", "provider_code"])

    return merged_master_devices


def join_mini_provider_codes_lookup(
    master_devices: pd.DataFrame,
    provider_codes_lookup: pd.DataFrame,
) -> pd.DataFrame:
    """
    This function is a wrapper around the join_provider_codes_lookup function. It reduces the
    provider_codes_lookup table down to only join on the required columns. The required columns are:
    - org_code (which is only used to join and then dropped)
    - current_name_in_proper_case

    ! WARNING: This function is highly coupled to the join_datasets function.

    Parameters
    ----------
    master_devices : pd.DataFrame
        The master_devices table. Must have the "upd_high_level_device_type" column.
    provider_codes_lookup : pd.DataFrame
        The provider_codes_lookup table. Must have the "org_code" and "current_name_in_proper_case" columns.

    Returns
    -------
    pd.DataFrame
        The master_devices table with the mini_provider_codes_lookup table joined on.

    Raises
    ------
    ColumnsNotFoundError
        If the required columns are not present in the provider_codes_lookup dataset.
    """
    mini_provider_codes_columns = ["org_code", "current_name_in_proper_case"]

    logger.info(
        f"Reducing the provider_codes_lookup table down to only join on the required columns: {mini_provider_codes_columns}"
    )

    try:
        mini_provider_codes_lookup = provider_codes_lookup[mini_provider_codes_columns]
    except KeyError as e:
        raise ColumnsNotFoundError(
            dataset_columns=provider_codes_lookup.columns,
            mini_provider_codes_columns=mini_provider_codes_columns,
        ) from e

    merged_master_devices = join_provider_codes_lookup(
        master_devices=master_devices, provider_codes_lookup=mini_provider_codes_lookup
    )

    return merged_master_devices


def join_mini_device_taxonomy(
    master_devices: pd.DataFrame,
    device_taxonomy: pd.DataFrame,
) -> pd.DataFrame:
    """
    This function is a wrapper around the join_device_taxonomy function. It reduces the
    device_taxonomy table down to only join on the required columns. The required columns are:
    - dev_code (which is only used to join and then dropped)
    - description_in_title_case

    ! WARNING: This function is highly coupled to the join_datasets function.

    Parameters
    ----------
    master_devices : pd.DataFrame
        The master_devices table. Must have the "upd_high_level_device_type" column.
    device_taxonomy : pd.DataFrame
        The device_taxonomy table. Must have the "dev_code" and "description_in_title_case" columns.

    Returns
    -------
    pd.DataFrame
        The master_devices table with the mini_device_taxonomy table joined on.

    Raises
    ------
    ColumnsNotFoundError
        If the required columns are not present in the device_taxonomy dataset.
    """
    mini_taxonomy_columns = ["dev_code", "description_in_title_case"]

    logger.info(
        f"Reducing the device_taxonomy table down to only join on the required columns: {mini_taxonomy_columns}"
    )

    try:
        mini_device_taxonomy = device_taxonomy[mini_taxonomy_columns]
    except KeyError as e:
        raise ColumnsNotFoundError(
            dataset_columns=device_taxonomy.columns, mini_taxonomy_columns=mini_taxonomy_columns
        ) from e

    merged_master_devices = join_device_taxonomy(
        master_devices=master_devices, device_taxonomy=mini_device_taxonomy
    )

    return merged_master_devices


def join_mini_exceptions(
    master_devices: pd.DataFrame, exceptions: pd.DataFrame, include_exception_notes: bool = False
) -> pd.DataFrame:
    """
    This function is a wrapper around the join_exceptions function. It reduces the exceptions table
    down to only join on the required columns. The required columns are:
    - provider_code (which is only used to join and then dropped)
    - dev_code (which is only used to join and then dropped)
    - handover_date_zcm
    - handover_date_vcm
    - exception_notes (if include_exception_notes is True)

    ! WARNING: This function is highly coupled to the join_exceptions function.
    """
    mini_exceptions_columns = [
        "provider_code",
        "dev_code",
        "handover_date_zcm",
        "handover_date_vcm",
    ]

    if include_exception_notes:
        exceptions = create_exception_notes(exceptions)
        mini_exceptions_columns.append("exception_notes")

    logger.info(
        f"Reducing the exceptions table down to only join on the required columns: {mini_exceptions_columns}"
    )

    try:
        mini_exceptions = exceptions[mini_exceptions_columns]
    except KeyError as e:
        raise ColumnsNotFoundError(
            dataset_columns=exceptions.columns, mini_exceptions_columns=mini_exceptions_columns
        ) from e

    merged_master_devices = join_exceptions(
        master_devices=master_devices, exceptions=mini_exceptions
    )

    return merged_master_devices


def join_mini_tables(
    summary_table: pd.DataFrame,
    provider_codes_lookup: pd.DataFrame,
    device_taxonomy: pd.DataFrame,
    exceptions: pd.DataFrame,
    include_exception_notes: bool = True,
) -> pd.DataFrame:
    """
    This function is a wrapper around the join_mini_provider_codes_lookup,
    join_mini_device_taxonomy, and join_mini_exceptions functions. It joins the mini tables onto a
    summary_table
    """
    logger.info("Joining the mini tables onto the master_devices table to add contextual columns")

    merged_master_devices = join_mini_provider_codes_lookup(
        master_devices=summary_table, provider_codes_lookup=provider_codes_lookup
    )
    merged_master_devices = join_mini_device_taxonomy(
        master_devices=merged_master_devices, device_taxonomy=device_taxonomy
    )
    merged_master_devices = join_mini_exceptions(
        master_devices=merged_master_devices,
        exceptions=exceptions,
        include_exception_notes=include_exception_notes,
    )

    return merged_master_devices
