"""
Tests for devices_rap/summary_tables.py
"""

import re

import pandas as pd
import pytest
from nhs_herbot.errors import ColumnsNotFoundError

from devices_rap import summary_tables

pytestmark = pytest.mark.no_data_needed


@pytest.fixture
def mock_create_pivot_sum_table(mocker, empty_df):
    """
    Mock the create_pivot_sum_table function
    """
    return mocker.patch("devices_rap.summary_tables.create_pivot_sum_table", return_value=empty_df)


@pytest.fixture
def mock_join_mini_tables(mocker, empty_df):
    """
    Mock the join_mini_tables function
    """
    return mocker.patch("devices_rap.summary_tables.join_mini_tables", return_value=empty_df)


@pytest.fixture()
def mock_calc_change_from_previous_month_column(mocker, empty_df):
    """
    Mock the calc_change_from_previous_month_column function
    """
    return mocker.patch(
        "devices_rap.summary_tables.calc_change_from_previous_month_column", return_value=empty_df
    )


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
                    "upd_region",
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
        "kwarg, input_value, actual_kwarg, expected",
        [
            ("values", ["test"], "values", ["test"]),
            ("columns", ["test"], "columns", ["test"]),
            ("base_index", ["test"], "index", ["test"]),
            (
                "extended_index",
                ["test"],
                "index",
                [
                    "upd_region",
                    "der_provider_code",
                    "upd_high_level_device_type",
                    "rag_status",
                    "test",
                ],
            ),
            (
                "extended_index",
                "test",
                "index",
                [
                    "upd_region",
                    "der_provider_code",
                    "upd_high_level_device_type",
                    "rag_status",
                    "test",
                ],
            ),
        ],
    )
    def test_non_default_values(
        self, mocker, empty_df, kwarg, input_value, actual_kwarg, expected
    ):
        """
        Test that the function can handle non-default values
        """
        mock_pivot_table = mocker.patch("pandas.pivot_table")
        summary_tables.create_pivot_sum_table(empty_df, **{kwarg: input_value})

        actual = mock_pivot_table.call_args.kwargs.get(actual_kwarg)

        assert actual == expected

    @pytest.mark.parametrize(
        "input_data, expected",
        [
            (
                [("test", "test", "test", "test", "test", 1)],
                pd.DataFrame(
                    columns=[
                        "upd_region",
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
                        "upd_region",
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
                        "upd_region",
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
                        "upd_region",
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
                "upd_region",
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
                "BASE_INDEX: ['der_provider_code', 'rag_status', 'upd_high_level_device_type', 'upd_region']",
            ),
            (
                [
                    "upd_region",
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
                    "upd_region",
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
                "BASE_INDEX: ['der_provider_code', 'rag_status', 'upd_high_level_device_type', 'upd_region']",
            ),
        ],
    )
    def test_columns_not_found_error_raised(
        self, mock_log_levels, input_columns, expected_message
    ):
        """
        Test that the ColumnsNotFoundError is raised when the columns are not found in the dataset
        """
        mock_info, mock_error = mock_log_levels["info"], mock_log_levels["error"]

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
                "Creating a pivot table with the sum of the values for the given columns. "
                "VALUES: cln_total_cost, COLUMNS: activity_date, INDEX: "
                "['upd_region', 'der_provider_code', 'upd_high_level_device_type', 'rag_status']",
            ),
            (
                {
                    "values": ["test"],
                    "columns": ["test"],
                    "base_index": ["test"],
                    "extended_index": ["test"],
                },
                "Creating a pivot table with the sum of the values for the given columns. "
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


class TestCalcChangeFromPreviousMonthColumn:
    """
    Tests for the summary_tables.calc_change_from_previous_month_column function
    """

    @pytest.fixture()
    def monthly_summary_table(self) -> pd.DataFrame:
        """
        Returns a dataframe with datetime columns and some data
        """
        data = {
            pd.Timestamp("2023-01-01"): [100, 200, 300],
            pd.Timestamp("2023-02-01"): [110, 210, 310],
            pd.Timestamp("2023-03-01"): [120, 220, 320],
        }
        df = pd.DataFrame(data)
        return df

    def test_default_columns(self, monthly_summary_table):
        """
        Test the calc_change_from_previous_month_column function with default columns
        """
        result_df = summary_tables.calc_change_from_previous_month_column(monthly_summary_table)
        expected_change = [10, 10, 10]
        assert list(result_df["change_from_previous_month"]) == expected_change

    def test_specified_columns(self, monthly_summary_table):
        """
        Test the calc_change_from_previous_month_column function with specified columns
        """
        result_df = summary_tables.calc_change_from_previous_month_column(
            monthly_summary_table,
            most_recent_col=pd.Timestamp("2023-02-01"),
            second_most_recent_col=pd.Timestamp("2023-01-01"),
        )
        expected_change = [10, 10, 10]
        assert list(result_df["change_from_previous_month"]) == expected_change

    def test_missing_columns(self, monthly_summary_table):
        """
        Test the calc_change_from_previous_month_column function with missing columns
        """
        match = re.escape(
            "Columns were not found in the dataset. MISSING COLUMNS: MOST_RECENT_COL: "
            "['non_existent_col']"
        )
        with pytest.raises(ColumnsNotFoundError, match=match):
            summary_tables.calc_change_from_previous_month_column(
                monthly_summary_table,
                most_recent_col="non_existent_col",
                second_most_recent_col=pd.Timestamp("2023-01-01"),
            )

    def test_with_nan_values(self):
        """
        Test the calc_change_from_previous_month_column function with NaN values
        """
        data = {
            pd.Timestamp("2023-01-01"): [100, None, 300],
            pd.Timestamp("2023-02-01"): [110, 210, None],
        }
        df = pd.DataFrame(data)
        result_df = summary_tables.calc_change_from_previous_month_column(df)
        expected_change = [10, 210, -300]
        assert list(result_df["change_from_previous_month"]) == expected_change


class TestCreateDeviceCategorySummaryTable:
    """
    Test class for summary_tables.create_device_category_summary_table
    """

    def test_returns_dataframe(
        self,
        mocker,
        empty_df,
        mock_create_pivot_sum_table,
        mock_calc_change_from_previous_month_column,
    ):
        """
        Tests that the create_device_category_summary_table function returns a DataFrame
        """
        result = summary_tables.create_device_category_summary_table(empty_df)
        assert isinstance(result, pd.DataFrame)

    def test_calls_create_pivot_sum_table(
        self,
        mocker,
        empty_df,
        mock_create_pivot_sum_table,
        mock_calc_change_from_previous_month_column,
    ):
        """
        Tests that the create_device_category_summary_table function calls create_pivot_sum_table
        """
        summary_tables.create_device_category_summary_table(empty_df)
        mock_create_pivot_sum_table.assert_called_once_with(data=empty_df)

    def test_calls_calc_change_from_previous_month_column(
        self,
        mocker,
        empty_df,
        mock_create_pivot_sum_table,
        mock_calc_change_from_previous_month_column,
    ):
        """
        Tests that the create_device_category_summary_table function calls calc_change_from_previous_month_column
        """
        summary_tables.create_device_category_summary_table(empty_df)
        mock_calc_change_from_previous_month_column.assert_called_once_with(empty_df)


class TestCreateDeviceSummaryTable:
    """
    Test class for summary_tables.create_device_summary_table
    """

    def test_returns_dataframe(self, mocker, empty_df, mock_create_pivot_sum_table):
        """
        Tests that the create_device_summary_table function returns a DataFrame
        """
        result = summary_tables.create_device_summary_table(empty_df)
        assert isinstance(result, pd.DataFrame)

    def test_calls_create_pivot_sum_table(self, mocker, empty_df, mock_create_pivot_sum_table):
        """
        Tests that the create_device_summary_table function calls create_pivot_sum_table
        """
        summary_tables.create_device_summary_table(empty_df)
        mock_create_pivot_sum_table.assert_called_once_with(
            data=empty_df,
            extended_index=["cln_manufacturer", "cln_manufacturer_device_name"],
        )
