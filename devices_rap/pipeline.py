"""
Main pipeline functions for the Devices RAP report. The pipeline is responsible for processing the
raw data and creating the final reports.
"""

from loguru import logger

from devices_rap.clean_data import (
    batch_normalise_column_names,
    cleanse_exceptions,
    cleanse_master_data,
    cleanse_master_joined_dataset,
)
from devices_rap.config import AMBER_OUTPUT_INSTRUCTIONS, DATASETS
from devices_rap.create_cuts import create_regional_table_cuts
from devices_rap.data_in.load_csv import load_devices_datasets
from devices_rap.data_out import create_excel_reports
from devices_rap.interpret_output_instructions import interpret_output_instructions
from devices_rap.joins import (
    join_device_taxonomy,
    join_exceptions,
    join_mini_tables,
    join_provider_codes_lookup,
)
from devices_rap.summary_tables import (
    create_device_category_summary_table,
    create_device_summary_table,
)
from devices_rap.utils import calc_change_from_previous_month_column, timeit


@timeit
def amber_report_pipeline():
    """
    Pipeline to create the monthly Amber Device Reports for all Regions.

    The pipeline will:
    - Load the raw data
    - Cleanse the data by normalising column names and converting values in the master dataset
    - Join the datasets together to create the master devices dataset
    - Create the summary and detailed tables for the device report
    - Create the regional tables for each region from the summary, detailed and master datasets
    - Create the Excel reports for each region based on the regional tables and output instructions
    """
    logger.info("Starting the Devices Pipeline")

    datasets = load_devices_datasets(DATASETS)

    normalised_datasets = batch_normalise_column_names(datasets)

    master_devices = normalised_datasets["master_devices"]["data"].pipe(cleanse_master_data)

    provider_codes_lookup = normalised_datasets["provider_codes_lookup"]["data"]
    device_taxonomy = normalised_datasets["device_taxonomy"]["data"]
    exceptions = normalised_datasets["exceptions"]["data"].pipe(cleanse_exceptions)

    master_provider_devices = join_provider_codes_lookup(master_devices, provider_codes_lookup)

    master_provider_devices_taxonomy = join_device_taxonomy(
        master_provider_devices, device_taxonomy
    )

    master_provider_devices_taxonomy_exceptions = join_exceptions(
        master_provider_devices_taxonomy, exceptions
    )

    master_devices_table = cleanse_master_joined_dataset(
        master_provider_devices_taxonomy_exceptions
    )

    summary_data = create_device_category_summary_table(
        master_devices_data=master_devices_table,
    )
    detailed_data = create_device_summary_table(
        master_devices_data=master_devices_table,
    )

    summary_data = summary_data.pipe(calc_change_from_previous_month_column).pipe(
        join_mini_tables,
        provider_codes_lookup=provider_codes_lookup,
        device_taxonomy=device_taxonomy,
        exceptions=exceptions,
        include_exception_notes=True,
    )

    detailed_data = detailed_data.pipe(
        join_mini_tables,
        provider_codes_lookup=provider_codes_lookup,
        device_taxonomy=device_taxonomy,
        exceptions=exceptions,
        include_exception_notes=False,
    )

    master_devices_no_missing_regions = master_devices_table.dropna(subset=["upd_region"])

    uncut_datasets = {
        "summary": summary_data,
        "detailed": detailed_data,
        "data": master_devices_no_missing_regions,
    }
    regional_table_cuts = create_regional_table_cuts(tables=uncut_datasets)

    output_workbooks = interpret_output_instructions(
        instructions=AMBER_OUTPUT_INSTRUCTIONS, region_cuts=regional_table_cuts
    )

    create_excel_reports(output_workbooks=output_workbooks)

    logger.success("Pipeline complete.")


if __name__ == "__main__":
    amber_report_pipeline()
