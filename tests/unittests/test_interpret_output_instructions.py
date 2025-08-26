"""
Tests for the interpret_output_instructions module.
"""

import re

import pandas as pd
import pytest
from nhs_herbot.errors import ColumnsNotFoundError, DataSetNotFoundError

from devices_rap import interpret_output_instructions as instructions


class TestFilterData:
    """
    Tests for the interpret_output_instructions.filter_data function.
    """

    def test_returns_dataframe(self):
        """
        Test that the function returns a DataFrame.
        """
        data = pd.DataFrame(columns=["a", "b"], data=[[1, 2], [3, 4]])
        result = instructions.filter_data(data, {"a": [2]})
        assert isinstance(result, pd.DataFrame)

    def test_empty_dataframe(self):
        """
        Test that the function returns an empty DataFrame when the input is empty.
        """
        data = pd.DataFrame(columns=["a", "b"])
        result = instructions.filter_data(data, {"a": [2]})
        assert result.empty

    def test_no_filter(self):
        """
        Test that the function returns the input DataFrame when no filter is provided.
        """
        data = pd.DataFrame(columns=["a", "b"], data=[[1, 2], [3, 4]])
        result = instructions.filter_data(data, {})

        pd.testing.assert_frame_equal(result, data)

    def test_single_filter(self):
        """
        Test that the function filters the data correctly when a single filter is provided.
        """
        data = pd.DataFrame(columns=["a", "b"], data=[[1, 2], [3, 4]])
        result = instructions.filter_data(data, {"a": [1]})
        expected = pd.DataFrame(columns=["a", "b"], data=[[1, 2]])

        pd.testing.assert_frame_equal(result, expected)

    def test_multiple_filters(self):
        """
        Test that the function filters the data correctly when multiple filters are provided.
        """
        data = pd.DataFrame(columns=["a", "b"], data=[[1, 2], [3, 4], [1, 5]])
        result = instructions.filter_data(data, {"a": [1], "b": [2]})
        expected = pd.DataFrame(columns=["a", "b"], data=[[1, 2]])

        pd.testing.assert_frame_equal(result, expected)

    def test_filter_not_in_data(self):
        """
        Test that the function returns an empty DataFrame when the filter is not in the data.
        """
        data = pd.DataFrame(columns=["a", "b"], data=[[1, 2], [3, 4]])
        match = "Columns were not found in the dataset. MISSING COLUMNS: FILTER_COLUMNS: ['c']"
        with pytest.raises(
            ColumnsNotFoundError,
            match=re.escape(match),
        ):
            instructions.filter_data(data, {"c": [1]})

    def test_filter_multiple_values(self):
        """
        Test that the function filters the data correctly when multiple values are provided for a filter.
        """
        data = pd.DataFrame(columns=["a", "b"], data=[[1, 2], [3, 4], [1, 5]])
        result = instructions.filter_data(data, {"a": [1, 3]})
        pd.testing.assert_frame_equal(result, data)


class TestAddSubtotals:
    """
    Tests for the interpret_output_instructions.add_subtotals function.
    """

    @pytest.fixture
    def input_df(self):
        """
        Input data for the tests.
        """
        columns = ["column1", "column2", "column3"]
        data = [
            ("foo", "bar", 1),
            ("foo", "baz", 2),
            ("foo", "baz", 3),
            ("qux", "bar", 4),
            ("qux", "baz", 5),
        ]
        return pd.DataFrame(columns=columns, data=data)

    def test_returns_dataframe(self, input_df):
        """
        Test that the function returns a DataFrame.
        """
        result = instructions.add_subtotals(worksheet_data=input_df, subtotal_columns=["column1"])
        assert isinstance(result, pd.DataFrame)

    def test_empty_dataframe(self):
        """
        Test that the function returns an empty DataFrame when the input is empty.
        """
        data = pd.DataFrame(columns=["column1", "column2", "column3"])
        result = instructions.add_subtotals(data, ["column1"])
        assert result.empty

    @pytest.mark.parametrize(
        "subtotal_columns, expected_data",
        [
            (
                ["column1"],
                [
                    ("foo", "bar", 1),
                    ("foo", "baz", 2),
                    ("foo", "baz", 3),
                    ("qux", "bar", 4),
                    ("qux", "baz", 5),
                    ("foo Total", None, 6),
                    ("qux Total", None, 9),
                ],
            ),
            (
                ["column2"],
                [
                    ("foo", "bar", 1),
                    ("foo", "baz", 2),
                    ("foo", "baz", 3),
                    ("qux", "bar", 4),
                    ("qux", "baz", 5),
                    (None, "bar Total", 5),
                    (None, "baz Total", 10),
                ],
            ),
            (
                ["column1", "column2"],
                [
                    ("foo", "bar", 1),
                    ("foo", "baz", 2),
                    ("foo", "baz", 3),
                    ("qux", "bar", 4),
                    ("qux", "baz", 5),
                    ("foo Total", None, 6),
                    ("qux Total", None, 9),
                    ("foo", "bar Total", 1),
                    ("foo", "baz Total", 5),
                    ("qux", "bar Total", 4),
                    ("qux", "baz Total", 5),
                ],
            ),
        ],
    )
    def test_adding(self, input_df, subtotal_columns, expected_data):
        """
        Test that the function adds subtotals correctly for a single subtotal column.
        """

        result = instructions.add_subtotals(input_df, subtotal_columns)
        expected = pd.DataFrame(columns=["column1", "column2", "column3"], data=expected_data)
        pd.testing.assert_frame_equal(result, expected)

    def test_sort_columns(self, input_df):
        """
        Test that the function sorts the DataFrame correctly after adding subtotals.
        """
        result = instructions.add_subtotals(
            input_df, ["column1"], sort_columns=["column1", "column2"]
        )
        expected = pd.DataFrame(
            columns=["column1", "column2", "column3"],
            data=[
                ("foo", "bar", 1),
                ("foo", "baz", 2),
                ("foo", "baz", 3),
                ("foo Total", None, 6),
                ("qux", "bar", 4),
                ("qux", "baz", 5),
                ("qux Total", None, 9),
            ],
        )
        pd.testing.assert_frame_equal(result, expected)

    def test_subtotal_column_not_in_data(self):
        """
        Test that the function raises ColumnsNotFoundError when the subtotal column is not in the data.
        """
        data = pd.DataFrame(columns=["a", "b"], data=[[1, 2], [3, 4]])
        match = "Columns were not found in the dataset. MISSING COLUMNS: SUBTOTAL_COLUMNS: ['c']"
        with pytest.raises(
            ColumnsNotFoundError,
            match=re.escape(match),
        ):
            instructions.add_subtotals(data, ["c"])

    def test_sort_column_not_in_data(self, input_df):
        """
        Test that the function raises ColumnsNotFoundError when the sort column is not in the data.
        """
        match = "Columns were not found in the dataset. MISSING COLUMNS: SORT_COLUMNS: ['c']"
        with pytest.raises(
            ColumnsNotFoundError,
            match=re.escape(match),
        ):
            instructions.add_subtotals(input_df, subtotal_columns=["column1"], sort_columns=["c"])


class TestHandleDatetimeColumns:
    """
    Tests for the interpret_output_instructions.handle_datetime_columns function.
    """

    @pytest.fixture
    def input_df(self):
        """
        Input data for the tests.
        """
        columns = ["column1", 2, pd.Timestamp("2021-01-01"), pd.Timestamp("2021-02-01"), "column4"]
        data = [
            ("foo", 1, 1, 2, 4),
            ("bar", 3, 3, 4, 5),
        ]
        return pd.DataFrame(columns=columns, data=data)

    @pytest.fixture
    def mock_get_datetime_columns(self, mocker):
        """
        Mock the get_datetime_columns function.
        """
        return_values = [pd.Timestamp("2021-01-01"), pd.Timestamp("2021-02-01")]

        return mocker.patch(
            "devices_rap.interpret_output_instructions.get_datetime_columns",
            return_value=return_values,
        )

    def test_empty_dataframe(self, empty_df, mock_get_datetime_columns):
        """
        Test that the function returns an empty DataFrame when the input is empty.
        """
        result, _ = instructions.handle_datetime_columns(empty_df, {"datetime_column": None})

        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_empty_worksheet_format(self, input_df, mock_get_datetime_columns):
        """
        Test that the function returns the input DataFrame when the worksheet format is None.
        """
        result_df, result_dict = instructions.handle_datetime_columns(input_df, {})

        assert isinstance(result_df, pd.DataFrame)
        assert not result_dict

    def test_worksheet_data_not_altered(self, input_df, mock_get_datetime_columns):
        """
        Test that the function does not alter the input DataFrame.
        """
        result_df, _ = instructions.handle_datetime_columns(input_df, {"datetime_columns": None})

        pd.testing.assert_frame_equal(result_df, input_df)

    def test_get_datetime_columns_called(self, input_df, mock_get_datetime_columns):
        """
        Test that the get_datetime_columns function is called with the correct arguments.
        """
        instructions.handle_datetime_columns(input_df, {"datetime_columns": None})

        mock_get_datetime_columns.assert_called_once()

        actual = mock_get_datetime_columns.call_args[0][0]

        pd.testing.assert_frame_equal(actual, input_df)

    def test_custom_formating(self, input_df, mock_get_datetime_columns):
        """
        Test that the function formats the datetime columns correctly.
        """
        _, result_dict = instructions.handle_datetime_columns(
            input_df, {"datetime_columns": "%Y-%m-%d"}
        )

        expected_dict = {
            pd.Timestamp("2021-01-01"): "2021-01-01",
            pd.Timestamp("2021-02-01"): "2021-02-01",
        }

        assert result_dict == expected_dict

    def test_worksheet_columns_updated(self, input_df, mock_get_datetime_columns):
        """
        Test that the function updates the worksheet columns correctly.
        """
        worksheet_columns = {
            "column1": "column1",
            "datetime_columns": None,
            "column4": "column4",
        }
        _, actual = instructions.handle_datetime_columns(input_df, worksheet_columns)

        expected = {
            "column1": "column1",
            pd.Timestamp("2021-01-01"): "Jan 2021",
            pd.Timestamp("2021-02-01"): "Feb 2021",
            "column4": "column4",
        }

        assert actual == expected


class TestOrderColumns:
    """
    Tests for the interpret_output_instructions.order_columns function.
    """

    @pytest.fixture
    def input_df(self):
        """
        Input data for the tests.
        """
        columns = ["column1", "column2", "column3"]
        data = [
            ("foo", "bar", 1),
            ("foo", "baz", 2),
            ("foo", "baz", 3),
        ]
        return pd.DataFrame(columns=columns, data=data)

    def test_empty_dataframe_with_columns(self):
        """
        Test that the function returns an empty DataFrame when the input is empty.
        """
        data = pd.DataFrame(columns=["a", "b"])
        result = instructions.order_columns(data, worksheet_columns={"a": "", "b": ""})
        assert result.empty

    def test_orders_columns(self, input_df):
        """
        Test that the function orders the columns correctly.
        """
        worksheet_columns = {
            "column3": "",
            "column1": "",
            "column2": "",
        }
        result = instructions.order_columns(input_df, worksheet_columns=worksheet_columns)
        expected = pd.DataFrame(
            columns=["column3", "column1", "column2"],
            data=[
                (1, "foo", "bar"),
                (2, "foo", "baz"),
                (3, "foo", "baz"),
            ],
        )

        pd.testing.assert_frame_equal(result, expected)

    def test_empty_worksheet_columns(self, input_df):
        """
        Test that the function returns the input DataFrame when the worksheet columns are empty.
        """
        result = instructions.order_columns(input_df, worksheet_columns={})
        expected = pd.DataFrame(columns=[], data=[(), (), ()])
        pd.testing.assert_frame_equal(result, expected)

    def test_columns_not_found_error(self, input_df):
        """
        Test that the function raises ColumnsNotFoundError when the worksheet columns are missing.
        """
        match = "Columns were not found in the dataset. MISSING COLUMNS: COLUMN_ORDER: ['column4']"
        with pytest.raises(
            ColumnsNotFoundError,
            match=re.escape(match),
        ):
            instructions.order_columns(input_df, worksheet_columns={"column4": ""})

    def test_drops_columns(self, input_df):
        """
        Test that the function drops columns that are not in the worksheet columns.

        This is technically tested for in test_empty_worksheet_columns, but this test is more
        explicit
        """
        result = instructions.order_columns(input_df, worksheet_columns={"column1": ""})
        expected = pd.DataFrame(
            columns=["column1"],
            data=[
                ("foo",),
                ("foo",),
                ("foo",),
            ],
        )

        pd.testing.assert_frame_equal(result, expected)


class TestRenameColumns:
    """
    Tests for the interpret_output_instructions.rename_columns function.
    """

    def test_empty_dataframe(self, empty_df):
        """
        Test that the function returns an empty DataFrame when the input is empty.
        """
        result = instructions.rename_columns(empty_df, worksheet_columns={})
        assert result.empty

    def test_empty_worksheet_columns(self):
        """
        Test that the function returns the input DataFrame when the worksheet columns are empty.
        """
        data = pd.DataFrame(columns=["a", "b"])
        result = instructions.rename_columns(data, worksheet_columns={})
        pd.testing.assert_frame_equal(result, data)

    def test_columns_not_found_error(self):
        """
        Test that the function raises ColumnsNotFoundError when the worksheet columns are missing.
        """
        data = pd.DataFrame(columns=["a", "b"])
        match = "Columns were not found in the dataset. MISSING COLUMNS: COLUMN_RENAME: ['c']"
        with pytest.raises(
            ColumnsNotFoundError,
            match=re.escape(match),
        ):
            instructions.rename_columns(data, worksheet_columns={"c": "d"})

    def test_renames_columns(self):
        """
        Test that the function renames the columns correctly.
        """
        data = pd.DataFrame(columns=["a", "b"], data=[[1, 2], [3, 4]])
        result = instructions.rename_columns(data, worksheet_columns={"a": "c", "b": "d"})
        expected = pd.DataFrame(columns=["c", "d"], data=[[1, 2], [3, 4]])
        pd.testing.assert_frame_equal(result, expected)

    def test_renames_one_column(self):
        """
        Test that the function renames a single column correctly.
        """
        data = pd.DataFrame(columns=["a", "b"], data=[[1, 2], [3, 4]])
        result = instructions.rename_columns(data, worksheet_columns={"a": "c"})
        expected = pd.DataFrame(columns=["c", "b"], data=[[1, 2], [3, 4]])
        pd.testing.assert_frame_equal(result, expected)


class TestRoundData:
    """
    Tests for the interpret_output_instructions.round_data function.
    """

    def test_empty_dataframe(self, empty_df):
        """
        Test that the function returns an empty DataFrame when the input is empty.
        """
        result = instructions.round_data(empty_df, decimals=0)
        assert result.empty

    @pytest.mark.parametrize(
        "decimals, expected_data",
        [
            (0, [[1, 2], [3, 4]]),
            (1, [[1.0, 2.0], [3.0, 4.0]]),
            (2, [[1.00, 2.00], [3.00, 4.00]]),
        ],
    )
    def test_rounds_data(self, decimals, expected_data):
        """
        Test that the function rounds the data correctly.
        """
        data = pd.DataFrame(columns=["a", "b"], data=[[1.001, 2.001], [3.001, 4.001]])
        result = instructions.round_data(data, decimals=decimals)
        expected = pd.DataFrame(columns=["a", "b"], data=expected_data)
        pd.testing.assert_frame_equal(result, expected, check_dtype=False)

    def test_mixed_data_types(self):
        """
        Test that the function rounds the data correctly when the data types are mixed.
        """
        data = pd.DataFrame(columns=["a", "b"], data=[["1.001", 2.001], [3, 4.001]])
        result = instructions.round_data(data, decimals=2)
        expected = pd.DataFrame(columns=["a", "b"], data=(["1.001", 2.00], [3.00, 4.00]))
        pd.testing.assert_frame_equal(result, expected)


class TestProcessWorksheet:
    """
    Test for the interpret_output_instructions.process_worksheet function.
    """

    @pytest.fixture
    def worksheet_config(self):
        """
        Fixture for worksheet_config parameter.
        """
        return {
            "type": "test",
            "columns": {
                "column1": "COL1",
                "datetime_columns": "%Y-%m-%d",
                "column5": "COL5",
            },
            "filters": {"column1": ["foo"]},
            "sub-totals": ["column1"],
            "round_to": 2,
        }

    @pytest.fixture
    def datasets(self):
        """
        Fixture for datasets parameter.
        """
        columns = [
            "column1",
            "column2",
            pd.Timestamp("2021-01-01"),
            pd.Timestamp("2021-02-01"),
            "column5",
        ]
        data = [
            ("foo", "bar", 1, 2, 4),
            ("foo", "baz", 3, 4, 5),
            ("foo", "baz", 5, 6, 7),
            ("qux", "bar", 7, 8, 9),
            ("qux", "baz", 9, 10, 11),
        ]
        return {"test": pd.DataFrame(columns=columns, data=data)}

    @pytest.fixture
    def mock_filter_data(self, mocker):
        """
        Mock the filter_data function.
        """
        return_value = pd.DataFrame(
            columns=[
                "column1",
                "column2",
                pd.Timestamp("2021-01-01"),
                pd.Timestamp("2021-02-01"),
                "column5",
            ],
            data=[
                ("foo", "bar", 1, 2, 4),
                ("foo", "baz", 3, 4, 5),
                ("foo", "baz", 5, 6, 7),
            ],
        )
        return mocker.patch(
            "devices_rap.interpret_output_instructions.filter_data", return_value=return_value
        )

    @pytest.fixture
    def mock_add_subtotals(self, mocker):
        """
        Mock the add_subtotals function.
        """
        return_value = pd.DataFrame(
            columns=[
                "column1",
                "column2",
                pd.Timestamp("2021-01-01"),
                pd.Timestamp("2021-02-01"),
                "column5",
            ],
            data=[
                ("foo", "bar", 1, 2, 4),
                ("foo", "baz", 3, 4, 5),
                ("foo", "baz", 5, 6, 7),
                ("foo Total", None, 9, 12, 16),
            ],
        )
        return mocker.patch(
            "devices_rap.interpret_output_instructions.add_subtotals", return_value=return_value
        )

    @pytest.fixture
    def mock_handle_datetime_columns(self, mocker):
        """
        Mock the handle_datetime_columns function.
        """
        return_value = (
            pd.DataFrame(
                columns=[
                    "column1",
                    "column2",
                    pd.Timestamp("2021-01-01"),
                    pd.Timestamp("2021-02-01"),
                    "column5",
                ],
                data=[
                    ("foo", "bar", 1, 2, 4),
                    ("foo", "baz", 3, 4, 5),
                    ("foo", "baz", 5, 6, 7),
                    ("foo Total", None, 9, 12, 16),
                ],
            ),
            {
                "column1": "COL1",
                pd.Timestamp("2021-01-01"): "2021-01-01",
                pd.Timestamp("2021-02-01"): "2021-02-01",
                "column5": "COL5",
            },
        )
        return mocker.patch(
            "devices_rap.interpret_output_instructions.handle_datetime_columns",
            return_value=return_value,
        )

    @pytest.fixture
    def mock_order_columns(self, mocker):
        """
        Mock the order_columns function.
        """
        return_value = pd.DataFrame(
            columns=[
                "column1",
                pd.Timestamp("2021-01-01"),
                pd.Timestamp("2021-02-01"),
                "column5",
            ],
            data=[
                ("foo", 1, 2, 4),
                ("foo", 3, 4, 5),
                ("foo", 5, 6, 7),
                ("foo Total", 9, 12, 16),
            ],
        )

        return mocker.patch(
            "devices_rap.interpret_output_instructions.order_columns", return_value=return_value
        )

    @pytest.fixture
    def mock_rename_columns(self, mocker):
        """
        Mock the rename_columns function.
        """
        return_value = pd.DataFrame(
            columns=[
                "COL1",
                "2021-01-01",
                "2021-02-01",
                "COL5",
            ],
            data=[
                ("foo", 1, 2, 4),
                ("foo", 3, 4, 5),
                ("foo", 5, 6, 7),
                ("foo Total", 9, 12, 16),
            ],
        )
        return mocker.patch(
            "devices_rap.interpret_output_instructions.rename_columns", return_value=return_value
        )

    @pytest.fixture
    def mock_round_data(self, mocker):
        """
        Mock the round_data function.
        """
        return_value = pd.DataFrame(
            columns=[
                "COL1",
                "2021-01-01",
                "2021-02-01",
                "COL5",
            ],
            data=[
                ("foo", 1.00, 2.00, 4.00),
                ("foo", 3.00, 4.00, 5.00),
                ("foo", 5.00, 6.00, 7.00),
                ("foo Total", 9.00, 12.00, 16.00),
            ],
        )
        return mocker.patch(
            "devices_rap.interpret_output_instructions.round_data", return_value=return_value
        )

    @pytest.fixture
    def mock_the_functions(
        self,
        mock_filter_data,
        mock_add_subtotals,
        mock_handle_datetime_columns,
        mock_order_columns,
        mock_rename_columns,
        mock_round_data,
    ):
        """
        Mock all the functions.
        """
        return {
            "filter_data": mock_filter_data,
            "add_subtotals": mock_add_subtotals,
            "handle_datetime_columns": mock_handle_datetime_columns,
            "order_columns": mock_order_columns,
            "rename_columns": mock_rename_columns,
            "round_data": mock_round_data,
        }

    def test_returns_dataframe(self, worksheet_config, datasets):
        """
        Test that the function returns a DataFrame.
        """
        result = instructions.process_worksheet(worksheet_config, datasets)
        assert isinstance(result, pd.DataFrame)

    def test_empty_dataframe_input_dataframe_empty(
        self,
        worksheet_config,
        datasets,
    ):
        """
        Test that the function returns an empty DataFrame when the input dataframe is empty.
        """
        datasets["test"] = pd.DataFrame(
            columns=[
                "column1",
                "column2",
                pd.Timestamp("2021-01-01"),
                pd.Timestamp("2021-02-01"),
                "column5",
            ]
        )
        result = instructions.process_worksheet(worksheet_config, datasets)
        assert result.empty

    def test_empty_dataframe_only_type_in_config(
        self,
        worksheet_config,
        datasets,
    ):
        """
        Test that the function returns an empty dataset when only the type is provided in the config.
        """
        worksheet_config = {"type": "test"}
        result = instructions.process_worksheet(worksheet_config, datasets)
        assert result.empty

    def test_dataset_not_found_error(self, worksheet_config, datasets):
        """
        Test that the function raises KeyError when the dataset is not found.
        """
        worksheet_config["type"] = "non_existent_dataset"
        match = re.escape(
            "The dataset specified in the worksheet configuration, non_existent_dataset, was not"
            " found in the datasets: ['test']"
        )
        with pytest.raises(DataSetNotFoundError, match=match):
            instructions.process_worksheet(worksheet_config, datasets)

    # {
    #     "filter_data": mock_filter_data,
    #     "add_subtotals": mock_add_subtotals,
    #     "handle_datetime_columns": mock_handle_datetime_columns,
    #     "order_columns": mock_order_columns,
    #     "rename_columns": mock_rename_columns,
    #     "round_data": mock_round_data,
    # }

    @pytest.mark.parametrize(
        "function, kwarg, expected",
        [
            (
                "filter_data",
                "worksheet_data",
                pd.DataFrame(
                    columns=[
                        "column1",
                        "column2",
                        pd.Timestamp("2021-01-01"),
                        pd.Timestamp("2021-02-01"),
                        "column5",
                    ],
                    data=[
                        ("foo", "bar", 1, 2, 4),
                        ("foo", "baz", 3, 4, 5),
                        ("foo", "baz", 5, 6, 7),
                        ("qux", "bar", 7, 8, 9),
                        ("qux", "baz", 9, 10, 11),
                    ],
                ),
            ),
            ("filter_data", "worksheet_filters", {"column1": ["foo"]}),
            (
                "add_subtotals",
                "worksheet_data",
                pd.DataFrame(
                    columns=[
                        "column1",
                        "column2",
                        pd.Timestamp("2021-01-01"),
                        pd.Timestamp("2021-02-01"),
                        "column5",
                    ],
                    data=[
                        ("foo", "bar", 1, 2, 4),
                        ("foo", "baz", 3, 4, 5),
                        ("foo", "baz", 5, 6, 7),
                    ],
                ),
            ),
            ("add_subtotals", "subtotal_columns", ["column1"]),
            (
                "handle_datetime_columns",
                "worksheet_data",
                pd.DataFrame(
                    columns=[
                        "column1",
                        "column2",
                        pd.Timestamp("2021-01-01"),
                        pd.Timestamp("2021-02-01"),
                        "column5",
                    ],
                    data=[
                        ("foo", "bar", 1, 2, 4),
                        ("foo", "baz", 3, 4, 5),
                        ("foo", "baz", 5, 6, 7),
                        ("foo Total", None, 9, 12, 16),
                    ],
                ),
            ),
            (
                "handle_datetime_columns",
                "worksheet_columns",
                {
                    "column1": "COL1",
                    "datetime_columns": "%Y-%m-%d",
                    "column5": "COL5",
                },
            ),
            (
                "order_columns",
                "worksheet_data",
                pd.DataFrame(
                    columns=[
                        "column1",
                        "column2",
                        pd.Timestamp("2021-01-01"),
                        pd.Timestamp("2021-02-01"),
                        "column5",
                    ],
                    data=[
                        ("foo", "bar", 1, 2, 4),
                        ("foo", "baz", 3, 4, 5),
                        ("foo", "baz", 5, 6, 7),
                        ("foo Total", None, 9, 12, 16),
                    ],
                ),
            ),
            (
                "order_columns",
                "worksheet_columns",
                {
                    "column1": "COL1",
                    pd.Timestamp("2021-01-01"): "2021-01-01",
                    pd.Timestamp("2021-02-01"): "2021-02-01",
                    "column5": "COL5",
                },
            ),
            (
                "rename_columns",
                "worksheet_data",
                pd.DataFrame(
                    columns=[
                        "column1",
                        pd.Timestamp("2021-01-01"),
                        pd.Timestamp("2021-02-01"),
                        "column5",
                    ],
                    data=[
                        ("foo", 1, 2, 4),
                        ("foo", 3, 4, 5),
                        ("foo", 5, 6, 7),
                        ("foo Total", 9, 12, 16),
                    ],
                ),
            ),
            (
                "rename_columns",
                "worksheet_columns",
                {
                    "column1": "COL1",
                    pd.Timestamp("2021-01-01"): "2021-01-01",
                    pd.Timestamp("2021-02-01"): "2021-02-01",
                    "column5": "COL5",
                },
            ),
            (
                "round_data",
                "worksheet_data",
                pd.DataFrame(
                    columns=[
                        "COL1",
                        "2021-01-01",
                        "2021-02-01",
                        "COL5",
                    ],
                    data=[
                        ("foo", 1, 2, 4),
                        ("foo", 3, 4, 5),
                        ("foo", 5, 6, 7),
                        ("foo Total", 9, 12, 16),
                    ],
                ),
            ),
            ("round_data", "decimals", 2),
        ],
    )
    def test_filters_called_correctly(
        self,
        worksheet_config,
        datasets,
        mock_the_functions,
        function,
        kwarg,
        expected,
    ):
        """
        Test that the filter_data function is called correctly.
        """
        instructions.process_worksheet(worksheet_config, datasets)
        mock = mock_the_functions[function]
        mock.assert_called_once()
        actual = mock.call_args.kwargs[kwarg]

        if isinstance(expected, pd.DataFrame):
            pd.testing.assert_frame_equal(actual, expected)
        else:
            assert actual == expected

    def test_add_subtotals_not_called(
        self,
        worksheet_config,
        datasets,
        mock_filter_data,
        mock_add_subtotals,
        mock_handle_datetime_columns,
        mock_order_columns,
        mock_rename_columns,
        mock_round_data,
    ):
        """
        Test that the add_subtotals function is not called when subtotal_columns is not provided.
        """
        worksheet_config.pop("sub-totals")
        instructions.process_worksheet(worksheet_config, datasets)
        mock_add_subtotals.assert_not_called()


class TestProcessRegion:
    """
    Tests for the interpret_output_instructions.process_region function.
    """

    @pytest.fixture
    def mock_process_worksheet(self, mocker):
        """
        Mock the process_worksheet function.
        """
        return mocker.patch(
            "devices_rap.interpret_output_instructions.process_worksheet",
            return_value=pd.DataFrame(),
        )

    def test_returns_dict(self, mock_process_worksheet):
        """
        Test that the function returns a Dictionary.
        """
        result = instructions.process_region(
            region="test", datasets={"test": pd.DataFrame()}, instructions={"test": {}}
        )
        assert isinstance(result, dict)

    def test_returns_dict_of_dataframes(self, mock_process_worksheet):
        """
        Test that the function returns a dictionary of DataFrames.
        """
        result = instructions.process_region(
            region="test", datasets={"test": pd.DataFrame()}, instructions={"test": {}}
        )
        assert all(isinstance(value, pd.DataFrame) for value in result.values())

    def test_empty_instruction(self, mock_process_worksheet):
        """
        Test that the function returns an empty DataFrame when the instruction is empty.
        """
        result = instructions.process_region(
            region="test", datasets={"test": pd.DataFrame()}, instructions={}
        )
        assert result == {}

    def test_process_worksheet_called(self, mock_process_worksheet):
        """
        Test that the process_worksheet function is called with the correct arguments.
        """
        instructions.process_region(
            region="test", datasets={"test": pd.DataFrame()}, instructions={"test": {}}
        )

        mock_process_worksheet.assert_called_once()

    def test_process_worksheet_not_called(self, mock_process_worksheet):
        """
        Test that the process_worksheet function is not called when the instructions are empty.
        """
        instructions.process_region(region="test", datasets={}, instructions={})
        mock_process_worksheet.assert_not_called()

    @pytest.mark.parametrize(
        "call_no, message",
        (
            (
                0,
                "Interpreting output instructions for the test region",
            ),
            (
                1,
                "Processing the test worksheet for the test region",
            ),
        ),
    )
    def test_loggers(self, mock_info, mock_process_worksheet, call_no, message):
        """
        Test that the logger is called with the correct message.
        """
        instructions.process_region(
            region="test", datasets={"test": pd.DataFrame()}, instructions={"test": {}}
        )
        actual_message = mock_info.call_args_list[call_no].args[0]
        assert actual_message == message


class TestInterpretOutputInstructions:
    """
    Tests for the interpret_output_instructions.interpret_output_instructions function.
    """

    @pytest.fixture
    def mock_process_region(self, mocker):
        """
        Mock the process_region function.
        """
        return mocker.patch(
            "devices_rap.interpret_output_instructions.process_region",
            return_value={"test": pd.DataFrame()},
        )

    @pytest.fixture
    def mock_pipeline_config(self, mocker):
        """
        Mock the pipeline_config function.
        """
        return mocker.MagicMock()

    def test_logger_called(self, mock_info, mock_pipeline_config, mock_process_region):
        """
        Test that the logger is called with the correct message.
        """
        instructions.interpret_output_instructions(
            pipeline_config=mock_pipeline_config, region_cuts={"test": {"test": pd.DataFrame()}}
        )
        actual_message = mock_info.call_args.args[0]
        assert actual_message == "Interpreting output instructions for each region"

    def test_returns_dict(self, mock_info, mock_pipeline_config, mock_process_region):
        """
        Test that the function returns a Dictionary.
        """
        result = instructions.interpret_output_instructions(
            pipeline_config=mock_pipeline_config, region_cuts={"test": {"test": pd.DataFrame()}}
        )
        assert isinstance(result, dict)

    def test_returns_dict_of_dicts(self, mock_info, mock_pipeline_config, mock_process_region):
        """
        Test that the function returns a dictionary of dictionaries.
        """
        result = instructions.interpret_output_instructions(
            pipeline_config=mock_pipeline_config, region_cuts={"test": {"test": pd.DataFrame()}}
        )
        assert all(isinstance(value, dict) for value in result.values())

    def test_process_region_called(self, mock_info, mock_pipeline_config, mock_process_region):
        """
        Test that the process_region function is called with the correct arguments.
        """
        mock_pipeline_config.amber_report_output_instructions = {"test": {}}
        instructions.interpret_output_instructions(
            pipeline_config=mock_pipeline_config, region_cuts={"test": {}}
        )

        mock_process_region.assert_called_once()
        actual_args = mock_process_region.call_args.args
        assert actual_args == ("test", {}, {"test": {}})

    def test_process_region_not_called(self, mock_info, mock_pipeline_config, mock_process_region):
        """
        Test that the process_region function is not called when the instructions are empty.
        """
        instructions.interpret_output_instructions(
            pipeline_config=mock_pipeline_config, region_cuts={}
        )
        mock_process_region.assert_not_called()
