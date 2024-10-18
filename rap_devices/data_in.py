"""
_summary_
"""

import pandas as pd
from loguru import logger

from rap_devices.config import EXTERNAL_DATA_DIR, RAW_DATA_DIR


def load_master_data(master_csv_name: str = "data_2324_mater_m5.csv") -> pd.DataFrame:
    """
    _summary_

    Parameters
    ----------
    master_csv_name : str, optional
        _description_, by default "data_2324_mater_m5.csv"

    Returns
    -------
    pd.DataFrame
        _description_
    """
    data_file_path = RAW_DATA_DIR / master_csv_name
    logger.info(f"Loading Master Data from: {data_file_path}")
    return pd.DataFrame()


def load_exceptions_data(exceptions_csv_name: str = "exception_report_m5.csv") -> pd.DataFrame:
    """
    _summary_

    Parameters
    ----------
    exceptions_csv_name : str, optional
        _description_, by default "exception_report_m5.csv"

    Returns
    -------
    pd.DataFrame
        _description_
    """
    data_file_path = RAW_DATA_DIR / exceptions_csv_name
    logger.info(f"Loading Exceptions Report from: {data_file_path}")
    return pd.DataFrame()


def load_provider_codes_lookup(lookup_csv_name: str = "provider_codes_lookup.csv") -> pd.DataFrame:
    """
    _summary_

    Parameters
    ----------
    lookup_csv_name : str, optional
        _description_, by default "provider_codes_lookup.csv"

    Returns
    -------
    pd.DataFrame
        _description_
    """
    data_file_path = EXTERNAL_DATA_DIR / lookup_csv_name
    logger.info(f"Loading Exceptions Report from: {data_file_path}")
    return pd.DataFrame()
