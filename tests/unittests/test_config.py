"""
Tests for devices_rap.config module.
"""

import sys
from pathlib import Path
from typing import Literal

import pytest
import yaml
from nhs_herbot.errors import LoggedWarning, PathNotFoundError

from devices_rap.config import Config, ConfigError, config_logger, create_directory
from devices_rap.constants import (
    DEVICE_TAXONOMY_CSV_NAME,
    EXCEPTIONS_CSV_NAME,
    MASTER_DEVICES_CSV_NAME,
    PROVIDER_CODES_LOOKUP_CSV_NAME,
)

if sys.version_info < (3, 11):
    from exceptiongroup import ExceptionGroup  # type: ignore


class TestConfigError:
    """
    Tests for ConfigError.
    """

    def test_config_error(self):
        """
        Test that ConfigError can be raised and has the correct message.
        """
        with pytest.raises(ConfigError, match="This is a config error."):
            raise ConfigError("This is a config error.")


class TestConfigLogger:
    """
    Tests for config_logger.
    """

    @pytest.fixture
    def mock_loguru(self, mocker):
        """
        Mock the logger from loguru.
        """
        return mocker.patch("devices_rap.config.logger")

    def test_removes(self, mock_loguru):
        """
        Test that config_logger sets up loguru logger correctly.
        """
        config_logger()
        mock_loguru.remove.assert_called_once_with(0)

    def test_calls_add_twice(self, mock_loguru):
        """
        Test that config_logger calls logger.add twice.
        """
        config_logger()
        assert mock_loguru.add.call_count == 2

    def test_adds_tqdm_write(self, mocker, mock_loguru, tmp_path):
        """
        Test that config_logger adds a tqdm write handler to the logger.
        """
        mocker.patch("devices_rap.config.PROJ_ROOT", tmp_path)

        config_logger()
        # Test that the first call to logger.add is with tqdm.write and colorize=True
        first_call_args = mock_loguru.add.call_args_list[0][0]
        first_call_kwargs = mock_loguru.add.call_args_list[0][1]
        assert callable(first_call_args[0])
        assert first_call_kwargs.get("colorize") is True

    def test_adds_log_file(self, mocker, mock_loguru, tmp_path):
        """
        Test that config_logger adds a log file with a timestamped filename.
        """
        mock_datetime = mocker.patch("devices_rap.config.datetime")
        mock_datetime.now.return_value.strftime.return_value = "20231001_120000.log"

        mocker.patch("devices_rap.config.PROJ_ROOT", tmp_path)

        config_logger()

        mock_log_file_path = mock_loguru.add.call_args_list[1][0][0]
        expected_file_path = tmp_path / "logs" / "20231001_120000.log"

        assert mock_log_file_path == expected_file_path

    def test_creates_logs_directory(self, mocker, tmp_path):
        """
        Test that config_logger creates the logs directory if it does not exist.
        """
        mocker.patch("devices_rap.config.PROJ_ROOT", tmp_path)

        config_logger()

        logs_dir = tmp_path / "logs"
        assert logs_dir.exists()
        assert logs_dir.is_dir()


class TestCreateDirectory:
    """
    Tests for create_directory.
    """

    def test_creates_directory(self, mocker, tmp_path):
        """
        Test that create_directory creates a directory if it does not exist.
        """
        dir_path = tmp_path / "new_dir"
        create_directory(dir_path)

        assert dir_path.exists()
        assert dir_path.is_dir()

    def test_does_not_create_existing_directory(self, mocker, tmp_path):
        """
        Test that create_directory does not raise an error if the directory already exists.
        """
        dir_path = tmp_path / "existing_dir"
        dir_path.mkdir()

        create_directory(dir_path)

        assert dir_path.exists()
        assert dir_path.is_dir()

    def test_creates_multiple_directories(self, mocker, tmp_path):
        """
        Test that create_directory can create multiple directories.
        """
        dir_paths = [tmp_path / "dir1", tmp_path / "dir2"]
        create_directory(dir_paths)

        for dir_path in dir_paths:
            assert dir_path.exists()
            assert dir_path.is_dir()

    def test_warning_on_empty_list(self, mocker):
        """
        Test that create_directory logs a warning if an empty list is provided.
        """
        mock_warn = mocker.patch("devices_rap.config.warnings.warn")
        create_directory([])

        mock_warn.assert_called_once_with(
            "No directory paths provided. No directories will be created.",
            LoggedWarning,
        )

    def test_logger_debug(self, mock_debug, tmp_path):
        """
        Test that logger.debug is called with correct log message when creating directories.
        """
        dir_path = tmp_path / "debug_dir"
        create_directory(dir_path)

        mock_debug.assert_called_once_with(
            "Ensuring the following directory is created if not already: {}",
            dir_path,
        )


class TestConfig:
    """
    Tests for Config class.
    """

    @pytest.fixture
    def mock_define_dataset_config(self, mocker):
        """
        Mock the define_dataset_config method.
        """
        return mocker.patch("devices_rap.config.Config._define_dataset_config")

    @pytest.fixture
    def mock_check_paths(self, mocker):
        """
        Mock the check_paths method.
        """
        return mocker.patch("devices_rap.config.Config._check_paths")

    @pytest.fixture
    def mock_load_amber_report_excel_config(self, mocker):
        """
        Mock the load_amber_report_excel_config method.
        """
        return mocker.patch("devices_rap.config.Config._load_amber_report_excel_config")

    @pytest.fixture
    def mock_create_output_directory(self, mocker):
        """
        Mock the create_output_directory method.
        """
        return mocker.patch("devices_rap.config.Config.create_output_directory")

    @pytest.fixture(autouse=True)
    def mock_amber_report_path(self, mocker, tmp_path):
        """
        Mock the AMBER_REPORT_EXCEL_CONFIG_PATH to point to a temporary path.
        """
        AMBER_REPORT_EXCEL_CONFIG_PATH = tmp_path / "test_amber_path"
        mocker.patch(
            "devices_rap.constants.AMBER_REPORT_EXCEL_CONFIG_PATH", AMBER_REPORT_EXCEL_CONFIG_PATH
        )
        return AMBER_REPORT_EXCEL_CONFIG_PATH

    @pytest.fixture(autouse=True)
    def mock_processed_path(self, mocker, tmp_path):
        """
        Mock the PROCESSED_DATA_DIR to point to a temporary path.
        """
        PROCESSED_DATA_DIR = tmp_path / "test_processed_data"
        mocker.patch("devices_rap.constants.PROCESSED_DATA_DIR", PROCESSED_DATA_DIR)
        return PROCESSED_DATA_DIR

    @pytest.fixture(autouse=True)
    def mock_raw_path(self, mocker, tmp_path):
        """
        Mock the RAW_DATA_DIR to point to a temporary path.
        """
        RAW_DATA_DIR = tmp_path / "test_raw_path"
        mocker.patch("devices_rap.config.RAW_DATA_DIR", RAW_DATA_DIR)
        return RAW_DATA_DIR

    def test_init_calls_define_dataset_paths(
        self,
        mock_define_dataset_config,
        mock_check_paths,
        mock_load_amber_report_excel_config,
        mock_create_output_directory,
    ):
        """
        Test that Config.__init__ calls the necessary methods.
        """
        Config(fin_month="01", fin_year="2425")

        mock_define_dataset_config.assert_called_once()

    def test_init_calls_load_amber_report_excel_config(
        self,
        mock_define_dataset_config,
        mock_check_paths,
        mock_load_amber_report_excel_config,
        mock_create_output_directory,
    ):
        """
        Test that Config.__init__ calls the necessary methods.
        """
        Config(fin_month="01", fin_year="2425")

        mock_load_amber_report_excel_config.assert_called_once()

    @pytest.mark.parametrize(
        "level, expected",
        [
            ("info", "Loading pipeline configuration..."),
            ("success", "Pipeline configuration loaded successfully."),
        ],
    )
    def test_init_calls_logger(
        self,
        mock_define_dataset_config,
        mock_check_paths,
        mock_load_amber_report_excel_config,
        mock_create_output_directory,
        mock_log_levels,
        level,
        expected,
    ):
        """
        Test that Config.__init__ calls the logger setup.
        """
        Config(fin_month="01", fin_year="2425")

        mock_log_levels[level].assert_called_once_with(expected)

    @pytest.mark.parametrize(
        "kwargs_dict, expected_values",
        [
            (
                {"fin_month": "test", "fin_year": "test"},
                {
                    "fin_month": "test",
                    "fin_year": "test",
                    "use_multiprocessing": True,
                    "raw_data_dir": None,
                    "amber_report_excel_config_path": None,
                    "master_devices_csv_name": MASTER_DEVICES_CSV_NAME,
                    "exceptions_csv_name": EXCEPTIONS_CSV_NAME,
                    "provider_codes_lookup_csv_name": PROVIDER_CODES_LOOKUP_CSV_NAME,
                    "device_taxonomy_csv_name": DEVICE_TAXONOMY_CSV_NAME,
                },
            ),
            (
                {
                    "fin_month": "02",
                    "fin_year": "2526",
                    "use_multiprocessing": False,
                    "raw_data_dir": "custom_raw_path",
                    "amber_report_excel_config_path": "custom_amber_path",
                    "master_devices_csv_name": "custom_master_devices.csv",
                    "exceptions_csv_name": "custom_exceptions.csv",
                    "provider_codes_lookup_csv_name": "custom_provider_codes.csv",
                    "device_taxonomy_csv_name": "custom_device_taxonomy.csv",
                },
                {
                    "fin_month": "02",
                    "fin_year": "2526",
                    "use_multiprocessing": False,
                    "raw_data_dir": "custom_raw_path",
                    "amber_report_excel_config_path": "custom_amber_path",
                    "master_devices_csv_name": "custom_master_devices.csv",
                    "exceptions_csv_name": "custom_exceptions.csv",
                    "provider_codes_lookup_csv_name": "custom_provider_codes.csv",
                    "device_taxonomy_csv_name": "custom_device_taxonomy.csv",
                },
            ),
        ],
    )
    @pytest.mark.parametrize(
        "property_name",
        [
            "fin_month",
            "fin_year",
            "use_multiprocessing",
            "raw_data_dir",
            "amber_report_excel_config_path",
            "master_devices_csv_name",
            "exceptions_csv_name",
            "provider_codes_lookup_csv_name",
            "device_taxonomy_csv_name",
        ],
    )
    def test_init_sets_properties(
        self,
        mock_define_dataset_config,
        mock_check_paths,
        mock_load_amber_report_excel_config,
        mock_create_output_directory,
        mock_amber_report_path,
        mock_processed_path,
        mock_raw_path,
        kwargs_dict,
        expected_values,
        property_name,
    ):
        """
        Test that Config.__init__ sets the properties correctly.
        """
        config = Config(**kwargs_dict)

        if property_name == "amber_report_excel_config_path":
            expected_values[property_name] = mock_amber_report_path
        elif property_name == "raw_data_dir":
            expected_values[property_name] = mock_raw_path
        else:
            assert getattr(config, property_name) == expected_values[property_name]

    class TestDefineDatasetPaths:
        """
        Tests for Config._define_dataset_paths method.
        """

        @pytest.mark.parametrize(
            "property_name",
            [
                "master_devices_path",
                "exceptions_path",
                "provider_codes_lookup_path",
                "device_taxonomy_path",
            ],
        )
        def test_properties_set(
            self,
            mock_check_paths,
            mock_load_amber_report_excel_config,
            mock_create_output_directory,
            mock_amber_report_path,
            mock_processed_path,
            mock_raw_path,
            property_name,
        ):
            """
            Test that _define_dataset_paths sets the properties correctly.
            """
            config = Config(fin_month="01", fin_year="2425")

            assert hasattr(config, property_name)
            assert getattr(config, property_name) is not None

        @pytest.mark.parametrize(
            "property_name, expected_path_tuple",
            [
                ("master_devices_path", ("year", "month", MASTER_DEVICES_CSV_NAME)),
                ("exceptions_path", ("year", "month", EXCEPTIONS_CSV_NAME)),
                ("provider_codes_lookup_path", (PROVIDER_CODES_LOOKUP_CSV_NAME,)),
                ("device_taxonomy_path", ("year", DEVICE_TAXONOMY_CSV_NAME)),
            ],
        )
        def test_path_properties(
            self,
            mock_check_paths,
            mock_load_amber_report_excel_config,
            mock_create_output_directory,
            mock_amber_report_path,
            mock_processed_path,
            mock_raw_path,
            property_name,
            expected_path_tuple,
        ):
            """
            Test that master_devices_path is set correctly.
            """
            fin_month = "01"
            fin_year = "2425"
            config = Config(fin_month=fin_month, fin_year=fin_year, raw_data_dir=mock_raw_path)

            expected_path = mock_raw_path
            for part in expected_path_tuple:
                if part == "year":
                    expected_path /= fin_year
                elif part == "month":
                    expected_path /= fin_month
                else:
                    expected_path /= part

            assert getattr(config, property_name) == expected_path

        def test_calls_check_paths(
            self,
            mocker,
            mock_check_paths,
            mock_load_amber_report_excel_config,
            mock_create_output_directory,
            mock_amber_report_path,
            mock_processed_path,
            mock_raw_path,
        ):
            """
            Test that _define_dataset_paths calls _check_paths.
            """
            fin_month = "01"
            fin_year = "2425"
            Config(fin_month=fin_month, fin_year=fin_year, raw_data_dir=mock_raw_path)

            expected_paths_to_check = [
                mock_raw_path / fin_year / fin_month / MASTER_DEVICES_CSV_NAME,
                mock_raw_path / fin_year / fin_month / EXCEPTIONS_CSV_NAME,
                mock_raw_path / PROVIDER_CODES_LOOKUP_CSV_NAME,
                mock_raw_path / fin_year / DEVICE_TAXONOMY_CSV_NAME,
            ]

            mock_check_paths.assert_called_once_with(expected_paths_to_check)

        def test_dataset_config_property(
            self,
            mock_check_paths,
            mock_load_amber_report_excel_config,
            mock_create_output_directory,
            mock_amber_report_path,
            mock_processed_path,
            mock_raw_path,
        ):
            """
            Test that dataset_config property returns a dictionary with dataset paths.
            """
            fin_month = "01"
            fin_year = "2425"
            config = Config(fin_month=fin_month, fin_year=fin_year, raw_data_dir=mock_raw_path)

            expected_dataset_config = {
                "master_devices": {
                    "filepath_or_buffer": mock_raw_path
                    / fin_year
                    / fin_month
                    / MASTER_DEVICES_CSV_NAME,
                    "low_memory": False,
                },
                "exceptions": {
                    "filepath_or_buffer": mock_raw_path
                    / fin_year
                    / fin_month
                    / EXCEPTIONS_CSV_NAME
                },
                "provider_codes_lookup": {
                    "filepath_or_buffer": mock_raw_path / PROVIDER_CODES_LOOKUP_CSV_NAME
                },
                "device_taxonomy": {
                    "filepath_or_buffer": mock_raw_path / fin_year / DEVICE_TAXONOMY_CSV_NAME
                },
            }

            assert config.dataset_config == expected_dataset_config

    class TestCheckPaths:
        """
        Tests for Config._check_paths method.
        """

        @pytest.mark.parametrize("list", [True, False])
        def test_does_not_raise(self, tmp_path, list):
            """
            Test that _check_paths does not raise an error if all paths exist.
            """
            mock_path = tmp_path / "mock_path"
            mock_path.mkdir(parents=True)

            mock_paths = [mock_path] if list else mock_path
            Config._check_paths(mock_paths)

        def test_raises_exception_group(self, mocker, tmp_path):
            """
            Test that _check_paths raises an ExceptionGroup if any path does not exist.
            """
            mock_path = tmp_path / "mock_path"
            mock_path.mkdir(parents=True)
            mock_non_existent_path = tmp_path / "non_existent_path"

            mock_paths = [mock_path, mock_non_existent_path]

            with pytest.raises(ExceptionGroup) as exc_info:
                Config._check_paths(mock_paths)

            assert isinstance(exc_info.value, ExceptionGroup)
            assert len(exc_info.value.exceptions) == 1
            assert isinstance(exc_info.value.exceptions[0], PathNotFoundError)
            assert str(exc_info.value.exceptions[0]) == f"Path not found: {mock_non_existent_path}"

        def test_debug_log_called(self, mock_debug, tmp_path):
            """
            Test that _check_paths logs debug messages for each path checked.
            """
            mock_path = tmp_path / "mock_path"
            mock_path.mkdir(parents=True)

            mock_paths = [mock_path]

            Config._check_paths(mock_paths)

            mock_debug.assert_called_once_with("Checking if the path exists: {}", mock_path)

        def test_raises_exception_group_with_multiple_errors(self, mocker, tmp_path):
            """
            Test that _check_paths raises an ExceptionGroup with multiple PathNotFoundError exceptions.
            """
            mock_path = tmp_path / "mock_path"
            mock_path.mkdir(parents=True)
            mock_non_existent_path1 = tmp_path / "non_existent_path1"
            mock_non_existent_path2 = tmp_path / "non_existent_path2"

            mock_paths = [mock_path, mock_non_existent_path1, mock_non_existent_path2]

            with pytest.raises(ExceptionGroup) as exc_info:
                Config._check_paths(mock_paths)

            assert isinstance(exc_info.value, ExceptionGroup)
            assert len(exc_info.value.exceptions) == 2
            assert all(isinstance(e, PathNotFoundError) for e in exc_info.value.exceptions)
            assert (
                str(exc_info.value.exceptions[0]) == f"Path not found: {mock_non_existent_path1}"
            )
            assert (
                str(exc_info.value.exceptions[1]) == f"Path not found: {mock_non_existent_path2}"
            )

    class TestLoadAmberReportExcelConfig:
        """
        Tests for Config._load_amber_report_excel_config method.
        """

        @pytest.fixture
        def test_config(
            self,
            mocker,
            mock_amber_report_path,
            mock_define_dataset_config,
            mock_check_paths,
            mock_create_output_directory,
            mock_raw_path,
        ):
            """
            Setup method to initialize the Config instance with mocked paths.
            """
            mocker.patch("devices_rap.config.Config.__init__", return_value=None)
            config = Config(fin_month="01", fin_year="2425")
            config.fin_month = "01"
            config.fin_year = "2425"
            config.amber_report_excel_config_path = mock_amber_report_path
            return config

        def prep_test_amber_report_excel_config(
            self,
            amber_excel_config_path: Path,
            setting: Literal[
                "meets_requirements",
                "missing_worksheet_config",
                "empty_worksheet_config",
                "invalid_worksheet_config",
            ],
        ):
            """
            Function to create a test amber report excel config file. Builds up the YAML structure
            based on the parameters provided.

            Parameters:
            -----------
            amber_excel_config_path: Path
                The path where the test config file will be created.
            setting: Literal[
                "meets_requirements",
                "missing_worksheet_config",
                "empty_worksheet_config",
                "invalid_worksheet_config"
            ]
                The setting to determine the content of the config file.
                    - "meets_requirements": Valid config with WORKSHEET_CONFIG.
                    - "missing_worksheet_config": Config without WORKSHEET_CONFIG.
                    - "empty_worksheet_config": Config with empty WORKSHEET_CONFIG.
                    - "invalid_worksheet_config": Config with WORKSHEET_CONFIG not as a dictionary.

            Returns:
            --------
            config_data: dict
                The configuration data that was written to the YAML file.
            """
            if setting == "missing_worksheet_config":
                config_data = {
                    "SOME_OTHER_CONFIG": {
                        "test_key": "test_value",
                    }
                }
            elif setting == "empty_worksheet_config":
                config_data = {"WORKSHEET_CONFIG": {}}
            elif setting == "invalid_worksheet_config":
                config_data = {"WORKSHEET_CONFIG": "This is not a dictionary"}
            else:  # meets_requirements
                config_data = {
                    "WORKSHEET_CONFIG": {
                        "test_key": "test_value",
                    }
                }

            with open(amber_excel_config_path, "w", encoding="UTF8") as file:
                yaml.dump(config_data, file, default_flow_style=False, sort_keys=False)

            return config_data

        def test_loads_config(
            self,
            test_config,
        ):
            """
            Test that _load_amber_report_excel_config loads the configuration from the YAML file.
            """
            config = test_config
            self.prep_test_amber_report_excel_config(
                config.amber_report_excel_config_path, "meets_requirements"
            )
            config._load_amber_report_excel_config()
            assert config.amber_report_output_instructions == {"test_key": "test_value"}

        @pytest.mark.parametrize(
            "setting, expected_error",
            [
                (
                    "missing_worksheet_config",
                    "Amber Report Excel configuration file is missing 'WORKSHEET_CONFIG' key.",
                ),
                (
                    "empty_worksheet_config",
                    "Amber Report Excel configuration 'WORKSHEET_CONFIG' is empty.",
                ),
                (
                    "invalid_worksheet_config",
                    "Amber Report Excel configuration 'WORKSHEET_CONFIG' should be a dictionary.",
                ),
            ],
        )
        def test_loads_config_errors(
            self,
            test_config,
            setting,
            expected_error,
        ):
            """
            Test that _load_amber_report_excel_config raises ConfigError for invalid configurations.
            """
            config = test_config
            self.prep_test_amber_report_excel_config(
                config.amber_report_excel_config_path, setting
            )

            with pytest.raises(ConfigError, match=expected_error):
                config._load_amber_report_excel_config()

        def test_calls_check_paths(
            self,
            test_config,
            mock_check_paths,
        ):
            """
            Test that _load_amber_report_excel_config calls _check_paths with the correct path.
            """
            config = test_config
            self.prep_test_amber_report_excel_config(
                config.amber_report_excel_config_path, "meets_requirements"
            )
            config._load_amber_report_excel_config()

            mock_check_paths.assert_called_once_with(config.amber_report_excel_config_path)

        @pytest.mark.parametrize(
            "call_number, expected_log_message",
            [
                (0, "Loading the Amber Report Excel configuration from: {}"),
                (1, "Loaded the Amber Report Excel instructions successfully: {}"),
            ],
        )
        def test_logger_debug(
            self,
            test_config,
            mock_debug,
            call_number,
            expected_log_message,
        ):
            """
            Test that _load_amber_report_excel_config logs debug messages.
            """
            config = test_config
            self.prep_test_amber_report_excel_config(
                config.amber_report_excel_config_path, "meets_requirements"
            )
            config._load_amber_report_excel_config()

            if call_number == 0:
                format_value = config.amber_report_excel_config_path
            else:
                format_value = config.amber_report_output_instructions

            actual_call = mock_debug.call_args_list[call_number].args
            assert actual_call == (expected_log_message, format_value)

        def test_logger_debug_called_twice(self, test_config, mock_debug):
            """
            Test that _load_amber_report_excel_config calls logger.debug twice.
            """
            config = test_config
            self.prep_test_amber_report_excel_config(
                config.amber_report_excel_config_path, "meets_requirements"
            )
            config._load_amber_report_excel_config()

            assert mock_debug.call_count == 2

    class TestCreateOutputDirectory:
        """
        Tests for Config.create_output_directory method.
        """

        @pytest.fixture
        def test_config(
            self,
            mocker,
            mock_amber_report_path,
            mock_define_dataset_config,
            mock_check_paths,
            mock_load_amber_report_excel_config,
            mock_raw_path,
            mock_processed_path,
        ):
            """
            Setup method to initialize the Config instance with mocked paths.
            """
            mocker.patch("devices_rap.config.Config.__init__", return_value=None)
            config = Config(fin_month="01", fin_year="2425")
            config.fin_month = "01"
            config.fin_year = "2425"
            config.output_directory = mock_processed_path / "01" / "2425"
            return config

        @pytest.fixture
        def mock_create_directory(self, mocker):
            """
            Mock the create_directory function.
            """
            return mocker.patch("devices_rap.config.create_directory")

        def test_creates_directory(self, test_config):
            """
            Test that create_output_directory creates the output directory.
            """
            output_directory = test_config.create_output_directory()

            assert output_directory.exists()
            assert output_directory.is_dir()
            assert output_directory == test_config.output_directory

        def test_calls_create_directory(self, mock_create_directory, test_config):
            """
            Test that create_output_directory calls create_directory with the correct path.
            """
            test_config.create_output_directory()

            mock_create_directory.assert_called_once_with(test_config.output_directory)

        def test_logger_debug_called(self, mock_create_directory, mock_debug, test_config):
            """
            Test that create_output_directory logs the correct debug message.
            """
            test_config.create_output_directory()

            mock_debug.assert_called_once_with(
                "Output directory for Amber Report Excel is {}", test_config.output_directory
            )
