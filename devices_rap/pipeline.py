"""
Main pipeline functions for the Devices RAP report. The pipeline is responsible for processing the
raw data and creating the final reports.
"""

from loguru import logger
from nhs_herbot.utils import timeit

from devices_rap.clean_data import (
    batch_normalise_column_names,
    cleanse_device_taxonomy,
    cleanse_exceptions,
    cleanse_master_data,
    cleanse_master_joined_dataset,
)
from devices_rap.config import Config, FinMonths, FinYears, PipelineOutputs
from devices_rap.create_cuts import create_regional_table_cuts
from devices_rap.data_in.load_csv import load_devices_datasets
from devices_rap.data_out import output_data
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


@timeit
def amber_report_pipeline(
    fin_month: FinMonths, fin_year: FinYears, outputs: PipelineOutputs = "excel", **config_kwargs
) -> None:
    """
    Pipeline to create the monthly Amber Device Reports for all Regions.

    The pipeline will:

    * Check the required paths exist
    * Load the raw data
    * Cleanse the data by normalising column names and converting values in the master dataset
    * Join the datasets together to create the master devices dataset
    * Create the summary and detailed tables for the device report
    * Create the regional tables for each region from the summary, detailed and master datasets
    * Create the Excel reports for each region based on the regional tables and output instructions

    """
    logger.info("Starting the Amber Report Pipeline")

    # Load the pipeline configuration
    pipeline_config = Config(
        fin_month=fin_month,
        fin_year=fin_year,
        outputs=outputs,
        **config_kwargs,
    )

    datasets = load_devices_datasets(pipeline_config=pipeline_config)

    normalised_datasets = batch_normalise_column_names(datasets)

    master_devices = normalised_datasets["master_devices"]["data"].pipe(cleanse_master_data)

    provider_codes_lookup = normalised_datasets["provider_codes_lookup"]["data"]
    device_taxonomy = normalised_datasets["device_taxonomy"]["data"].pipe(cleanse_device_taxonomy)
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
    ).pipe(
        join_mini_tables,
        provider_codes_lookup=provider_codes_lookup,
        device_taxonomy=device_taxonomy,
        exceptions=exceptions,
        include_exception_notes=True,
    )

    detailed_data = create_device_summary_table(
        master_devices_data=master_devices_table,
    ).pipe(
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
        pipeline_config=pipeline_config, region_cuts=regional_table_cuts
    )

    output_data(
        output_workbooks=output_workbooks,
        pipeline_config=pipeline_config,
    )

    logger.success("Pipeline complete.")


if __name__ == "__main__":
    amber_report_pipeline(
        fin_month="02", fin_year="2526", use_multiprocessing=True, outputs=["excel_zip"]
    )
