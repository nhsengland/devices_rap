"""
Tests for the devices_rap/exception_notes.py module.
"""

import re
import pytest
import pandas as pd
from devices_rap import exception_notes
from devices_rap.errors import ColumnsNotFoundError


class TestColumnSummaryNotes:
    """
    Tests for the column_summary_notes function.
    """

    def test_return_type(self):
        """
        Tests that the function returns a pandas Series.
        """
        row = pd.Series({"col1": "Y", "col2": "N", "col3": "Ceased"})
        columns_to_summarise = {"col1": "Note 1", "col2": "Note 2", "col3": "Note 3"}
        match_summaries = {"Group 1": "Y", "Group 2": "Ceased"}

        actual = exception_notes.column_summary_notes(row, columns_to_summarise, match_summaries)
        assert isinstance(actual, pd.Series)

    def test_return_columns(self):
        """
        Tests that the function returns a Series with the correct index.
        """
        row = pd.Series({"col1": "Y", "col2": "N", "col3": "Ceased"})
        columns_to_summarise = {"col1": "Note 1", "col2": "Note 2", "col3": "Note 3"}
        match_summaries = {"Group 1": "Y", "Group 2": "Ceased"}

        actual = exception_notes.column_summary_notes(row, columns_to_summarise, match_summaries)
        assert actual.index.tolist() == ["summary"]

    def test_all_matches(self):
        """
        Tests that the function returns the correct summary for a row with all matches.
        """
        row = pd.Series({"col1": "Y", "col2": "N", "col3": "Ceased"})
        columns_to_summarise = {"col1": "Note 1", "col2": "Note 2", "col3": "Note 3"}
        match_summaries = {"Group 1": "Y", "Group 2": "Ceased"}

        actual = exception_notes.column_summary_notes(row, columns_to_summarise, match_summaries)
        expected = pd.Series(["Group 1: Note 1. Group 2: Note 3."], index=["summary"], dtype="string")

        pd.testing.assert_series_equal(actual, expected)

    def test_no_matches(self):
        """
        Tests that the function returns an empty summary for a row with no matches.
        """
        row = pd.Series({"col1": "N", "col2": "N", "col3": "N"})
        columns_to_summarise = {"col1": "Note 1", "col2": "Note 2", "col3": "Note 3"}
        match_summaries = {"Group 1": "Y", "Group 2": "Ceased"}

        actual = exception_notes.column_summary_notes(row, columns_to_summarise, match_summaries)
        expected = pd.Series([None], index=["summary"], dtype="string")

        pd.testing.assert_series_equal(actual, expected)

    def test_partial_matches(self):
        """
        Tests that the function returns the correct summary for a row with partial matches.
        """
        row = pd.Series({"col1": "Y", "col2": "N", "col3": "N"})
        columns_to_summarise = {"col1": "Note 1", "col2": "Note 2", "col3": "Note 3"}
        match_summaries = {"Group 1": "Y", "Group 2": "Ceased"}

        actual = exception_notes.column_summary_notes(row, columns_to_summarise, match_summaries)
        expected = pd.Series(["Group 1: Note 1."], index=["summary"], dtype="string")

        pd.testing.assert_series_equal(actual, expected)

    def test_column_not_found_error(self, mock_error):
        """
        Tests that the function raises a ColumnsNotFoundError if a column is not found in the row.
        """
        row = pd.Series({"col1": "Y", "col2": "N"})
        columns_to_summarise = {"col1": "Note 1", "col2": "Note 2", "col3": "Note 3"}
        match_summaries = {"Group 1": "Y", "Group 2": "Ceased"}

        expected_message = (
            "Columns were not found in the dataset. MISSING COLUMNS: MATCH_COLUMNS: ['col3']"
        )

        with pytest.raises(ColumnsNotFoundError, match=re.escape(expected_message)):
            exception_notes.column_summary_notes(row, columns_to_summarise, match_summaries)

        mock_error.assert_called_once_with(expected_message)

    def test_logger_not_called(self, mock_info):
        """
        Tests that the logger is not called if the function runs successfully.
        """
        row = pd.Series({"col1": "Y", "col2": "N", "col3": "Ceased"})
        columns_to_summarise = {"col1": "Note 1", "col2": "Note 2", "col3": "Note 3"}
        match_summaries = {"Group 1": "Y", "Group 2": "Ceased"}

        exception_notes.column_summary_notes(row, columns_to_summarise, match_summaries)

        mock_info.assert_not_called()


class TestCreateExceptionsNotes:
    """
    Tests for the exception_notes.create_exception_notes function.
    """

    @pytest.fixture
    def input_exceptions(self):
        """
        Fixture to create a sample exceptions DataFrame.
        """
        return pd.DataFrame(
            columns=[
                "exception_status_legacy_list",
                "exception_status_planned_migration",
                "exception_status_category_list",
                "exception_status_product_list",
                "exception_status_hcted_category",
                "exception_status_stock_<180_days",
            ],
            data=[
                (
                    "Y",
                    "Y",
                    "Y",
                    "Y",
                    "Y",
                    "Y",
                ),
                (
                    "Ceased",
                    "Ceased",
                    "Ceased",
                    "Ceased",
                    "Ceased",
                    "Ceased",
                ),
                (
                    "N",
                    "N",
                    "N",
                    "N",
                    "N",
                    "N",
                ),
                (
                    "Y",
                    "Ceased",
                    "N",
                    "N",
                    "N",
                    "N",
                ),
                (
                    "Y",
                    "Y",
                    "Ceased",
                    "Ceased",
                    "N",
                    "N",
                ),
            ],
        )

    def test_returns_dataframe(self, input_exceptions):
        """
        Tests that the function returns a pandas DataFrame.
        """

        actual = exception_notes.create_exception_notes(input_exceptions)
        assert isinstance(actual, pd.DataFrame)

    @pytest.mark.parametrize(
        "drop_columns, expected_columns",
        [
            (True, ["exception_notes"]),
            (
                False,
                [
                    "exception_status_legacy_list",
                    "exception_status_planned_migration",
                    "exception_status_category_list",
                    "exception_status_product_list",
                    "exception_status_hcted_category",
                    "exception_status_stock_<180_days",
                    "exception_notes",
                ],
            ),
        ],
    )
    def test_returns_correct_columns(self, input_exceptions, drop_columns, expected_columns):
        """
        Tests that the function returns a DataFrame with the correct columns.
        """

        actual = exception_notes.create_exception_notes(input_exceptions, drop_columns=drop_columns)
        assert actual.columns.tolist() == expected_columns

    def test_returns_correct_values(self, input_exceptions):
        """
        Tests that the function returns a DataFrame with the correct values.
        """
        result = exception_notes.create_exception_notes(input_exceptions)
        expected_values = [
            "Exceptions: Legacy List, Planned Migration, Category List, Product List, Hcted Category, Stock <180 Days.",
            "Ceased: Legacy List, Planned Migration, Category List, Product List, Hcted Category, Stock <180 Days.",
            None,
            "Exceptions: Legacy List. Ceased: Planned Migration.",
            "Exceptions: Legacy List, Planned Migration. Ceased: Category List, Product List.",
        ]

        actual = result["exception_notes"]
        expected = pd.Series(expected_values, name="exception_notes", dtype="string")

        pd.testing.assert_series_equal(actual, expected)

    def test_logger_called(self, input_exceptions, mock_info):
        """
        Tests that the logger is called when the function runs successfully.
        """
        exception_notes.create_exception_notes(input_exceptions)
        mock_info.assert_called_once_with("Creating exception notes column")


if __name__ == "__main__":
    pytest.main([__file__])
