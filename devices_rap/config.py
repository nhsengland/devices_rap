"""
Configuration file for the project.
"""

import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import yaml
from dotenv import load_dotenv
from loguru import logger
from tqdm import tqdm

from devices_rap.errors import LoggedWarning, PathNotFoundError

if sys.version_info < (3, 11):
    from exceptiongroup import ExceptionGroup  # type: ignore

# Set financial year and month
FIN_YEAR = "2425"
FIN_MONTH = "8"

# Define project root directory
PROJ_ROOT = Path(__file__).resolve().parents[1]

# Configure loguru with tqdm.write https://github.com/Delgan/loguru/issues/135
logger.remove(0)
logger.add(lambda msg: tqdm.write(msg, end=""), colorize=True)

# Set LOG_FILE to False to disable logging to file which is useful during development with automatic
# test discovery turned on in an IDE like VSCode. This is because the config file will be executed
# each time you save and the log file will be generated each time.
LOG_FILE = False

log_file_name = datetime.now().strftime("%Y%m%d_%H%M%S.log")
log_file_path = PROJ_ROOT / "logs" / log_file_name

if LOG_FILE:
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    logger.add(log_file_path)
else:
    warnings.warn(
        "Logging to file is disabled. Enable it by setting the `LOG_FILE` variable to True.",
        LoggedWarning,
    )

# Load environment variables from .env file if it exists
load_dotenv()

# Settings
USE_MULTIPROCESSING = True
logger.debug(
    f"Running the pipeline with the following settings: "
    f"FIN_YEAR={FIN_YEAR}, "
    f"FIN_MONTH={FIN_MONTH}, "
    f"USE_MULTIPROCESSING={USE_MULTIPROCESSING}"
)

# RAG Prioritisation
RAG_PRIORITIES = ["AMBER", "RED", "YELLOW"]

# Paths
logger.debug(f"PROJ_ROOT path is: {PROJ_ROOT}")

DATA_DIR = PROJ_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"

MODELS_DIR = PROJ_ROOT / "models"

REPORTS_DIR = PROJ_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

# Financial year and month specific directories
YEAR_DATA_DIR = RAW_DATA_DIR / FIN_YEAR
MONTH_DATA_DIR = YEAR_DATA_DIR / FIN_MONTH

# File names
AMBER_REPORT_EXCEL_CONFIG_NAME = "amber_report_excel_config.yaml"
MASTER_DEVICES_CSV_NAME = "master_data.csv"
EXCEPTIONS_CSV_NAME = "exception_report.csv"
PROVIDER_CODES_LOOKUP_CSV_NAME = "provider_codes_lookup.csv"
DEVICE_TAXONOMY_CSV_NAME = "device_taxonomy.csv"

# Config paths
AMBER_REPORT_EXCEL_CONFIG_PATH = PROJ_ROOT / "amber_report_excel_config.yaml"

# Dataset paths
MASTER_DEVICES_PATH = MONTH_DATA_DIR / MASTER_DEVICES_CSV_NAME
EXCEPTIONS_PATH = MONTH_DATA_DIR / EXCEPTIONS_CSV_NAME
PROVIDER_CODES_LOOKUP_PATH = RAW_DATA_DIR / PROVIDER_CODES_LOOKUP_CSV_NAME
DEVICE_TAXONOMY_PATH = YEAR_DATA_DIR / DEVICE_TAXONOMY_CSV_NAME

# Dataset configuration
DATASETS = {
    "master_devices": {
        "filepath_or_buffer": MASTER_DEVICES_PATH,
        "low_memory": False,
    },
    "device_taxonomy": {"filepath_or_buffer": DEVICE_TAXONOMY_PATH},
    "exceptions": {"filepath_or_buffer": EXCEPTIONS_PATH},
    "provider_codes_lookup": {
        "filepath_or_buffer": PROVIDER_CODES_LOOKUP_PATH,
    },
}
logger.debug(f"Using the following datasets configuration: {DATASETS}")

# Create directories if they do not exist - this should only be done for output directories
paths_to_create = [
    # INTERIM_DATA_DIR,
    PROCESSED_DATA_DIR,
    # MODELS_DIR,
    # REPORTS_DIR,
    # FIGURES_DIR,
]
for dir_path in tqdm(paths_to_create):
    logger.debug("Ensuring the following directory is created if not already:{}", dir_path)
    dir_path.mkdir(parents=True, exist_ok=True)


def check_paths(paths_to_check: Optional[List[Path]] = None):
    """
    Checks if the specified paths exist. If any of the paths do not exist, an exception is raised.

    Parameters
    ----------
    paths_to_check : Optional[List[Path]], optional
        A list of paths to check. If not provided, a default list of paths will be used.

    Raises
    ------
    ExceptionGroup[PathNotFoundError]
        If any of the paths do not exist, an exception is raised containing all the missing paths.
    """

    # Check paths
    logger.debug("Checking if the required paths exist")
    paths_to_check = paths_to_check or [
        RAW_DATA_DIR,
        # INTERIM_DATA_DIR,
        PROCESSED_DATA_DIR,
        EXTERNAL_DATA_DIR,
        # MODELS_DIR,
        # REPORTS_DIR,
        # FIGURES_DIR,
        AMBER_REPORT_EXCEL_CONFIG_PATH,
        YEAR_DATA_DIR,
        MONTH_DATA_DIR,
        MASTER_DEVICES_PATH,
        EXCEPTIONS_PATH,
        PROVIDER_CODES_LOOKUP_PATH,
        DEVICE_TAXONOMY_PATH,
    ]

    path_not_found_errors = []
    for path in tqdm(paths_to_check):
        logger.debug("Checking if the path exists: {}", path)
        if not path.exists():
            path_not_found_errors.append(PathNotFoundError(path))

    if path_not_found_errors:
        raise ExceptionGroup(
            "Config paths were not found. Please ensure that the paths exists before running the pipeline.",
            path_not_found_errors,
        )


# Load Amber Report Excel configuration
with open(AMBER_REPORT_EXCEL_CONFIG_PATH, "r", encoding="UTF8") as file:
    logger.debug(
        "Loading the Amber Report Excel configuration from: {}", AMBER_REPORT_EXCEL_CONFIG_PATH
    )
    AMBER_REPORT_EXCEL_CONFIG = yaml.safe_load(file)
    AMBER_OUTPUT_INSTRUCTIONS = AMBER_REPORT_EXCEL_CONFIG["WORKSHEET_CONFIG"]
    logger.debug(
        "Loaded the Amber Report Excel instructions successfully: {}",
        AMBER_OUTPUT_INSTRUCTIONS,
    )

logger.success("Configuration loaded successfully.")
