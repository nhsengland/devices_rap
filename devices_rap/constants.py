"""
Configuration file for the project.
"""

from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# RAG Prioritisation
RAG_PRIORITIES = ["AMBER", "RED", "YELLOW"]

# Define project root directory
PROJ_ROOT = Path(__file__).resolve().parents[1]

# Paths
DATA_DIR = PROJ_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SQL_DIR = PROJ_ROOT / "sql"

MODELS_DIR = PROJ_ROOT / "models"

REPORTS_DIR = PROJ_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

# File names
AMBER_REPORT_EXCEL_CONFIG_NAME = "amber_report_excel_config.yaml"
MASTER_DEVICES_CSV_NAME = "master_data.csv"
EXCEPTIONS_CSV_NAME = "exception_report.csv"
PROVIDER_CODES_LOOKUP_CSV_NAME = "provider_codes_lookup.csv"
DEVICE_TAXONOMY_CSV_NAME = "device_taxonomy.csv"

# SQL file names
MASTER_DEVICES_SQL_NAME = "query_devices_reporting_amber.sql"
PROVIDER_CODES_LOOKUP_SQL_NAME = "query_provider_codes_lookup.sql"

# Config paths
AMBER_REPORT_EXCEL_CONFIG_PATH = PROJ_ROOT / "amber_report_excel_config.yaml"
