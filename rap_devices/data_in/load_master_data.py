"""
_summary_
"""

import pandas as pd
from loguru import logger

from devices_rap.config import RAW_DATA_DIR


def load_master_data(master_csv_name: str = "data_2324_master_m5.csv") -> pd.DataFrame:
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

    master_df = pd.read_csv(data_file_path)

    return master_df
