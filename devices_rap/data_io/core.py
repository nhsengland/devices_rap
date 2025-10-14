"""
Core orchestration functions for data input and output operations.
"""

from typing import Any

from loguru import logger
import pandas as pd

from devices_rap.config import Config
from devices_rap.data_io.input import load_devices_datasets
from devices_rap.data_io.output import (
    create_excel_reports,
    create_excel_zip_reports,
    create_pickle,
)


def load_data(pipeline_config: Config) -> dict[str, dict[str, Any]]:
    """
    Load data based on the pipeline configuration.

    Uses the hybrid loader that can handle both CSV files and SQL queries
    based on the dataset configuration keys.

    Parameters
    ----------
    pipeline_config : Config
        The configuration object containing dataset information.

    Returns
    -------
    dict
        The loaded datasets with "data" key containing DataFrames
    """
    logger.info(f"Loading data in {pipeline_config.mode} mode")
    return load_devices_datasets(pipeline_config)


def output_data(
    output_workbooks: dict[str, dict[str, pd.DataFrame]],
    pipeline_config: Config,
) -> None:
    """
    Handle the output of processed data from the pipeline. This function will create the Excel
    reports and pickle files based on the processed data for each region. It will check the
    configuration to determine which outputs to create (Excel, pickle, or both) and will create the
    output directory if it does not exist.

    Parameters
    ----------
    output_workbooks : dict
        The processed data for each region
    pipeline_config : Config
        The configuration object containing the output directory and other settings

    Returns
    -------
    None
    """
    outputs = pipeline_config.outputs

    if not outputs:
        logger.warning("No outputs configured. Skipping output data.")
        return

    output_directory = pipeline_config.create_output_directory()

    for output_format in outputs:
        if output_format.startswith("excel"):
            use_multiprocessing = pipeline_config.use_multiprocessing
            create_excel_reports(
                output_workbooks=output_workbooks,
                output_directory=output_directory,
                use_multiprocessing=use_multiprocessing,
            )
            if output_format == "excel_zip":
                fin_month = pipeline_config.fin_month
                fin_year = pipeline_config.fin_year
                create_excel_zip_reports(
                    output_directory=output_directory,
                    fin_month=fin_month,
                    fin_year=fin_year,
                )
        elif output_format == "pickle":
            fin_month = pipeline_config.fin_month
            fin_year = pipeline_config.fin_year
            create_pickle(
                output_workbooks=output_workbooks,
                output_directory=output_directory,
                fin_month=fin_month,
                fin_year=fin_year,
            )
        else:
            logger.warning(
                f"{output_format} output is not implemented yet. Skipping {output_format} output."
            )
