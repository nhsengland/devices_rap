"""
_summary_
"""

import typer
from loguru import logger
from tqdm import tqdm

app = typer.Typer()


@app.command()
def amber_report_pipeline():
    """
    Pipeline to create the monthly Amber Reports
    """
    # ---- REPLACE THIS WITH YOUR OWN CODE ----
    logger.info("Starting the Devices Pipeline")
    for i in tqdm(range(10), total=10):
        if i == 5:
            logger.info("Something happened for iteration 5.")

    logger.success("Pipeline complete.")


if __name__ == "__main__":
    app()
