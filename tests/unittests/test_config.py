"""
Tests for the configuration settings in devices_rap/config.py.
"""

import pytest
from dotenv import dotenv_values
from loguru import logger
from pathlib import Path
from devices_rap.config import MASTER_DEVICES_PATH, check_paths, PathNotFoundError
from exceptiongroup import ExceptionGroup

from devices_rap.config import (
    DATA_DIR,
    EXTERNAL_DATA_DIR,
    FIGURES_DIR,
    INTERIM_DATA_DIR,
    MODELS_DIR,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
    REPORTS_DIR,
)


class TestConfig:
    """
    Tests for the configuration settings
    """

    @pytest.mark.parametrize(
        "dir_path, expected",
        [
            (DATA_DIR, "data"),
            (RAW_DATA_DIR, "data/raw"),
            (INTERIM_DATA_DIR, "data/interim"),
            (PROCESSED_DATA_DIR, "data/processed"),
            (EXTERNAL_DATA_DIR, "data/external"),
            (MODELS_DIR, "models"),
            (REPORTS_DIR, "reports"),
            (FIGURES_DIR, "reports/figures"),
        ],
    )
    def test_dir_paths(self, dir_path, expected):
        """Test if the directory paths are correctly set."""
        windows_expected = expected.replace("/", "\\")
        actual = dir_path.__str__()

        assert actual.endswith(expected) or actual.endswith(windows_expected)

    def test_logger_configuration(self):
        """Test if the logger is correctly configured."""
        logger.info("Testing logger configuration")
        assert logger

    def test_env_variables_loaded(self):
        """Test if environment variables are loaded from the .env file."""
        env_vars = dotenv_values()
        assert env_vars is not None


class TestCheckPaths:
    """
    Tests for the check_paths function
    """

    def test_check_paths_all_exist(self, mocker):
        """Test check_paths when all paths exist."""
        mocker.patch("pathlib.Path.exists", return_value=True)
        try:
            check_paths()
        except ExceptionGroup:
            pytest.fail("ExceptionGroup was raised unexpectedly!")

    def test_check_paths_all_missing(self, mocker):
        """Test check_paths when some paths are missing."""

        mocker.patch("pathlib.Path.exists", return_value=False)
        with pytest.raises(ExceptionGroup) as exc_info:
            check_paths()
        assert any(isinstance(e, PathNotFoundError) for e in exc_info.value.exceptions)

    def test_check_paths_no_paths_provided(self, mocker):
        """Test check_paths when no paths are provided."""
        mocker.patch("pathlib.Path.exists", return_value=True)
        try:
            check_paths([])
        except ExceptionGroup:
            pytest.fail("ExceptionGroup was raised unexpectedly!")

    def test_check_paths_custom_paths(self, mocker):
        """Test check_paths with custom paths."""
        custom_paths = [Path("/custom/path/one"), Path("/custom/path/two")]
        mocker.patch("pathlib.Path.exists", return_value=True)
        try:
            check_paths(custom_paths)
        except ExceptionGroup:
            pytest.fail("ExceptionGroup was raised unexpectedly!")


if __name__ == "__main__":
    pytest.main([__file__])
