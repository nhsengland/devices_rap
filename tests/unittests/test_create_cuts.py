"""
Tests for devices_rap/create_cuts.py
"""

import sys
import re
import pytest
import pandas as pd

from devices_rap import create_cuts
from devices_rap.errors import ColumnsNotFoundError

if sys.version_info < (3, 11):
    from exceptiongroup import ExceptionGroup  # type: ignore


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


class TestCreateRegionalTableCuts:
    """
    Tests for create_cuts.create_regional_table_cuts
    """

    @pytest.fixture
    def test_input(self):
        """
        Fixture to return a test dictionary of dataframes
        """
        columns = ["upd_region", "A", "B", "C"]
        data = [
            ("North", 1, 1, 1),
            ("North", 1, 2, 2),
            ("South", 1, 1, 3),
            ("South", 1, 2, 4),
        ]
        df = pd.DataFrame(columns=columns, data=data)
        return {
            "summary": df,
            "detailed": df,
        }

    @pytest.fixture
    def mock_create_table_cuts(self, mocker):
        """
        Fixture to mock the create_cuts.create_table_cuts function
        """
        columns = ["upd_region", "A", "B", "C"]
        north_data = [
            ("North", 1, 1, 1),
            ("North", 1, 2, 2),
        ]
        south_data = [
            ("South", 1, 1, 3),
            ("South", 1, 2, 4),
        ]
        return_value = {
            "North": pd.DataFrame(columns=columns, data=north_data),
            "South": pd.DataFrame(columns=columns, data=south_data),
        }
        return mocker.patch("devices_rap.create_cuts.create_table_cuts", return_value=return_value)

    def test_returns_dict(self, test_input, mock_create_table_cuts):
        """
        Test that the function returns a dictionary
        """
        result = create_cuts.create_regional_table_cuts(test_input)
        assert isinstance(result, dict)

    def test_returns_dict_of_dicts(self, test_input, mock_create_table_cuts):
        """
        Test that the function returns a dictionary of dictionaries
        """
        result = create_cuts.create_regional_table_cuts(test_input)
        assert all(isinstance(value, dict) for value in result.values())

    def test_keys_are_regions(self, test_input, mock_create_table_cuts):
        """
        Test that the keys of the returned dictionary are regions
        """
        result = create_cuts.create_regional_table_cuts(test_input)
        assert set(result.keys()) == {"North", "South"}

    def test_inner_keys_are_table_types(self, test_input, mock_create_table_cuts):
        """
        Test that the inner keys of the returned dictionary are table types
        """
        result = create_cuts.create_regional_table_cuts(test_input)
        for region_tables in result.values():
            assert set(region_tables.keys()) == {"summary", "detailed"}

    def test_inner_values_are_dataframes(self, test_input, mock_create_table_cuts):
        """
        Test that the inner values of the returned dictionary are DataFrames
        """
        result = create_cuts.create_regional_table_cuts(test_input)
        for region_tables in result.values():
            assert all(isinstance(df, pd.DataFrame) for df in region_tables.values())

    @pytest.mark.parametrize(
        "region, table_type, expected_df",
        [
            (
                "North",
                "summary",
                pd.DataFrame(
                    columns=["upd_region", "A", "B", "C"],
                    data=[
                        ("North", 1, 1, 1),
                        ("North", 1, 2, 2),
                    ],
                ),
            ),
            (
                "North",
                "detailed",
                pd.DataFrame(
                    columns=["upd_region", "A", "B", "C"],
                    data=[
                        ("North", 1, 1, 1),
                        ("North", 1, 2, 2),
                    ],
                ),
            ),
            (
                "South",
                "summary",
                pd.DataFrame(
                    columns=["upd_region", "A", "B", "C"],
                    data=[
                        ("South", 1, 1, 3),
                        ("South", 1, 2, 4),
                    ],
                ),
            ),
            (
                "South",
                "detailed",
                pd.DataFrame(
                    columns=["upd_region", "A", "B", "C"],
                    data=[
                        ("South", 1, 1, 3),
                        ("South", 1, 2, 4),
                    ],
                ),
            )
        ],
    )
    def test_correct_data_in_dataframes(
        self, test_input, mock_create_table_cuts, region, table_type, expected_df
    ):
        """
        Test that the data in the returned DataFrames is correct
        """
        actual_dict = create_cuts.create_regional_table_cuts(test_input)

        actual = actual_dict[region][table_type]

        actual_df = actual.sort_values(by=actual.columns.tolist()).reset_index(drop=True)
        expected_df = expected_df.sort_values(by=expected_df.columns.tolist()).reset_index(drop=True)

        pd.testing.assert_frame_equal(actual_df, expected_df)


if __name__ == "__main__":
    pytest.main([__file__])
