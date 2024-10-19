"""
Functions for intake of data into the pipeline with any preliminary data cleansing carried out.
"""

import pandas as pd
from loguru import logger

from devices_rap.config import EXTERNAL_DATA_DIR


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

    provider_codes_df = pd.read_csv(data_file_path)

    return provider_codes_df


if __name__ == "__main__":
    load_provider_codes_lookup()
