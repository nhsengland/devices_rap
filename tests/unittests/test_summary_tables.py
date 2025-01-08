"""
Tests for devices_rap/summary_tables.py
"""

import re

import pandas as pd
import pytest

from devices_rap import summary_tables
from devices_rap.errors import ColumnsNotFoundError


pytestmark = pytest.mark.no_data_needed


@pytest.fixture
def mock_create_pivot_sum_table(mocker):
    """
    Mock the create_pivot_sum_table function
    """
    return mocker.patch("devices_rap.summary_tables.create_pivot_sum_table")


class TestCreatePivotSumTable:
    """
    Test class for summary_tables.create_pivot_sum_table
    """

    def test_returns_dataframe(self, mocker, empty_df):
        """
        Tests that the create_pivot_table function returns a DataFrame
        """
        mocker.patch("pandas.pivot_table", return_value=pd.DataFrame())
        result = summary_tables.create_pivot_sum_table(empty_df)
        assert isinstance(result, pd.DataFrame)

    @pytest.mark.parametrize(
        "kwarg, expected",
        [
            ("data", pd.DataFrame()),
            ("values", "cln_total_cost"),
            ("columns", "activity_date"),
            (
                "index",
                [
                    "nhs_england_region",
                    "der_provider_code",
                    "upd_high_level_device_type",
                    "rag_status",
                ],
            ),
        ],
    )
    def test_empty_input_pivot_table_call(self, mocker, empty_df, kwarg, expected):
        """
        Test that the function handle an empty input correctly, passing the correct arguments to
        pd.pivot_table with reasonable defaults.
        """
        mock_pivot_table = mocker.patch("pandas.pivot_table")
        summary_tables.create_pivot_sum_table(empty_df)

        # assert mock_pivot_table.assert_called()  # Ensure the function was called

        actual = mock_pivot_table.call_args.kwargs.get(kwarg)

        if isinstance(expected, pd.DataFrame):
            pd.testing.assert_frame_equal(actual, expected)
        else:
            assert actual == expected

    @pytest.mark.parametrize(
        "kwarg, actual_kwarg, expected",
        [
            ("values", "values", ["test"]),
            ("columns", "columns", ["test"]),
            ("base_index", "index", ["test"]),
            (
                "extended_index",
                "index",
                [
                    "nhs_england_region",
                    "der_provider_code",
                    "upd_high_level_device_type",
                    "rag_status",
                    "test",
                ],
            ),
        ],
    )
    def test_non_default_values(self, mocker, empty_df, kwarg, actual_kwarg, expected):
        """
        Test that the function can handle non-default values
        """
        mock_pivot_table = mocker.patch("pandas.pivot_table")
        summary_tables.create_pivot_sum_table(empty_df, **{kwarg: ["test"]})

        actual = mock_pivot_table.call_args.kwargs.get(actual_kwarg)

        assert actual == expected

    @pytest.mark.parametrize(
        "input_data, expected",
        [
            (
                [("test", "test", "test", "test", "test", 1)],
                pd.DataFrame(
                    columns=[
                        "nhs_england_region",
                        "der_provider_code",
                        "upd_high_level_device_type",
                        "rag_status",
                        "test",
                    ],
                    data=[["test", "test", "test", "test", 1]],
                ),
            ),
            (
                [
                    ("test", "test", "test", "test", "test1", 1),
                    ("test", "test", "test", "test", "test2", 2),
                ],
                pd.DataFrame(
                    columns=[
                        "nhs_england_region",
                        "der_provider_code",
                        "upd_high_level_device_type",
                        "rag_status",
                        "test1",
                        "test2",
                    ],
                    data=[["test", "test", "test", "test", 1, 2]],
                ),
            ),
            (
                [
                    ("test", "test", "test", "test", "test1", 1),
                    ("test", "test", "test", "test", "test1", 2),
                ],
                pd.DataFrame(
                    columns=[
                        "nhs_england_region",
                        "der_provider_code",
                        "upd_high_level_device_type",
                        "rag_status",
                        "test1",
                    ],
                    data=[["test", "test", "test", "test", 3]],
                ),
            ),
            (
                [
                    ("test", "test", "test", "test", "test1", 1),
                    ("test", "test", "test", "test", "test1", 2),
                    ("test", "test", "test", "test", "test2", 3),
                    ("test", "test", "test", "test", "test2", 4),
                ],
                pd.DataFrame(
                    columns=[
                        "nhs_england_region",
                        "der_provider_code",
                        "upd_high_level_device_type",
                        "rag_status",
                        "test1",
                        "test2",
                    ],
                    data=[["test", "test", "test", "test", 3, 7]],
                ),
            ),
        ],
    )
    def test_pivot_table_happy_path(self, input_data, expected):
        """
        Test that the function can handle normal inputs and return the output in the expected
        format.

        Cases include:
        - Single row with a single value to pivot
        - Multiple rows with different values to pivot
        - Multiple rows with the same value to pivot
        - Multiple rows with multiple values to pivot
        """
        input_df = pd.DataFrame(
            columns=[
                "nhs_england_region",
                "der_provider_code",
                "upd_high_level_device_type",
                "rag_status",
                "activity_date",
                "cln_total_cost",
            ],
            data=input_data,
        )

        actual = summary_tables.create_pivot_sum_table(input_df)

        pd.testing.assert_frame_equal(actual, expected)

    @pytest.mark.parametrize(
        "input_columns, expected_message",
        [
            (
                ["cln_total_cost", "activity_date"],
                "Columns were not found in the dataset. "
                "MISSING COLUMNS: "
                "BASE_INDEX: ['der_provider_code', 'nhs_england_region', 'rag_status', "
                "'upd_high_level_device_type']",
            ),
            (
                [
                    "nhs_england_region",
                    "der_provider_code",
                    "upd_high_level_device_type",
                    "rag_status",
                    "activity_date",
                ],
                "Columns were not found in the dataset. "
                "MISSING COLUMNS: "
                "VALUES: ['cln_total_cost']",
            ),
            (
                [
                    "nhs_england_region",
                    "der_provider_code",
                    "upd_high_level_device_type",
                    "rag_status",
                    "cln_total_cost",
                ],
                "Columns were not found in the dataset. "
                "MISSING COLUMNS: "
                "COLUMNS: ['activity_date']",
            ),
            (
                [],
                "Columns were not found in the dataset. "
                "MISSING COLUMNS: "
                "VALUES: ['cln_total_cost'] "
                "COLUMNS: ['activity_date'] "
                "BASE_INDEX: ['der_provider_code', 'nhs_england_region', 'rag_status', "
                "'upd_high_level_device_type']",
            ),
        ],
    )
    def test_columns_not_found_error_raised(
        self, mock_log_levels, input_columns, expected_message
    ):
        """
        Test that the ColumnsNotFoundError is raised when the columns are not found in the dataset
        """
        mock_info, mock_error, _, _ = mock_log_levels

        input_df = pd.DataFrame(columns=input_columns)

        with pytest.raises(ColumnsNotFoundError, match=re.escape(expected_message)):
            summary_tables.create_pivot_sum_table(input_df)

        mock_info.assert_called_once()
        mock_error.assert_called_once_with(expected_message)

    @pytest.mark.parametrize(
        "input_args, expected_message",
        [
            (
                {},
                "Creating a pivot table with the sum of the values for the given columns."
                "VALUES: cln_total_cost, COLUMNS: activity_date, INDEX: "
                "['nhs_england_region', 'der_provider_code', 'upd_high_level_device_type', 'rag_status']",
            ),
            (
                {
                    "values": ["test"],
                    "columns": ["test"],
                    "base_index": ["test"],
                    "extended_index": ["test"],
                },
                "Creating a pivot table with the sum of the values for the given columns."
                "VALUES: ['test'], COLUMNS: ['test'], INDEX: ['test', 'test']",
            ),
        ],
    )
    def test_log_called(self, mock_info, mocker, empty_df, input_args, expected_message):
        """
        Test that the loguru.logger is called
        """
        mocker.patch("pandas.pivot_table")
        summary_tables.create_pivot_sum_table(empty_df, **input_args)

        mock_info.assert_called_once_with(expected_message)


class TestCreateDeviceCategorySummaryTable:
    """
    Test class for summary.create_device_category_summary_table
    """

    def test_log_called(self, mock_info, mock_create_pivot_sum_table, empty_df):
        """
        Test that the loguru.logger is called
        """
        mock_create_pivot_sum_table.return_value = empty_df

        summary_tables.create_device_category_summary_table(empty_df)

        mock_info.assert_called_once_with("Creating the device category summary (pivot) table")

    def test_return_dataframe(self, mock_create_pivot_sum_table, empty_df):
        """
        Test that the function returns a DataFrame
        """
        mock_create_pivot_sum_table.return_value = empty_df

        result = summary_tables.create_device_category_summary_table(empty_df)

        assert isinstance(result, pd.DataFrame)

    def test_calls_create_pivot_sum_table(self, mock_create_pivot_sum_table, empty_df):
        """
        Test that the function calls the create_pivot_sum_table function
        """
        expected = pd.DataFrame(columns=["A", "B"], data=[(1, 1)])
        mock_create_pivot_sum_table.return_value = expected

        actual = summary_tables.create_device_category_summary_table(empty_df)

        mock_create_pivot_sum_table.assert_called_once()

        pd.testing.assert_frame_equal(actual, expected)

    @pytest.mark.parametrize(
        "kwarg, expected",
        [
            ("data", pd.DataFrame()),
            ("values", None),
            ("columns", None),
            ("base_index", None),
            ("extended_index", None),
        ],
    )
    def test_empty_input_create_sum_table_call(
        self, mock_create_pivot_sum_table, empty_df, kwarg, expected
    ):
        """
        Test that the function handle an empty input correctly, passing only the data argument to
        create_pivot_sum_table and leaving the rest as None (allowing the function to use the
        default argument values).
        """
        summary_tables.create_device_category_summary_table(empty_df)

        actual = mock_create_pivot_sum_table.call_args.kwargs.get(kwarg)

        if isinstance(expected, pd.DataFrame):
            pd.testing.assert_frame_equal(actual, expected)
        else:
            assert actual == expected

    @pytest.mark.parametrize(
        "input_data, expected",
        [
            (
                [("test", "test", "test", "test", "test", 1)],
                pd.DataFrame(
                    columns=[
                        "nhs_england_region",
                        "der_provider_code",
                        "upd_high_level_device_type",
                        "rag_status",
                        "test",
                    ],
                    data=[["test", "test", "test", "test", 1]],
                ),
            ),
            (
                [
                    ("test", "test", "test", "test", "test1", 1),
                    ("test", "test", "test", "test", "test2", 2),
                ],
                pd.DataFrame(
                    columns=[
                        "nhs_england_region",
                        "der_provider_code",
                        "upd_high_level_device_type",
                        "rag_status",
                        "test1",
                        "test2",
                    ],
                    data=[["test", "test", "test", "test", 1, 2]],
                ),
            ),
            (
                [
                    ("test", "test", "test", "test", "test1", 1),
                    ("test", "test", "test", "test", "test1", 2),
                ],
                pd.DataFrame(
                    columns=[
                        "nhs_england_region",
                        "der_provider_code",
                        "upd_high_level_device_type",
                        "rag_status",
                        "test1",
                    ],
                    data=[["test", "test", "test", "test", 3]],
                ),
            ),
            (
                [
                    ("test", "test", "test", "test", "test1", 1),
                    ("test", "test", "test", "test", "test1", 2),
                    ("test", "test", "test", "test", "test2", 3),
                    ("test", "test", "test", "test", "test2", 4),
                ],
                pd.DataFrame(
                    columns=[
                        "nhs_england_region",
                        "der_provider_code",
                        "upd_high_level_device_type",
                        "rag_status",
                        "test1",
                        "test2",
                    ],
                    data=[["test", "test", "test", "test", 3, 7]],
                ),
            ),
        ],
    )
    def test_happy_path(self, input_data, expected):
        """
        Test that the function can handle normal inputs and return the output in the expected
        format.

        This technically repeats the tests from create_pivot_sum_table, but it is useful to ensure
        that the function works as expected and is well integrated with the create_pivot_sum_table.

        Cases include:
        - Single row with a single value to pivot
        - Multiple rows with different values to pivot
        - Multiple rows with the same value to pivot
        - Multiple rows with multiple values to pivot
        """
        input_df = pd.DataFrame(
            columns=[
                "nhs_england_region",
                "der_provider_code",
                "upd_high_level_device_type",
                "rag_status",
                "activity_date",
                "cln_total_cost",
            ],
            data=input_data,
        )

        actual = summary_tables.create_device_category_summary_table(input_df)

        pd.testing.assert_frame_equal(actual, expected)


class TestCreateDeviceSummaryTable:
    """
    Test class for summary.create_device_summary_table
    """

    def test_log_called(self, mock_info, mock_create_pivot_sum_table, empty_df):
        """
        Test that the loguru.logger is called
        """
        mock_create_pivot_sum_table.return_value = empty_df

        summary_tables.create_device_summary_table(empty_df)

        mock_info.assert_called_once_with("Creating the device summary (pivot) table")

    def test_return_dataframe(self, mock_create_pivot_sum_table, empty_df):
        """
        Test that the function returns a DataFrame
        """
        mock_create_pivot_sum_table.return_value = empty_df

        result = summary_tables.create_device_summary_table(empty_df)

        assert isinstance(result, pd.DataFrame)

    def test_calls_create_pivot_sum_table(self, mock_create_pivot_sum_table, empty_df):
        """
        Test that the function calls the create_pivot_sum_table function
        """
        expected = pd.DataFrame(columns=["A", "B"], data=[(1, 1)])
        mock_create_pivot_sum_table.return_value = expected

        actual = summary_tables.create_device_summary_table(empty_df)

        mock_create_pivot_sum_table.assert_called_once()

        pd.testing.assert_frame_equal(actual, expected)

    @pytest.mark.parametrize(
        "kwarg, expected",
        [
            ("data", pd.DataFrame()),
            ("values", None),
            ("columns", None),
            ("base_index", None),
            ("extended_index", "cln_manufacturer_device_name"),
        ],
    )
    def test_empty_input_create_sum_table_call(
        self, mock_create_pivot_sum_table, empty_df, kwarg, expected
    ):
        """
        Test that the function handle an empty input correctly, passing only the data argument to
        create_pivot_sum_table and leaving the rest as None (allowing the function to use the
        default argument values).
        """
        summary_tables.create_device_summary_table(empty_df)

    @pytest.mark.parametrize(
        "input_data, expected",
        [
            (
                [("test", "test", "test", "test", "test", "test", 1)],
                pd.DataFrame(
                    columns=[
                        "nhs_england_region",
                        "der_provider_code",
                        "upd_high_level_device_type",
                        "rag_status",
                        "cln_manufacturer_device_name",
                        "test",
                    ],
                    data=[["test", "test", "test", "test", "test", 1]],
                ),
            ),
            (
                [
                    ("test", "test", "test", "test", "test", "test1", 1),
                    ("test", "test", "test", "test", "test", "test2", 2),
                ],
                pd.DataFrame(
                    columns=[
                        "nhs_england_region",
                        "der_provider_code",
                        "upd_high_level_device_type",
                        "rag_status",
                        "cln_manufacturer_device_name",
                        "test1",
                        "test2",
                    ],
                    data=[["test", "test", "test", "test", "test", 1, 2]],
                ),
            ),
            (
                [
                    ("test", "test", "test", "test", "test", "test1", 1),
                    ("test", "test", "test", "test", "test", "test1", 2),
                ],
                pd.DataFrame(
                    columns=[
                        "nhs_england_region",
                        "der_provider_code",
                        "upd_high_level_device_type",
                        "rag_status",
                        "cln_manufacturer_device_name",
                        "test1",
                    ],
                    data=[["test", "test", "test", "test", "test", 3]],
                ),
            ),
            (
                [
                    ("test", "test", "test", "test", "test", "test1", 1),
                    ("test", "test", "test", "test", "test", "test1", 2),
                    ("test", "test", "test", "test", "test", "test2", 3),
                    ("test", "test", "test", "test", "test", "test2", 4),
                ],
                pd.DataFrame(
                    columns=[
                        "nhs_england_region",
                        "der_provider_code",
                        "upd_high_level_device_type",
                        "rag_status",
                        "cln_manufacturer_device_name",
                        "test1",
                        "test2",
                    ],
                    data=[["test", "test", "test", "test", "test", 3, 7]],
                ),
            ),
        ],
    )
    def test_happy_path(self, input_data, expected):
        """
        Test that the function can handle normal inputs and return the output in the expected
        format.

        This technically repeats the tests from create_pivot_sum_table, but it is useful to ensure
        that the function works as expected and is well integrated with the create_pivot_sum_table.

        Cases include:
        - Single row with a single value to pivot
        - Multiple rows with different values to pivot
        - Multiple rows with the same value to pivot
        - Multiple rows with multiple values to pivot
        """
        input_df = pd.DataFrame(
            columns=[
                "nhs_england_region",
                "der_provider_code",
                "upd_high_level_device_type",
                "rag_status",
                "cln_manufacturer_device_name",
                "activity_date",
                "cln_total_cost",
            ],
            data=input_data,
        )

        actual = summary_tables.create_device_summary_table(input_df)

        pd.testing.assert_frame_equal(actual, expected)


if __name__ == "__main__":
    pytest.main([__file__])
