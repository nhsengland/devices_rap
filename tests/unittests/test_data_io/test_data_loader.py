"""
Tests for devices_rap/data_io/input/data_loader.py
"""

import pandas as pd
import pytest
from nhs_herbot.errors import NoDatasetsProvidedError

from devices_rap.data_io.input.data_loader import load_devices_datasets


class TestLoadDevicesDatasets:
    """
    Tests for load_devices_datasets
    """

    def test_load_devices_datasets_csv(self, mocker):
        """
        Test that the function returns a dictionary with the expected keys for CSV loading
        """
        datasets = {
            "test1": {"filepath_or_buffer": "test1.csv"},
            "test2": {"filepath_or_buffer": "test2.csv"},
        }
        mock_pipeline_config = mocker.MagicMock()
        mock_pipeline_config.dataset_config = datasets

        mock_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mocker.patch("devices_rap.data_io.input.data_loader.load_csv_data", return_value=mock_df)

        result = load_devices_datasets(mock_pipeline_config)

        assert isinstance(result, dict)
        assert "test1" in result
        assert "test2" in result
        assert isinstance(result["test1"]["data"], pd.DataFrame)
        assert isinstance(result["test2"]["data"], pd.DataFrame)

    def test_load_devices_datasets_sql(self, mocker):
        """
        Test that the function returns a dictionary with the expected keys for SQL loading
        """
        datasets = {
            "test1": {"sql_query_path": "test1.sql"},
            "test2": {"sql_query_path": "test2.sql"},
        }
        mock_pipeline_config = mocker.MagicMock()
        mock_pipeline_config.dataset_config = datasets
        mock_sql_server = mocker.MagicMock()
        mock_pipeline_config.sql_server = mock_sql_server

        mock_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mock_sql_server.load_from_sql_query.return_value = mock_df

        result = load_devices_datasets(mock_pipeline_config)

        assert isinstance(result, dict)
        assert "test1" in result
        assert "test2" in result
        assert isinstance(result["test1"]["data"], pd.DataFrame)
        assert isinstance(result["test2"]["data"], pd.DataFrame)

    def test_no_datasets_error(self, mocker):
        """
        Test that the function raises an error when no datasets are provided
        """
        mock_pipeline_config = mocker.MagicMock()
        mock_pipeline_config.dataset_config = {}

        with pytest.raises(NoDatasetsProvidedError):
            load_devices_datasets(mock_pipeline_config)

    def test_removes_data(self, mocker):
        """
        Test that the function removes the "data" key from the datasets dictionary
        and then overwrites it with the loaded DataFrame
        """
        datasets = {
            "test1": {"filepath_or_buffer": "test1.csv", "data": "test_data"},
        }
        mock_pipeline_config = mocker.MagicMock()
        mock_pipeline_config.dataset_config = datasets

        mock_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mocker.patch("devices_rap.data_io.input.data_loader.load_csv_data", return_value=mock_df)

        result = load_devices_datasets(mock_pipeline_config)

        # Check that the "data" key is overwritten with the DataFrame
        pd.testing.assert_frame_equal(result["test1"]["data"], mock_df)
        # Check that other keys are preserved
        assert result["test1"]["filepath_or_buffer"] == "test1.csv"
