"""
This module contains the configuration for the devices RAP project.
It includes setup for logging, directory creation, and dataset paths.
It also provides a Config class to manage dataset configurations and paths.
"""

import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import List, Literal

import yaml
from loguru import logger
from nhs_herbot.errors import LoggedException, LoggedWarning, PathNotFoundError
from tqdm import tqdm

from devices_rap.constants import (
    AMBER_REPORT_EXCEL_CONFIG_PATH,
    DEVICE_TAXONOMY_CSV_NAME,
    EXCEPTIONS_CSV_NAME,
    MASTER_DEVICES_CSV_NAME,
    PROCESSED_DATA_DIR,
    PROJ_ROOT,
    PROVIDER_CODES_LOOKUP_CSV_NAME,
    RAW_DATA_DIR,
)

if sys.version_info < (3, 11):
    from exceptiongroup import ExceptionGroup  # type: ignore


FinMonths = Literal["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
FinYears = Literal["2425", "2526", "2627", "2728", "2829", "2930", "3031", "3132"]
OutputFormats = Literal["excel", "pickle", "csv", "sql", "excel_zip"]
PipelineOutputs = OutputFormats | List[OutputFormats]


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
        outputs: PipelineOutputs = "excel",
        raw_data_dir: Path = RAW_DATA_DIR,
        processed_data_dir: Path = PROCESSED_DATA_DIR,
        amber_report_excel_config_path: Path = AMBER_REPORT_EXCEL_CONFIG_PATH,
        master_devices_csv_name: str = MASTER_DEVICES_CSV_NAME,
        exceptions_csv_name: str = EXCEPTIONS_CSV_NAME,
        provider_codes_lookup_csv_name: str = PROVIDER_CODES_LOOKUP_CSV_NAME,
        device_taxonomy_csv_name: str = DEVICE_TAXONOMY_CSV_NAME,
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
        self.outputs = outputs
        self.raw_data_dir = raw_data_dir
        self.processed_data_dir = processed_data_dir
        self.amber_report_excel_config_path = amber_report_excel_config_path
        self.master_devices_csv_name = master_devices_csv_name
        self.exceptions_csv_name = exceptions_csv_name
        self.provider_codes_lookup_csv_name = provider_codes_lookup_csv_name
        self.device_taxonomy_csv_name = device_taxonomy_csv_name

        self.output_directory = self.processed_data_dir / self.fin_year / self.fin_month

        self._define_dataset_paths()
        self._load_amber_report_excel_config()

        logger.success("Pipeline configuration loaded successfully.")

    def _define_dataset_paths(self):
        """
        Defines the paths for the datasets used in the project based on the month and year strings.
        It constructs paths for the master devices CSV, exceptions CSV, provider codes lookup CSV,
        and device taxonomy CSV files. It also checks if these paths exist and raises an exception
        if any of the paths do not exist. Builds the dataset configuration dictionary to be used
        when loading the datasets.
        """
        year_data_dir = self.raw_data_dir / self.fin_year
        month_data_dir = year_data_dir / self.fin_month

        self.master_devices_path = month_data_dir / self.master_devices_csv_name
        self.exceptions_path = month_data_dir / self.exceptions_csv_name
        self.provider_codes_lookup_path = self.raw_data_dir / self.provider_codes_lookup_csv_name
        self.device_taxonomy_path = year_data_dir / self.device_taxonomy_csv_name

        paths_to_check = [
            self.master_devices_path,
            self.exceptions_path,
            self.provider_codes_lookup_path,
            self.device_taxonomy_path,
        ]

        self._check_paths(paths_to_check)

        # Dataset configuration
        self.dataset_config = {
            "master_devices": {
                "filepath_or_buffer": self.master_devices_path,
                "low_memory": False,
            },
            "device_taxonomy": {"filepath_or_buffer": self.device_taxonomy_path},
            "exceptions": {"filepath_or_buffer": self.exceptions_path},
            "provider_codes_lookup": {
                "filepath_or_buffer": self.provider_codes_lookup_path,
            },
        }
        logger.debug(f"Using the following datasets configuration: {self.dataset_config}")

    @staticmethod
    def _check_paths(paths_to_check: List[Path] | Path):
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

    def _load_amber_report_excel_config(self):
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

        print(amber_excel_config_path)

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
