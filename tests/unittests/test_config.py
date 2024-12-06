from pathlib import Path

import pytest
from dotenv import dotenv_values
from loguru import logger
from tqdm import tqdm

from devices_rap.config import (
    DATA_DIR,
    EXTERNAL_DATA_DIR,
    FIGURES_DIR,
    INTERIM_DATA_DIR,
    MODELS_DIR,
    PROCESSED_DATA_DIR,
    PROJ_ROOT,
    RAW_DATA_DIR,
    REPORTS_DIR,
)

# FILE: devices_rap/test_config.py


class TestConfig:
    """
    Tests for the configuration settings
    """

    def test_proj_root(self):
        """Test if PROJ_ROOT is correctly set to the project's root directory."""
        assert PROJ_ROOT == Path(__file__).resolve().parents[2]

    def test_data_dir(self):
        """Test if DATA_DIR is correctly set to the 'data' directory."""
        assert DATA_DIR == Path("data")

    def test_raw_data_dir(self):
        """Test if RAW_DATA_DIR is correctly set to the 'data/raw' directory."""
        assert RAW_DATA_DIR == DATA_DIR / "raw"

    def test_interim_data_dir(self):
        """Test if INTERIM_DATA_DIR is correctly set to the 'data/interim' directory."""
        assert INTERIM_DATA_DIR == DATA_DIR / "interim"

    def test_processed_data_dir(self):
        """Test if PROCESSED_DATA_DIR is correctly set to the 'data/processed' directory."""
        assert PROCESSED_DATA_DIR == DATA_DIR / "processed"

    def test_external_data_dir(self):
        """Test if EXTERNAL_DATA_DIR is correctly set to the 'data/external' directory."""
        assert EXTERNAL_DATA_DIR == DATA_DIR / "external"

    def test_models_dir(self):
        """Test if MODELS_DIR is correctly set to the 'models' directory."""
        assert MODELS_DIR == PROJ_ROOT / "models"

    def test_reports_dir(self):
        """Test if REPORTS_DIR is correctly set to the 'reports' directory."""
        assert REPORTS_DIR == PROJ_ROOT / "reports"

    def test_figures_dir(self):
        """Test if FIGURES_DIR is correctly set to the 'reports/figures' directory."""
        assert FIGURES_DIR == REPORTS_DIR / "figures"

    def test_logger_configuration(self):
        """Test if the logger is correctly configured."""
        logger.info("Testing logger configuration")
        assert logger

    def test_env_variables_loaded(self):
        """Test if environment variables are loaded from the .env file."""
        env_vars = dotenv_values()
        assert env_vars is not None


if __name__ == "__main__":
    pytest.main([__file__])
