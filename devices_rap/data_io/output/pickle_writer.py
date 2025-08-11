"""
Pickle writing functionality for the devices_rap pipeline.
"""

from pathlib import Path
from typing import Dict

import pandas as pd
from loguru import logger


def create_pickle(
    output_workbooks: Dict[str, Dict[str, pd.DataFrame]],
    output_directory: Path,
    fin_month: str,
    fin_year: str,
):
    """
    Create a pickle file containing the processed data for all regions. The pickle file will be saved
    in the output directory with a name that includes the financial year and month.

    Parameters
    ----------
    output_workbooks : dict
        The processed data for each region
    output_directory : Path
        The path to save the pickle file to
    fin_month : str
        The financial month for which the data is being processed
    fin_year : str
        The financial year for which the data is being processed

    Returns
    -------
    None
    """
    logger.info("Creating pickle file")

    output_file = output_directory / f"{fin_year}_{fin_month}_amber_report_all_regions.pkl"
    if output_file.exists():
        logger.warning(f"Overwriting the existing pickle file: {output_file}")
        output_file.unlink()
    else:
        logger.info(f"Creating pickle file for all regions for {fin_month} {fin_year}")

    with open(output_file, "wb") as f:
        pd.to_pickle(output_workbooks, f)

    logger.success(f"Pickle file for all regions for {fin_month} {fin_year} created successfully.")
