"""
Tests for devices_rap/data_in/load_csv.py
"""

import pandas as pd
import pytest

from nhs_herbot.errors import NoDatasetsProvidedError
from devices_rap.data_in.load_csv import load_devices_datasets


class TestLoadDevicesDatasets:
    """
    Tests for load_devices_datasets
    """

    def test_load_devices_datasets(self, mocker):
        """
        Test that the function returns a dictionary with the expected keys
        """
        datasets = {
            "test1": {"filepath_or_buffer": "test1"},
            "test2": {"filepath_or_buffer": "test2"},
        }
        mock_pipeline_config = mocker.MagicMock()
        mock_pipeline_config.dataset_config = datasets

        mock_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mocker.patch("devices_rap.data_in.load_csv.load_csv_data", return_value=mock_df)

        result = load_devices_datasets(mock_pipeline_config)
        assert set(result.keys()) == set(datasets.keys())

    def test_data(self, mocker):
        """
        Test that the function returns a dictionary with the expected keys
        """
        datasets = {
            "test1": {"filepath_or_buffer": "test1"},
            "test2": {"filepath_or_buffer": "test2"},
        }
        mock_pipeline_config = mocker.MagicMock()
        mock_pipeline_config.dataset_config = datasets

        mock_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mocker.patch("devices_rap.data_in.load_csv.load_csv_data", return_value=mock_df)

        result = load_devices_datasets(mock_pipeline_config)
        for dataset in result.values():
            assert "data" in dataset

    def test_data_shape(self, mocker):
        """
        Test that the function returns a dictionary with the expected keys
        """
        datasets = {
            "test1": {"filepath_or_buffer": "test1"},
            "test2": {"filepath_or_buffer": "test2"},
        }
        mock_pipeline_config = mocker.MagicMock()
        mock_pipeline_config.dataset_config = datasets

        mock_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mocker.patch("devices_rap.data_in.load_csv.load_csv_data", return_value=mock_df)

        result = load_devices_datasets(mock_pipeline_config)
        for dataset in result.values():
            assert dataset["data"].shape == (2, 2)

    def test_data_type(self, mocker):
        """
        Test that the function returns a dictionary with the expected keys
        """
        datasets = {
            "test1": {"filepath_or_buffer": "test1"},
            "test2": {"filepath_or_buffer": "test2"},
        }
        mock_pipeline_config = mocker.MagicMock()
        mock_pipeline_config.dataset_config = datasets

        mock_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mocker.patch("devices_rap.data_in.load_csv.load_csv_data", return_value=mock_df)

        result = load_devices_datasets(mock_pipeline_config)
        for dataset in result.values():
            assert isinstance(dataset["data"], pd.DataFrame)

    def test_no_datasets_error(self, mocker):
        """
        Test that the function raises an AssertionError when no datasets are provided
        """
        datasets = {}
        mock_pipeline_config = mocker.MagicMock()
        mock_pipeline_config.dataset_config = datasets

        

        with pytest.raises(NoDatasetsProvidedError):
            load_devices_datasets(mock_pipeline_config)

    def test_removes_data(self, mocker):
        """
        Test that the function removes the "data" key from the datasets dictionary
        and then overwrites it with the loaded DataFrame
        """
        datasets = {
            "test1": {"filepath_or_buffer": "test1", "data": "test_data"},
        }
        mock_pipeline_config = mocker.MagicMock()
        mock_pipeline_config.dataset_config = datasets

        mock_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mocker.patch("devices_rap.data_in.load_csv.load_csv_data", return_value=mock_df)

        result = load_devices_datasets(mock_pipeline_config)
        dataset = result["test1"]
        assert str(dataset["data"]) != "test_data"


if __name__ == "__main__":
    pytest.main([__file__])
