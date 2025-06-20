"""
Functionality that handle the output of processed data from the pipeline.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Literal

import pandas as pd
import tqdm
from loguru import logger

from devices_rap.config import Config

FormatsDict = Dict[Literal["header", "total", "default", "cost"], object]


def output_data(
    output_workbooks: Dict[str, Dict[str, pd.DataFrame]],
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

    if "excel" in outputs:
        use_multiprocessing = pipeline_config.use_multiprocessing
        create_excel_reports(
            output_workbooks=output_workbooks,
            output_directory=output_directory,
            use_multiprocessing=use_multiprocessing,
        )
    if "pickle" in outputs:
        fin_month = pipeline_config.fin_month
        fin_year = pipeline_config.fin_year
        create_pickle(
            output_workbooks=output_workbooks,
            output_directory=output_directory,
            fin_month=fin_month,
            fin_year=fin_year,
        )
    if "sql" in outputs:
        logger.warning("SQL output is not implemented yet. Skipping SQL output.")


def create_excel_reports(
    output_workbooks: Dict[str, Dict[str, pd.DataFrame]],
    output_directory: Path,
    use_multiprocessing: bool,
):
    """
    Create the Excel reports based on the processed data. The function will create an Excel file for
    each region containing the processed worksheets for that region.

    Parameters
    ----------
    output_workbooks : dict
        The processed data for each region
    output_directory : Path
        The path to save the Excel reports to
    use_multiprocessing : bool
        Whether to use multiprocessing for writing the Excel files.

    Returns
    -------
    None
    """
    logger.info("Creating excel reports")

    if use_multiprocessing:
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(
                    process_region,
                    output_directory=output_directory,
                    region=region,
                    worksheets=worksheets,
                    use_multiprocessing=use_multiprocessing,
                )
                for region, worksheets in output_workbooks.items()
            ]
            for future in tqdm.tqdm(as_completed(futures), total=len(futures), position=0):
                future.result()
    else:
        for region, worksheets in output_workbooks.items():
            process_region(
                output_directory=output_directory,
                region=region,
                worksheets=worksheets,
                use_multiprocessing=use_multiprocessing,
            )

    logger.success("Excel reports created successfully.")


def process_region(
    output_directory: Path,
    region: str,
    worksheets: Dict[str, pd.DataFrame],
    use_multiprocessing: bool,
):
    """
    Process the data for a region and create the Excel report.

    Parameters
    ----------
    output_directory : Path
        The path to save the Excel reports to
    region : str
        The region to process
    worksheets : dict
        The processed data for the region
    use_multiprocessing : bool
        Whether to use multiprocessing for writing the Excel file

    Returns
    -------
    None
    """
    output_file = output_directory / f"{region.upper().replace(' ', '_')}_RAG_STATUS_REPORT.xlsx"

    if output_file.exists():
        logger.warning(f"Overwriting the existing Excel file: {output_file}")
        output_file.unlink()
    else:
        logger.info(f"Creating Excel report for {region}")

    create_excel_file(
        output_file=output_file, worksheets=worksheets, use_multiprocessing=use_multiprocessing
    )

    logger.success(f"Excel report for {region} created successfully.")


def create_excel_file(output_file: Path, worksheets: Dict[str, pd.DataFrame], use_multiprocessing):
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

        if use_multiprocessing:
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


def create_pickle(
    output_workbooks: Dict[str, Dict[str, pd.DataFrame]],
    output_directory: Path,
    fin_month: str,
    fin_year: str,
):
    """
    Create pickle files for each region containing the processed data.

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
