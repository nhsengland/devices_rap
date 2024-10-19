"""
Functions for intake of data into the pipeline with any preliminary data cleansing carried out.
"""

import pandas as pd
from loguru import logger

from devices_rap.config import RAW_DATA_DIR


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

    exceptions_df = pd.read_csv(data_file_path)

    return exceptions_df


if __name__ == "__main__":
    load_exceptions_data()
