"""
Main pipeline functions for the Devices RAP report. The pipeline is responsible for processing the
raw data and creating the final reports.
"""

from cyclopts import App
from loguru import logger
from nhs_herbot.utils import timeit

from devices_rap.clean_data import (
    batch_normalise_column_names,
    cleanse_device_taxonomy,
    cleanse_exceptions,
    cleanse_master_data,
    cleanse_master_joined_dataset,
    cleanse_provider_codes_lookup,
)
from devices_rap.config import (
    Config,
    FinMonths,
    FinYears,
    PipelineMode,
    PipelineOutputs,
)
from devices_rap.create_cuts import create_regional_table_cuts
from devices_rap.data_io import load_data, output_data
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

app = App()


@timeit
@app.command()
def amber_report_pipeline(
    fin_month: FinMonths,
    fin_year: FinYears,
    mode: PipelineMode = "local",
    outputs: PipelineOutputs = "pickle",
    **config_kwargs,
) -> None:
    """
    Pipeline to create the monthly Amber Device Reports for all Regions.

    The pipeline will:

    * Configure the pipeline based on the provided financial month & year, mode, and output types.
    * Load the datasets required for the report.
    * Cleanse and normalise the datasets.
    * Join the datasets to create a master dataset of devices.
    * Create summary and detailed tables from the master dataset.
    * Create regional cuts of the data.
    * Interpret the output instructions to generate the final reports.
    * Output the reports in the specified format (e.g., Excel, CSV).

    Parameters
    ----------
    fin_month : FinMonths
        The financial month for which the report is being generated.
    fin_year : FinYears
        The financial year for which the report is being generated.
    mode : PipelineMode, optional
        The mode in which the pipeline is run. Can be "local" or "remote".
        Defaults to "local".
    outputs : PipelineOutputs, optional
        The type of outputs to generate. Can be "excel", "csv", or "excel_zip".
        Defaults to "excel".
    **config_kwargs : dict, optional
        Additional keyword arguments to pass to the Config class for custom configuration.
    """
    logger.info("Starting the Amber Report Pipeline")

    with Config(
        fin_month=fin_month,
        fin_year=fin_year,
        mode=mode,
        outputs=outputs,
        **config_kwargs,
    ) as pipeline_config:
        datasets = load_data(pipeline_config=pipeline_config)

        normalised_datasets = batch_normalise_column_names(datasets)

        master_devices = normalised_datasets["master_devices"]["data"].pipe(cleanse_master_data)

        provider_codes_lookup = normalised_datasets["provider_codes_lookup"]["data"].pipe(
            cleanse_provider_codes_lookup
        )
        device_taxonomy = normalised_datasets["device_taxonomy"]["data"].pipe(
            cleanse_device_taxonomy
        )
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


@app.command()
def null_report_pipeline() -> None:
    """
    Pipeline to create the NULL report. This pipeline currently does nothing and serves as a placeholder.
    """
    logger.warning("NULL report pipeline is not implemented yet.")


if __name__ == "__main__":
    # app()
    amber_report_pipeline(fin_month="10", fin_year="2526", mode="local", outputs="excel_zip")
