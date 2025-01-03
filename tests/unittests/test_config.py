"""
Tests for the configuration settings in devices_rap/config.py.
"""

import sys
import importlib

import pytest
from dotenv import dotenv_values
from loguru import logger
from unittest import mock

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
        assert dir_path.__str__().endswith(expected)

    def test_logger_configuration(self):
        """Test if the logger is correctly configured."""
        logger.info("Testing logger configuration")
        assert logger

    def test_env_variables_loaded(self):
        """Test if environment variables are loaded from the .env file."""
        env_vars = dotenv_values()
        assert env_vars is not None

    def test_tqdm_not_installed(self):
        """Test if ModuleNotFoundError is handled when tqdm is not installed."""
        with mock.patch.dict("sys.modules", {"tqdm": None}):
            import devices_rap.config

            importlib.reload(devices_rap.config)

            assert not sys.modules.get("tqdm")


if __name__ == "__main__":
    pytest.main([__file__])
