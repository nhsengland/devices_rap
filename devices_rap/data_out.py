"""
Functionality that handle the output of processed data from the pipeline.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Literal, Optional

import pandas as pd
import tqdm
from loguru import logger

from devices_rap.config import (
    FIN_MONTH,
    FIN_YEAR,
    PROCESSED_DATA_DIR,
    USE_MULTIPROCESSING,
)

FormatsDict = Dict[Literal["header", "total", "default", "cost"], object]


def create_excel_reports(
    output_workbooks: Dict[str, Dict[str, pd.DataFrame]],
    output_directory: Optional[Path] = None,
    fin_year: Optional[str] = None,
    fin_month: Optional[str] = None,
):
    """
    Create the Excel reports based on the processed data. The function will create an Excel file for
    each region containing the processed worksheets for that region.

    Parameters
    ----------
    output_workbooks : dict
        The processed data for each region
    output_directory : Path, optional
        The directory to save the Excel reports to, by default PROCESSED_DATA_DIR
    fin_year : str, optional
        The financial year, by default FIN_YEAR
    fin_month : str, optional
        The financial month, by default FIN_MONTH

    Returns
    -------
    None
    """
    output_directory = output_directory or PROCESSED_DATA_DIR
    fin_year = fin_year or FIN_YEAR
    fin_month = fin_month or FIN_MONTH

    logger.info("Creating excel reports")

    fin_output_directory = output_directory / fin_year / fin_month
    fin_output_directory.mkdir(parents=True, exist_ok=True)

    if USE_MULTIPROCESSING:
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(
                    process_region,
                    fin_output_directory=fin_output_directory,
                    region=region,
                    worksheets=worksheets,
                )
                for region, worksheets in output_workbooks.items()
            ]
            for future in tqdm.tqdm(as_completed(futures), total=len(futures), position=0):
                future.result()
    else:
        for region, worksheets in output_workbooks.items():
            process_region(
                fin_output_directory=fin_output_directory,
                region=region,
                worksheets=worksheets,
            )

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

    create_excel_file(output_file=output_file, worksheets=worksheets)

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
        formats = create_formats(workbook)

        if USE_MULTIPROCESSING:
            with ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(
                        write_worksheet,
                        writer=writer,
                        sheet_name=sheet_name,
                        data=data,
                        formats=formats,
                        output_file=output_file,
                    )
                    for sheet_name, data in worksheets.items()
                ]
                for future in tqdm.tqdm(as_completed(futures), total=len(futures), position=1):
                    future.result()
        else:
            for sheet_name, data in worksheets.items():
                write_worksheet(
                    writer=writer,
                    sheet_name=sheet_name,
                    data=data,
                    formats=formats,
                    output_file=output_file,
                )


def create_formats(workbook) -> FormatsDict:
    """
    Create the formats for the Excel file. This include the formats for the:
    - Header rows
    - Total rows

    Parameters
    ----------
    workbook : object
        The workbook object

    Returns
    -------
    FORMATS_DICT (dict[str, object])
        A dictionary containing the formats for the Excel file
    """
    format_config = {
        "default": {},
        "cost": {
            "num_format": "£#,##0",
        },
        "header": {
            "bold": True,
            "text_wrap": True,
            "valign": "top",
            "fg_color": "#D9E1F2",
            "border": 1,
        },
        "total": {
            "bold": True,
            "fg_color": "#C6EFCE",
            "num_format": "£#,##0",
        },
    }

    formats = {}

    for name, config in format_config.items():
        if config:
            formats[name] = workbook.add_format(config)
        else:
            formats[name] = workbook.add_format()

    return formats


def apply_excel_formatting(writer, data: pd.DataFrame, formats: FormatsDict, sheet_name: str):
    """
    Apply formatting to the Excel worksheet. This includes:
    - Header formatting
    - Total row formatting
    - Column formatting for floats
    - Autofilter for the header row
    - Autofit for the columns

    Parameters
    ----------
    writer : pd.ExcelWriter
        The Excel writer object
    data : pd.DataFrame
        The data to write to the worksheet
    formats : dict
        The formats to apply to the worksheet
    sheet_name : str
        The name of the worksheet
    """
    # Write the column headers with the defined format.
    header_format = formats["header"]

    worksheet = writer.sheets[sheet_name]
    for col_num, value in enumerate(data.columns.values):
        worksheet.write(0, col_num, value, header_format)

    worksheet.autofilter(0, 0, data.shape[0], data.shape[1] - 1)

    # Apply formatting for rows with "Total" in the provider code column
    for row_num, (provider_code, region) in enumerate(
        zip(data["Provider Code"], data["Region"]), start=1
    ):  # Start from row 1 (after header)
        if "Total" in str(provider_code) or "Total" in str(region):
            worksheet.set_row(row_num, None, formats["total"])

    # Apply formatting for columns with floats to be formatted as Accounting "£#,##0"
    for col_num, dtype in enumerate(data.dtypes):
        if dtype in ["float64", "float32"]:
            worksheet.set_column(col_num, col_num, None, formats["cost"])

    worksheet.autofit()


def write_worksheet(
    writer: pd.ExcelWriter,
    sheet_name: str,
    data: pd.DataFrame,
    formats: FormatsDict,
    output_file: Path,
):
    """
    Write a worksheet to the Excel file with conditional formatting.

    Parameters
    ----------
    writer : pd.ExcelWriter
        The Excel writer object
    sheet_name : str
        The name of the worksheet
    data : pd.DataFrame
        The data to write to the worksheet
    formats : dict
        The formats to apply to the worksheet
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

    # Format datetime columns to %d-%m-%Y
    for col in data.select_dtypes(include=["datetime"]).columns:
        data[col] = data[col].dt.strftime("%d-%m-%Y")

    data.to_excel(
        excel_writer=writer,
        sheet_name=sheet_name,
        index=False,
        startrow=1,
        header=False,
    )

    apply_excel_formatting(
        writer=writer,
        data=data,
        formats=formats,
        sheet_name=sheet_name,
    )

    logger.debug(f"Worksheet {sheet_name} written to the Excel file: {output_file}")
