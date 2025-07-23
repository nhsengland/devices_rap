"""
Functions for processing the datasets for the pipeline.
"""

import pandas as pd
from loguru import logger
from nhs_herbot.errors import ColumnsNotFoundError
from nhs_herbot.joins import join_datasets

from devices_rap.exception_notes import create_exception_notes


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
    mini_taxonomy_columns = [
        "dev_code",
        "description_in_title_case",
        "upd_migrated_categories",
        "upd_non_migrated_categories",
    ]

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
