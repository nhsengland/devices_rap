"""
Tests for devices_rap/summary_tables.py
"""

import re

import loguru
import pandas as pd
import pytest

from devices_rap import summary_tables
from devices_rap.errors import ColumnsNotFoundError

# from devices_rap import summary_tables


pytestmark = pytest.mark.no_data_needed


@pytest.fixture
def mock_info(mocker):
    """
    Fixture to mock the loguru.logger.info method
    """
    return mocker.spy(loguru.logger, "info")


@pytest.fixture
def mock_error(mocker):
    """
    Fixture to mock the loguru.logger.error method
    """
    return mocker.spy(loguru.logger, "error")


@pytest.fixture
def mock_log_levels(mock_info, mock_error):
    """
    Fixture to mock the loguru.logger.info and loguru.logger.error methods
    """
    return mock_info, mock_error


# @pytest.fixture()
# def mock_pivot_table(mocker):
#     """
#     Fixture to mock the pd.pivot_table method
#     """
#     return mocker.spy(pd, "pivot_table")


@pytest.fixture
def empty_df():
    """
    Fixture to return an empty DataFrame
    """
    return pd.DataFrame()


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
                    "der_high_level_device_type",
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
                    "der_high_level_device_type",
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
                        "der_high_level_device_type",
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
                        "der_high_level_device_type",
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
                        "der_high_level_device_type",
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
                        "der_high_level_device_type",
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
                "der_high_level_device_type",
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
                "BASE_INDEX: ['der_high_level_device_type', 'der_provider_code', "
                "'nhs_england_region', 'rag_status']",
            ),
            (
                [
                    "nhs_england_region",
                    "der_provider_code",
                    "der_high_level_device_type",
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
                    "der_high_level_device_type",
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
                "BASE_INDEX: ['der_high_level_device_type', 'der_provider_code', "
                "'nhs_england_region', 'rag_status']",
            ),
        ],
    )
    def test_columns_not_found_error_raised(
        self, mock_log_levels, input_columns, expected_message
    ):
        """
        Test that the ColumnsNotFoundError is raised when the columns are not found in the dataset
        """
        mock_info, mock_error = mock_log_levels

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
                "['nhs_england_region', 'der_provider_code', 'der_high_level_device_type', 'rag_status']",
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


class TestCreateTableCuts:
    """
    Test class for summary.create_table_cuts
    """

    @pytest.fixture
    def test_input(self):
        """
        Fixture to return a test dataframe
        """
        columns = ["A", "B", "C", "D"]
        data = [
            (1, 1, 1, 1),
            (1, 1, 2, 2),
            (1, 2, 1, 3),
            (1, 2, 2, 4),
            (1, 1, 1, 5),
            (1, 1, 2, 6),
            (1, 2, 1, 7),
            (1, 2, 2, 8),
        ]
        return pd.DataFrame(columns=columns, data=data)

    def test_returns_dict(self, test_input):
        """
        Test that the function returns a dictionary
        """
        result = summary_tables.create_table_cuts(test_input, "A")
        assert isinstance(result, dict)

    def test_returns_dict_of_dataframes(self, test_input):
        """
        Test that the function returns a dictionary of DataFrames
        """
        result = summary_tables.create_table_cuts(test_input, "A")
        assert all(isinstance(value, pd.DataFrame) for value in result.values())

    @pytest.mark.parametrize(
        "cut_columns, expected",
        [
            (
                "A",
                {
                    1: pd.DataFrame(
                        columns=["A", "B", "C", "D"],
                        data=[
                            (1, 1, 1, 1),
                            (1, 1, 2, 2),
                            (1, 2, 1, 3),
                            (1, 2, 2, 4),
                            (1, 1, 1, 5),
                            (1, 1, 2, 6),
                            (1, 2, 1, 7),
                            (1, 2, 2, 8),
                        ],
                    )
                },
            ),
            (
                "B",
                {
                    1: pd.DataFrame(
                        columns=["A", "B", "C", "D"],
                        data=[
                            (1, 1, 1, 1),
                            (1, 1, 2, 2),
                            (1, 1, 1, 5),
                            (1, 1, 2, 6),
                        ],
                    ),
                    2: pd.DataFrame(
                        columns=["A", "B", "C", "D"],
                        data=[
                            (1, 2, 1, 3),
                            (1, 2, 2, 4),
                            (1, 2, 1, 7),
                            (1, 2, 2, 8),
                        ],
                    ),
                },
            ),
            (
                ["A", "B"],
                {
                    (1, 1): pd.DataFrame(
                        columns=["A", "B", "C", "D"],
                        data=[
                            (1, 1, 1, 1),
                            (1, 1, 2, 2),
                            (1, 1, 1, 5),
                            (1, 1, 2, 6),
                        ],
                    ),
                    (1, 2): pd.DataFrame(
                        columns=["A", "B", "C", "D"],
                        data=[
                            (1, 2, 1, 3),
                            (1, 2, 2, 4),
                            (1, 2, 1, 7),
                            (1, 2, 2, 8),
                        ],
                    ),
                },
            ),
        ],
    )
    def test_cuts(self, test_input, cut_columns, expected):
        """
        Test that the function can create the cuts correctly
        """
        actual = summary_tables.create_table_cuts(test_input, cut_columns)
        assert actual.keys() == expected.keys()

        failures = []
        for key, value in actual.items():
            try:
                actual_df = value.sort_values(by=value.columns.tolist()).reset_index(drop=True)
                expected_df = (
                    expected[key]
                    .sort_values(by=expected[key].columns.tolist())
                    .reset_index(drop=True)
                )
                pd.testing.assert_frame_equal(actual_df, expected_df)
            except AssertionError as fail:
                failures.append(fail)

        if failures:
            raise ExceptionGroup("Test failures", failures)

    def test_drop_cut_columns(self, test_input):
        """
        Test that the function can drop the cut columns from the DataFrame
        """
        actual = summary_tables.create_table_cuts(test_input, "A", drop_cut_columns=True)
        expected = {
            1: pd.DataFrame(
                columns=["B", "C", "D"],
                data=[
                    (1, 1, 1),
                    (1, 2, 2),
                    (2, 1, 3),
                    (2, 2, 4),
                    (1, 1, 5),
                    (1, 2, 6),
                    (2, 1, 7),
                    (2, 2, 8),
                ],
            )
        }

        failures = []
        for key, value in actual.items():
            try:
                actual_df = value.sort_values(by=value.columns.tolist()).reset_index(drop=True)
                expected_df = (
                    expected[key]
                    .sort_values(by=expected[key].columns.tolist())
                    .reset_index(drop=True)
                )
                pd.testing.assert_frame_equal(actual_df, expected_df)
            except AssertionError as fail:
                failures.append(fail)

        if failures:
            raise ExceptionGroup("Test failures", failures)

    @pytest.mark.parametrize(
        "cut_columns, expected_message",
        [
            ("E", "Columns were not found in the dataset. MISSING COLUMNS: CUT_COLUMNS: ['E']"),
            (
                ["A", "E"],
                "Columns were not found in the dataset. MISSING COLUMNS: CUT_COLUMNS: ['E']",
            ),
            (
                ["E", "F"],
                "Columns were not found in the dataset. MISSING COLUMNS: CUT_COLUMNS: ['E', 'F']",
            ),
        ],
    )
    def test_columns_not_found_error_raised(
        self, mock_log_levels, test_input, cut_columns, expected_message
    ):
        """
        Test that the ColumnsNotFoundError is raised when the columns are not found in the dataset
        """
        mock_info, mock_error = mock_log_levels

        with pytest.raises(ColumnsNotFoundError, match=re.escape(expected_message)):
            summary_tables.create_table_cuts(test_input, cut_columns)

        mock_info.assert_called_once()
        mock_error.assert_called_once_with(expected_message)

    @pytest.mark.parametrize(
        "input_cut_columns, expected_message",
        [
            (
                "A",
                "Creating a collection of tables based on the unique values in the cut_columns. "
                "CUT COLUMNS: A",
            ),
            (
                ["A"],
                "Creating a collection of tables based on the unique values in the cut_columns. "
                "CUT COLUMNS: ['A']",
            ),
            (
                ["A", "B"],
                "Creating a collection of tables based on the unique values in the cut_columns. "
                "CUT COLUMNS: ['A', 'B']",
            ),
        ],
    )
    def test_log_called(self, mock_info, test_input, input_cut_columns, expected_message):
        """
        Test that the loguru.logger is called
        """
        summary_tables.create_table_cuts(test_input, input_cut_columns)

        mock_info.assert_called_once_with(expected_message)


if __name__ == "__main__":
    pytest.main([__file__])
