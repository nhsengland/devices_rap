"""
Tests for devices_rap/create_cuts.py
"""

import re
import pytest
import pandas as pd

from devices_rap import create_cuts
from devices_rap.errors import ColumnsNotFoundError


class TestCreateTableCuts:
    """
    Test class for create_cuts.create_table_cuts
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
        result = create_cuts.create_table_cuts(test_input, "A")
        assert isinstance(result, dict)

    def test_returns_dict_of_dataframes(self, test_input):
        """
        Test that the function returns a dictionary of DataFrames
        """
        result = create_cuts.create_table_cuts(test_input, "A")
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
        actual = create_cuts.create_table_cuts(test_input, cut_columns)
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
        actual = create_cuts.create_table_cuts(test_input, "A", drop_cut_columns=True)
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
            create_cuts.create_table_cuts(test_input, cut_columns)

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
        create_cuts.create_table_cuts(test_input, input_cut_columns)

        mock_info.assert_called_once_with(expected_message)
