"""
Tests for devices_rap/clean_data.py
"""

import pandas as pd
import pytest

from devices_rap import clean_data


pytestmark = pytest.mark.no_data_needed


class TestBatchNormaliseColumnNames:
    """
    Tests for clean_data.batch_normalise_column_names
    """

    def test_checks_for_empty_input(self):
        """
        Test that the function raises an error when no data is provided
        """
        with pytest.raises(clean_data.NoDatasetsProvidedError):
            clean_data.batch_normalise_column_names({})

    def test_checks_for_missing_data_key(self, mocker):
        """
        Test that the function raises an error when the data key is missing
        """
        mocker.patch("devices_rap.clean_data.normalise_column_names")
        with pytest.raises(clean_data.NoDataProvidedError):
            clean_data.batch_normalise_column_names({"test": {}})

    def test_check_for_data_not_dataframe(self, mocker):
        """
        Test that the function raises an error when the data is not a DataFrame
        """
        mocker.patch("devices_rap.clean_data.normalise_column_names")
        with pytest.raises(clean_data.NoDataProvidedError):
            clean_data.batch_normalise_column_names({"test": {"data": None}})

    def test_calls_normalise_column_names(self, mocker):
        """
        Test that the function calls the normalise_column_names function
        """
        mock_function = mocker.patch("devices_rap.clean_data.normalise_column_names")
        dataframe = pd.DataFrame()
        datasets = {"test": {"data": dataframe}}
        clean_data.batch_normalise_column_names(datasets)
        mock_function.assert_called_once_with(dataframe)

    def test_calls_normalise_column_names_for_each_dataset(self, mocker):
        """
        Test that the function calls the normalise_column_names function for each dataset
        """
        mock_function = mocker.patch("devices_rap.clean_data.normalise_column_names")
        input_df = pd.DataFrame()
        datasets = {"test1": {"data": input_df}, "test2": {"data": input_df}}
        clean_data.batch_normalise_column_names(datasets)
        assert mock_function.call_count == 2

    def test_returns_normalised_datasets(self, mocker):
        """
        Test that the function returns the normalised datasets
        """
        expected_df = pd.DataFrame({"col1": ["test"]})
        mocker.patch("devices_rap.clean_data.normalise_column_names", return_value=expected_df)
        input_df = pd.DataFrame()
        datasets = {"test1": {"data": input_df}, "test2": {"data": input_df}}
        result = clean_data.batch_normalise_column_names(datasets)
        assert all("data" in dataset for dataset in result.values())
        for dataset in result.values():
            pd.testing.assert_frame_equal(dataset["data"], expected_df)


class TestCleanseMasterData:
    """
    Tests for clean_data.cleanse_master_data
    """

    @pytest.fixture
    def mock_called_functions(self, mocker):
        """
        Fixture to mock the functions called by cleanse_master_data
        """
        mock_convert_fin_dates = mocker.patch(
            "devices_rap.clean_data.convert_fin_dates", return_value="foo", autospec=True
        )
        mock_convert_values_to = mocker.patch(
            "devices_rap.clean_data.convert_values_to", return_value="bar", autospec=True
        )
        mock_logger = mocker.patch("devices_rap.clean_data.logger")

        return mock_convert_fin_dates, mock_convert_values_to, mock_logger

    @pytest.fixture
    def test_master_df(self):
        """
        Fixture to create a test master DataFrame
        """
        return pd.DataFrame(
            {
                "der_high_level_device_type": ["test_der_high_level_device_type"],
                "cln_activity_year": ["test_cln_activity_year"],
                "cln_activity_month": ["test_cln_activity_month"],
            }
        )

    def test_covert_fin_datas_calls(self, test_master_df, mock_called_functions):
        """
        Test that the function applies the convert_fin_dates function correctly
        """
        mock_convert_fin_dates, _, _ = mock_called_functions
        clean_data.cleanse_master_data(test_master_df)
        assert mock_convert_fin_dates.call_count == 1

    def test_convert_values_to_calls(self, test_master_df, mock_called_functions):
        """
        Test that the function applies the convert_values_to function correctly
        """
        _, mock_convert_values_to, _ = mock_called_functions
        clean_data.cleanse_master_data(test_master_df)
        assert mock_convert_values_to.call_count == 2
        mock_convert_values_to.assert_called_with(
            "test_cln_activity_year", match=[2425], to=202425
        )

    def test_logger_calls(self, test_master_df, mock_called_functions):
        """
        Test that the function logs the expected messages
        """
        _, _, mock_logger = mock_called_functions
        clean_data.cleanse_master_data(test_master_df)
        assert mock_logger.info.call_count == 4
        mock_logger.info.assert_any_call("Cleaning the master dataset ready for processing")
        mock_logger.info.assert_any_call("Converting high level device type values")
        mock_logger.info.assert_any_call("Converting activity year values without century")
        mock_logger.info.assert_any_call("Converting activity date values to datetime")


if __name__ == "__main__":
    pytest.main([__file__])
