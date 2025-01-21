"""
Functionality that handle the output of processed data from the pipeline.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict

import pandas as pd
import tqdm
from loguru import logger

from devices_rap.config import (
    FIN_MONTH,
    FIN_YEAR,
    PROCESSED_DATA_DIR,
    USE_MULTIPROCESSING,
)


def create_excel_reports(
    output_workbooks: Dict[str, Dict[str, pd.DataFrame]],
    output_directory: Path = PROCESSED_DATA_DIR,
    fin_year: str = FIN_YEAR,
    fin_month: str = FIN_MONTH,
):
    """
    Create the Excel reports based on the processed data. The function will create an Excel file for
    each region containing the processed worksheets for that region.

    Parameters
    ----------
    output_workbooks : dict
        The processed data for each region
    output_directory : str
        The path to save the Excel reports to

    Returns
    -------
    None
    """
    logger.info("Creating excel reports")

    fin_output_directory = output_directory / fin_year / fin_month
    fin_output_directory.mkdir(parents=True, exist_ok=True)

    if USE_MULTIPROCESSING:
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(process_region, fin_output_directory, region, worksheets)
                for region, worksheets in output_workbooks.items()
            ]
            for future in tqdm.tqdm(as_completed(futures), total=len(futures), position=0):
                future.result()
    else:
        for region, worksheets in output_workbooks.items():
            process_region(fin_output_directory, region, worksheets)

    logger.success("Excel reports created successfully.")


def process_region(fin_output_directory: Path, region: str, worksheets: Dict[str, pd.DataFrame]):
    """
    Process the data for a region and create the Excel report.

    Parameters
    ----------
    fin_output_directory : Path
        The path to save the Excel reports to
    region : str
        The region to process
    worksheets : dict
        The processed data for the region

    Returns
    -------
    None
    """
    output_file = (
        fin_output_directory / f"{region.upper().replace(' ', '_')}_RAG_STATUS_REPORT.xlsx"
    )

    if output_file.exists():
        logger.warning(f"Overwriting the existing Excel file: {output_file}")
        output_file.unlink()
    else:
        logger.info(f"Creating Excel report for {region}")

    create_excel_file(output_file, worksheets)

    logger.success(f"Excel report for {region} created successfully.")


def create_excel_file(output_file: Path, worksheets: Dict[str, pd.DataFrame]):
    """
    Create an Excel file with the given worksheets.

    Parameters
    ----------
    output_file : Path
        The path to save the Excel file to
    worksheets : dict
        The worksheets to include in the Excel file

    Returns
    -------
    None
    """
    logger.debug(f"Creating the Excel file: {output_file}")
    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        workbook = writer.book
        header_format = create_header_format(workbook)

        if USE_MULTIPROCESSING:
            with ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(
                        write_worksheet, writer, sheet_name, data, header_format, output_file
                    )
                    for sheet_name, data in worksheets.items()
                ]
                for future in tqdm.tqdm(as_completed(futures), total=len(futures), position=1):
                    future.result()
        else:
            for sheet_name, data in worksheets.items():
                write_worksheet(writer, sheet_name, data, header_format, output_file)


def create_header_format(workbook) -> object:
    """
    Create the header format for the Excel file.

    Parameters
    ----------
    workbook : object
        The workbook object

    Returns
    -------
    object
        The header format
    """
    return workbook.add_format(
        {
            "bold": True,
            "text_wrap": True,
            "valign": "top",
            "fg_color": "#D9E1F2",
            "border": 1,
        }
    )


def write_worksheet(
    writer, sheet_name: str, data: pd.DataFrame, header_format: object, output_file: Path
):
    """
    Write a worksheet to the Excel file.

    Parameters
    ----------
    writer : object
        The Excel writer object
    sheet_name : str
        The name of the worksheet
    data : pd.DataFrame
        The data to write to the worksheet
    header_format : object
        The header format
    output_file : Path
        The path to the Excel file that is been written to (only used for logging context)

    Returns
    -------
    None
    """
    logger.debug(
        f"Writing data with {data.shape[0]} rows and {data.shape[1]} columns to "
        f"the {sheet_name} worksheet to the Excel file, {output_file}."
    )
    data.to_excel(writer, sheet_name=sheet_name, index=False, startrow=1, header=False)
    worksheet = writer.sheets[sheet_name]

    # Write the column headers with the defined format.
    for col_num, value in enumerate(data.columns.values):
        worksheet.write(0, col_num, value, header_format)

    worksheet.autofilter(0, 0, data.shape[0], data.shape[1] - 1)
    worksheet.autofit()
