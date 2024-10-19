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
)
from devices_rap.data_in.load_data import load_provider_codes_lookup
from devices_rap.data_in.load_exceptions_data import load_exceptions_data
from devices_rap.data_in.load_master_data import load_master_data
from devices_rap.data_out import create_excel_reports
from devices_rap.processing import (
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
    # ---- REPLACE THIS WITH YOUR OWN CODE ----
    logger.info("Starting the Devices Pipeline")

    load_provider_codes_lookup()
    load_exceptions_data()
    load_master_data()

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
