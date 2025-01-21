"""
Tests for devices_rap/create_cuts.py
"""

import re
import pytest
import pandas as pd

from devices_rap import create_cuts
from devices_rap.errors import ColumnsNotFoundError


@pytest.fixture
def mock_create_table_cuts(mocker):
    """
    Fixture to mock the create_cuts.create_table_cuts function
    """
    return mocker.patch("devices_rap.create_cuts.create_table_cuts", return_value={})


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
        mock_info, mock_error, _, _ = mock_log_levels

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


@pytest.mark.xfail()
class TestCreateRAGSummaryTables:
    """
    Tests for create_cuts.create_rag_summary_tables
    """

    def test_returns_dict(self, mock_create_table_cuts, empty_df):
        """
        Test that the function returns a dictionary
        """
        result = create_cuts.create_regional_rag_summary_tables_cuts(empty_df)
        assert isinstance(result, dict)

    def test_returns_dict_of_dataframes(self, mock_create_table_cuts, empty_df):
        """
        Test that the function returns a dictionary of DataFrames
        """
        mock_create_table_cuts.return_value = {
            "RAG1": pd.DataFrame(columns=["A", "B"], data=[(1, 1), (2, 2)]),
            "RAG2": pd.DataFrame(columns=["A", "B"], data=[(3, 3), (4, 4)]),
        }
        result = create_cuts.create_regional_rag_summary_tables_cuts(empty_df)
        assert all(isinstance(value, pd.DataFrame) for value in result.values())

    def test_calls_create_table_cuts(self, mock_create_table_cuts, empty_df):
        """
        Test that the function calls the create_table_cuts function
        """
        create_cuts.create_regional_rag_summary_tables_cuts(empty_df)
        mock_create_table_cuts.assert_called_once()

    def test_returns_correct_dataframes(self, mock_create_table_cuts, empty_df):
        """
        Test that the function returns the correct DataFrames
        """
        mock_create_table_cuts.return_value = {
            "RAG1": pd.DataFrame(columns=["A", "B"], data=[(1, 1), (2, 2)]),
            "RAG2": pd.DataFrame(columns=["A", "B"], data=[(3, 3), (4, 4)]),
        }

        result = create_cuts.create_regional_rag_summary_tables_cuts(empty_df)
        expected = {
            "RAG1": pd.DataFrame(columns=["A", "B"], data=[(1, 1), (2, 2)]),
            "RAG2": pd.DataFrame(columns=["A", "B"], data=[(3, 3), (4, 4)]),
        }

        assert result.keys() == expected.keys()

        failures = []
        for key, value in result.items():
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
        "kwarg, expected",
        [
            ("data", pd.DataFrame()),
            ("cut_columns", ["Region", "RAG Status"]),
            ("drop_cut_columns", None),
        ],
    )
    def test_calls_create_table_cuts_with_correct_args(
        self, mock_create_table_cuts, empty_df, kwarg, expected
    ):
        """
        Tests if the function calls create_table_cuts with the correct arguments
        """
        create_cuts.create_regional_rag_summary_tables_cuts(empty_df)

        actual = mock_create_table_cuts.call_args.kwargs.get(kwarg)

        if isinstance(expected, pd.DataFrame):
            pd.testing.assert_frame_equal(actual, expected)
        else:
            assert actual == expected

    def test_log_info(self, mock_info, empty_df, mock_create_table_cuts):
        """
        Test that the logger.info is called correctly
        """
        create_cuts.create_regional_rag_summary_tables_cuts(empty_df)
        mock_info.assert_called_once_with("Creating the Regional RAG summary tables")

    def test_log_success(self, mock_success, empty_df, mock_create_table_cuts):
        """
        Test that the logger.success is called correctly
        """
        mock_create_table_cuts.return_value = {
            "RAG1": pd.DataFrame(columns=["A", "B"], data=[(1, 1), (2, 2)]),
            "RAG2": pd.DataFrame(columns=["A", "B"], data=[(3, 3), (4, 4)]),
        }
        create_cuts.create_regional_rag_summary_tables_cuts(empty_df)
        mock_success.assert_called_once_with(
            "Created the collection of 2 Regional RAG summary tables"
        )


if __name__ == "__main__":
    pytest.main([__file__])
