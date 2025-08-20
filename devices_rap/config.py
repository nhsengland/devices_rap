"""
This module contains the configuration for the devices RAP project.
It includes setup for logging, directory creation, and dataset paths.
It also provides a Config class to manage dataset configurations and paths.
"""

import os
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Literal

import yaml
from loguru import logger
from nhs_herbot import LoggedException, LoggedWarning, PathNotFoundError, SQLServer
from tqdm import tqdm

from devices_rap.constants import (
    AMBER_REPORT_EXCEL_CONFIG_PATH,
    DEVICE_TAXONOMY_CSV_NAME,
    EXCEPTIONS_CSV_NAME,
    MASTER_DEVICES_CSV_NAME,
    MASTER_DEVICES_SQL_NAME,
    PROCESSED_DATA_DIR,
    PROJ_ROOT,
    PROVIDER_CODES_LOOKUP_CSV_NAME,
    PROVIDER_CODES_LOOKUP_SQL_NAME,
    RAW_DATA_DIR,
    SQL_DIR,
)

if sys.version_info < (3, 11):
    from exceptiongroup import ExceptionGroup  # type: ignore

FinMonths = Literal["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
FinYears = Literal["2425", "2526", "2627", "2728", "2829", "2930", "3031", "3132"]

OutputFormats = Literal["excel", "pickle", "csv", "sql", "excel_zip"]
PipelineOutputs = OutputFormats | List[OutputFormats]

PipelineMode = Literal["local", "remote"]


class ConfigError(LoggedException):
    """
    Custom exception class for configuration errors.
    This class is used to raise exceptions related to configuration issues.
    """


def config_logger():
    """
    Set up logging configuration for the project using loguru.
    This function configures loguru to log messages to both the console and a file.
    It also ensures that the log file is created in the 'logs' directory with a timestamped filename.
    """
    logger.remove(0)
    logger.add(lambda msg: tqdm.write(msg, end=""), colorize=True)

    log_file_name = datetime.now().strftime("%Y%m%d_%H%M%S.log")
    log_file_path = PROJ_ROOT / "logs" / log_file_name

    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    logger.add(log_file_path)


def create_directory(directory_path: Path | List[Path]):
    """
    Creates directories if they do not already exist.

    Parameters
    ----------
    directory_paths : Path | List[Path]
        A single Path object or a list of Path objects representing the directories to be created.

    Raises
    ------
    ValueError
        If the provided directory_path list is empty, a warning is logged and the function returns
        without creating any directories.
    """
    if not directory_path:
        warnings.warn(
            "No directory paths provided. No directories will be created.",
            LoggedWarning,
        )

    if isinstance(directory_path, Path):
        directory_path = [directory_path]

    for dir_path in directory_path:
        logger.debug("Ensuring the following directory is created if not already: {}", dir_path)
        dir_path.mkdir(parents=True, exist_ok=True)


class Config:
    """
    Configuration class for the project.
    """

    def __init__(
        self,
        fin_month: FinMonths,
        fin_year: FinYears,
        use_multiprocessing: bool = True,
        mode: PipelineMode = "local",
        outputs: PipelineOutputs = "excel",
        raw_data_dir: Path = RAW_DATA_DIR,
        processed_data_dir: Path = PROCESSED_DATA_DIR,
        amber_report_excel_config_path: Path = AMBER_REPORT_EXCEL_CONFIG_PATH,
        master_devices_csv_name: str = MASTER_DEVICES_CSV_NAME,
        exceptions_csv_name: str = EXCEPTIONS_CSV_NAME,
        provider_codes_lookup_csv_name: str = PROVIDER_CODES_LOOKUP_CSV_NAME,
        device_taxonomy_csv_name: str = DEVICE_TAXONOMY_CSV_NAME,
        sql_dir: Path = SQL_DIR,
        master_device_sql_name: str = MASTER_DEVICES_SQL_NAME,
        provider_codes_lookup_sql_name: str = PROVIDER_CODES_LOOKUP_SQL_NAME,
    ):
        """
        Initializes the Config class with the provided parameters.

        Parameters
        ----------
        fin_month : FIN_MONTHS
            The financial month string in the format "MM" (e.g., "12") with 01 referring to April.
        fin_year : FIN_YEARS
            The financial year string in the format "YY1YY2" (e.g., "2425").
        raw_data_dir : Path, optional
            The directory where raw data is stored. Defaults to the RAW_DATA_DIR constant.
        amber_report_excel_config_path : Path, optional
            The path to the Amber Report Excel configuration file. Defaults to the AMBER_REPORT_EXCEL_CONFIG_PATH constant.
        master_devices_csv_name : str, optional
            The name of the master devices CSV file. Defaults to the MASTER_DEVICES_CSV_NAME constant.
        exceptions_csv_name : str, optional
            The name of the exceptions CSV file. Defaults to the EXCEPTIONS_CSV_NAME constant.
        provider_codes_lookup_csv_name : str, optional
            The name of the provider codes lookup CSV file. Defaults to the PROVIDER_CODES_LOOKUP_CSV_NAME constant.
        device_taxonomy_csv_name : str, optional
            The name of the device taxonomy CSV file. Defaults to the DEVICE_TAXONOMY_CSV_NAME constant.

        """
        logger.info("Loading pipeline configuration...")
        self.fin_month = fin_month
        self.fin_year = fin_year
        self.use_multiprocessing = use_multiprocessing
        self.mode = mode
        self.outputs = outputs if isinstance(outputs, list) else [outputs]
        self.raw_data_dir = raw_data_dir
        self.processed_data_dir = processed_data_dir
        self.amber_report_excel_config_path = amber_report_excel_config_path
        self.master_devices_csv_name = master_devices_csv_name
        self.exceptions_csv_name = exceptions_csv_name
        self.provider_codes_lookup_csv_name = provider_codes_lookup_csv_name
        self.device_taxonomy_csv_name = device_taxonomy_csv_name
        self.sql_dir = sql_dir
        self.master_devices_sql_name = master_device_sql_name
        self.provider_codes_lookup_sql_name = provider_codes_lookup_sql_name

        self.output_directory = self.processed_data_dir / self.fin_year / self.fin_month

        self._define_dataset_config()
        self._load_amber_report_excel_config()

        self.sql_server = None
        if mode == "remote":
            self._connect_to_sql_server()
            assert isinstance(self.sql_server, SQLServer), "SQL Server connection failed."

        logger.success("Pipeline configuration loaded successfully.")

    def close(self) -> None:
        """
        Closes the SQL Server connection if it exists.
        This method is called to clean up resources when the Config instance is no longer needed.
        """
        if self.mode == "remote" and self.sql_server:
            self.sql_server.close()
            logger.info("SQL Server connection closed.")
        elif self.mode == "remote":
            logger.warning("No SQL Server connection to close.")

    def __enter__(self):
        """
        Enter the runtime context related to this object.
        This method is called when the Config instance is used in a 'with' statement.
        It returns the Config instance itself.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the runtime context related to this object.
        This method is called when the 'with' statement is exited.
        It calls the close method to clean up resources.
        """
        self.close()
        if exc_type is not None:
            logger.critical("An error occurred: {}", exc_value)

    def get(self, key: str):
        """
        Get the value of a configuration key.

        Parameters
        ----------
        key : str
            The key for which to retrieve the value.

        Returns
        -------
        Any
            The value associated with the key, or None if the key does not exist.
        """
        return getattr(self, key, None)

    def _define_dataset_config(self) -> None:
        """
        Configure dataset paths and loading parameters based on operating mode.

        Constructs file paths for all required datasets using the configured financial
        year and month. In local mode, uses CSV files from the filesystem. In remote
        mode, uses SQL queries for master devices and provider codes lookup while
        maintaining CSV files for exceptions and device taxonomy.

        The method performs the following operations:
        1. Builds appropriate file/query paths based on the current mode
        2. Validates that all required paths exist
        3. Creates a dataset configuration dictionary with loading parameters
        4. In remote mode, loads SQL replacement values from environment variables

        Notes
        -----
        In remote mode, master_devices and provider_codes_lookup use SQL
        queries while exceptions and device_taxonomy remain as CSV files.
        """

        year_data_dir = self.raw_data_dir / self.fin_year
        month_data_dir = year_data_dir / self.fin_month

        # Set up paths based on mode
        if self.mode == "local":
            self.master_devices_path = month_data_dir / self.master_devices_csv_name
            self.provider_codes_lookup_path = (
                self.raw_data_dir / self.provider_codes_lookup_csv_name
            )
            config_key = "filepath_or_buffer"
        else:  # remote mode
            self.master_devices_path = self.sql_dir / self.master_devices_sql_name
            self.provider_codes_lookup_path = self.sql_dir / self.provider_codes_lookup_sql_name
            config_key = "sql_query_path"

        # These are always CSV files regardless of mode
        self.exceptions_path = month_data_dir / self.exceptions_csv_name
        self.device_taxonomy_path = year_data_dir / self.device_taxonomy_csv_name

        # Check all paths exist
        paths_to_check = [
            self.master_devices_path,
            self.exceptions_path,
            self.provider_codes_lookup_path,
            self.device_taxonomy_path,
        ]
        self._check_paths(paths_to_check)

        # Load SQL replacements for remote mode
        sql_replacements = {}
        if self.mode == "remote":
            sql_replacements = self._load_sql_replacements()

        # Build dataset configuration
        self.dataset_config = {
            "master_devices": {
                config_key: self.master_devices_path,
                **({"low_memory": False} if self.mode == "local" else {}),
                **({"replacements": sql_replacements} if self.mode == "remote" else {}),
            },
            "device_taxonomy": {"filepath_or_buffer": self.device_taxonomy_path},
            "exceptions": {"filepath_or_buffer": self.exceptions_path},
            "provider_codes_lookup": {
                config_key: self.provider_codes_lookup_path,
                **({"replacements": sql_replacements} if self.mode == "remote" else {}),
            },
        }

        logger.debug("Dataset configuration loaded successfully")

    def _load_sql_replacements(self) -> Dict[str, str]:
        """
        Load SQL replacement values from environment variables.

        Reads environment variables for SQL query placeholders to obscure
        database details. The replacements are used in SQL queries to substitute
        placeholder values with actual database schema and table names.

        Returns
        -------
        dict
            Dictionary mapping placeholder names to actual values from environment variables.

        Note
        ----
        The environment variables should be defined in the .env file and include:
        - ods_schema_placeholder
        - org_ods_table_placeholder
        - hierarchies_ods_table_placeholder
        - curated_devices_schema_placeholder
        - curated_devices_table_placeholder
        - devices_schema_placeholder
        - devices_table_placeholder
        """
        replacements = {}

        # Define the mapping of placeholder names to environment variable names
        env_mapping = {
            "ods_schema_placeholder": "ods_schema_placeholder",
            "org_ods_table_placeholder": "org_ods_table_placeholder",
            "hierarchies_ods_table_placeholder": "hierarchies_ods_table_placeholder",
            "curated_devices_schema_placeholder": "curated_devices_schema_placeholder",
            "curated_devices_table_placeholder": "curated_devices_table_placeholder",
            "devices_schema_placeholder": "devices_schema_placeholder",
            "devices_table_placeholder": "devices_table_placeholder",
            "report_schema_placeholder": "curated_devices_schema_placeholder",  # Alias for report schema
            "curated_devices_placeholder": "curated_devices_table_placeholder",  # Alias for curated devices
        }

        for placeholder, env_var in env_mapping.items():
            value = os.environ.get(env_var)
            if value:
                replacements[placeholder] = value

        logger.info(f"Loaded {len(replacements)} SQL replacements from environment variables")
        return replacements

    @staticmethod
    def _check_paths(paths_to_check: List[Path] | Path) -> None:
        """
        Checks if the specified paths exist. If any of the paths do not exist, an exception is raised.

        Parameters
        ----------
        paths_to_check : List[Path] | Path
            A single Path object or a list of Path objects representing the paths to be checked.

        Raises
        ------
        ExceptionGroup[PathNotFoundError]
            If any of the paths do not exist, an exception is raised containing all the missing paths.
        """
        path_not_found_errors = []
        if isinstance(paths_to_check, Path):
            paths_to_check = [paths_to_check]
        for path in paths_to_check:
            logger.debug("Checking if the path exists: {}", path)
            if not path.exists():
                path_not_found_errors.append(PathNotFoundError(path))

        if path_not_found_errors:
            raise ExceptionGroup(
                "Config paths were not found. Please ensure that the paths exists before running the pipeline.",
                path_not_found_errors,
            )

    def _load_amber_report_excel_config(self) -> None:
        """
        Load the Amber Report Excel configuration from the specified YAML file.
        This method reads the configuration file, checks for the presence of the 'WORKSHEET_CONFIG'
        key, and validates its structure. If the configuration is valid, it stores it in the
        instance variable `amber_report_excel_config`. If the configuration is invalid, it raises a
        ConfigError with an appropriate message.

        Raises
        ------
        ConfigError
            If the Amber Report Excel configuration file is missing the 'WORKSHEET_CONFIG' key,
            if 'WORKSHEET_CONFIG' is not a dictionary, or if it is empty.
        """
        amber_excel_config_path = self.amber_report_excel_config_path

        self._check_paths(amber_excel_config_path)

        with open(amber_excel_config_path, "r", encoding="UTF8") as file:
            logger.debug(
                "Loading the Amber Report Excel configuration from: {}",
                amber_excel_config_path,
            )
            amber_report_excel_config = yaml.safe_load(file)

            if "WORKSHEET_CONFIG" not in amber_report_excel_config:
                raise ConfigError(
                    "Amber Report Excel configuration file is missing 'WORKSHEET_CONFIG' key."
                )
            if not isinstance(amber_report_excel_config["WORKSHEET_CONFIG"], dict):
                raise ConfigError(
                    "Amber Report Excel configuration 'WORKSHEET_CONFIG' should be a dictionary."
                )
            if not amber_report_excel_config["WORKSHEET_CONFIG"]:
                raise ConfigError("Amber Report Excel configuration 'WORKSHEET_CONFIG' is empty.")

            self.amber_report_output_instructions = amber_report_excel_config["WORKSHEET_CONFIG"]

            logger.debug(
                "Loaded the Amber Report Excel instructions successfully: {}",
                self.amber_report_output_instructions,
            )

    def create_output_directory(self) -> Path:
        """
        Creates the output directory for the Amber Report Excel files based on the financial month
        and year.

        Returns
        -------
        Path
            The path to the created output directory.
        """
        create_directory(self.output_directory)

        logger.debug("Output directory for Amber Report Excel is {}", self.output_directory)

        return self.output_directory

    def _connect_to_sql_server(self) -> None:
        """
        Connects to the SQL Server database using the configuration parameters set in the
        environment variables.

        Raises
        ------
        ConfigError
            If the SQL Server connection parameters (server, uid, database) are not set in the
            environment variables.
        """
        logger.info("Connecting to the SQL Server Database")

        server = os.environ.get("server")
        uid = os.environ.get("uid")
        database = os.environ.get("database")

        if not server or not uid or not database:
            raise ConfigError(
                "SQL Server connection parameters (server, uid, database) must be set "
                "in environment variables."
            )

        self.sql_server = SQLServer(server=server, uid=uid, database=database)
