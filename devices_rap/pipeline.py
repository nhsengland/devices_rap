"""
_summary_
"""

import pandas as pd
import typer
from loguru import logger

from devices_rap.clean_data import (
    cleanse_exceptions_data,
    cleanse_master_data,
    cleanse_provider_data,
    cleanse_taxonomy_data,
)
from devices_rap.config import DATASETS
from devices_rap.data_in.load_csv import load_devices_datasets
from devices_rap.data_out import create_excel_reports
from devices_rap.joins import (
    lookup_provider_codes,
    lookup_taxonomy_tariff,
    translate_high_level_devices_type,
)
from devices_rap.summary_tables import (
    create_device_category_summary_table,
    create_device_summary_table,
    create_rag_summary_tables,
    create_regional_data_cuts,
)

app = typer.Typer()

placeholder_df = pd.DataFrame()


@app.command()
def amber_report_pipeline():
    """
    Pipeline to create the monthly Amber Reports
    """
    logger.info("Starting the Devices Pipeline")

    datasets = load_devices_datasets(DATASETS)

    exceptions_df = datasets["exceptions"]["data"].pipe(cleanse_exceptions_data)
    provider_codes_lookup = datasets["provider_codes_lookup"]["data"].pipe(cleanse_provider_data)
    device_taxonomy = datasets["device_taxonomy"]["data"].pipe(cleanse_taxonomy_data)

    datasets["master_devices"]["data"].pipe(cleanse_master_data).pipe(
        translate_high_level_devices_type
    )

    exceptions_df.head()
    provider_codes_lookup.head()
    device_taxonomy.head()

    cleanse_provider_data()
    cleanse_exceptions_data()
    cleanse_master_data()

    translate_high_level_devices_type(placeholder_df)
    lookup_provider_codes(placeholder_df, placeholder_df)
    lookup_taxonomy_tariff(placeholder_df, placeholder_df)

    create_device_category_summary_table()
    create_device_summary_table()
    create_rag_summary_tables()
    create_regional_data_cuts()

    create_excel_reports()

    logger.success("Pipeline complete.")


if __name__ == "__main__":
    app()
