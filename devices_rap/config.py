"""
_summary_
"""

from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

# Load environment variables from .env file if it exists
load_dotenv()

# Paths
PROJ_ROOT = Path(__file__).resolve().parents[1]
logger.info(f"PROJ_ROOT path is: {PROJ_ROOT}")

DATA_DIR = (PROJ_ROOT / "data").relative_to(PROJ_ROOT)
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"

MODELS_DIR = PROJ_ROOT / "models"

REPORTS_DIR = PROJ_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"


MASTER_DEVICES_CSV_NAME = "data_2425_master_m6.csv"
EXCEPTIONS_CSV_NAME = "exception_report_m6.csv"
PROVIDER_CODES_LOOKUP_CSV_NAME = "provider_codes_lookup.csv"
DEVICE_TAXONOMY_CSV_NAME = "device_taxonomy_2425.csv"

DATASETS = {
    "master_devices": {
        "filepath_or_buffer": RAW_DATA_DIR / MASTER_DEVICES_CSV_NAME,
        "low_memory": False,
    },
    "device_taxonomy": {"filepath_or_buffer": EXTERNAL_DATA_DIR / DEVICE_TAXONOMY_CSV_NAME},
    "exceptions": {"filepath_or_buffer": RAW_DATA_DIR / EXCEPTIONS_CSV_NAME},
    "provider_codes_lookup": {
        "filepath_or_buffer": EXTERNAL_DATA_DIR / PROVIDER_CODES_LOOKUP_CSV_NAME
    },
}

# If tqdm is installed, configure loguru with tqdm.write
# https://github.com/Delgan/loguru/issues/135
try:
    from tqdm import tqdm

    logger.remove(0)
    logger.add(lambda msg: tqdm.write(msg, end=""), colorize=True)
except ModuleNotFoundError:
    pass
