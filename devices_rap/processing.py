"""
Functions for processing the datasets for the pipeline.
"""

import pandas as pd
from loguru import logger


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
