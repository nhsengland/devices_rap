"""
Functions for processing the datasets for the pipeline.
"""

import pandas as pd
from loguru import logger


def translate_high_level_devices_type(
    data: pd.DataFrame, col_name: str = "high_level_device_type"
) -> pd.DataFrame:
    """
    _summary_

    Parameters
    ----------
    data : pd.DataFrame
        _description_
    col_name : str, optional
        _description_, by default "high_level_device_type"

    Returns
    -------
    pd.DataFrame
        _description_
    """
    logger.info(f"Translating the high level device type in column: {col_name}")
    return data


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
