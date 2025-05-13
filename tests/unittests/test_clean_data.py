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
        with pytest.raises(clean_data.NoDataProvidedError):
            clean_data.batch_normalise_column_names({"test": {}})

    def test_check_for_data_not_dataframe(self, mocker):
        """
        Test that the function raises an error when the data is not a DataFrame
        """
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
    def mock_called_functions(self, mocker, mock_info):
        """
        Fixture to mock the functions called by cleanse_master_data
        """
        mock_convert_fin_dates = mocker.patch(
            "devices_rap.clean_data.convert_fin_dates_vectorised",
            return_value="foo",
            autospec=True,
        )
        mock_convert_values_to = mocker.patch(
            "devices_rap.clean_data.convert_values_to", return_value="bar", autospec=True
        )
        mock_convert_to_numeric_column = mocker.patch(
            "devices_rap.clean_data.convert_to_numeric_column",
            return_value=pd.Series("bar"),
            autospec=True,
        )

        return (
            mock_convert_fin_dates,
            mock_convert_values_to,
            mock_info,
            mock_convert_to_numeric_column,
        )

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
                "cln_total_cost": ["test_cln_total_cost"],
            }
        )

    def test_covert_fin_datas_calls(self, test_master_df, mock_called_functions):
        """
        Test that the function applies the convert_fin_dates function correctly
        """
        mock_convert_fin_dates, _, _, _ = mock_called_functions
        clean_data.cleanse_master_data(test_master_df)
        assert mock_convert_fin_dates.call_count == 1

    def test_convert_values_to_calls(self, test_master_df, mock_called_functions):
        """
        Test that the function applies the convert_values_to function correctly
        """
        _, mock_convert_values_to, _, _ = mock_called_functions
        clean_data.cleanse_master_data(test_master_df)
        assert mock_convert_values_to.call_count == 2
        mock_convert_values_to.assert_called_with(
            "test_cln_activity_year", match=[2425], to=202425
        )

    def test_logger_calls(self, test_master_df, mock_called_functions):
        """
        Test that the function logs the expected messages
        """
        _, _, mock_info, _ = mock_called_functions
        clean_data.cleanse_master_data(test_master_df)
        assert mock_info.call_count == 5
        mock_info.assert_any_call("Cleaning the master dataset ready for processing")
        mock_info.assert_any_call("Converting high level device type values")
        mock_info.assert_any_call("Converting activity year values without century")
        mock_info.assert_any_call("Converting activity date values to datetime")
        mock_info.assert_any_call(
            "Converting total cost values to numeric, removing commas and converting to float"
        )

    def test_columns_not_found_error(self, mock_error):
        """
        Test that the function raises a ColumnsNotFoundError when the required columns are not present
        """
        with pytest.raises(clean_data.ColumnsNotFoundError):
            clean_data.cleanse_master_data(pd.DataFrame())

        mock_error.assert_called_once_with(
            "Columns were not found in the dataset. MISSING COLUMNS: CLEAN_COLUMNS: "
            "['cln_activity_year', 'cln_total_cost', 'der_high_level_device_type']"
        )


class TestCleanseMasterJoinedDataset:
    """
    Tests for clean_data.cleanse_master_joined_dataset
    """

    joined_df_columns = [
        "region",
        "nhs_england_region",
        "rag_status",
        "upd_high_level_device_type",
        "cln_manufacturer",
        "cln_manufacturer_device_name",
    ]

    @pytest.fixture
    def empty_joined_df(self):
        return pd.DataFrame(columns=self.joined_df_columns)

    def test_dataframe_returned(self, empty_joined_df):
        """
        Test that the function returns a DataFrame
        """
        actual = clean_data.cleanse_master_joined_dataset(empty_joined_df)
        expected_dtype = pd.DataFrame
        assert isinstance(actual, expected_dtype)

    @pytest.mark.parametrize(
        "input_data, expected_upd_region",
        [
            (("test1", "test2", "test", "test", "test", "test"), "test1"),
            ((None, "test2", "test", "test", "test", "test"), "test2"),
            (("test1", None, "test", "test", "test", "test"), "test1"),
            ((None, None, "test", "test", "test", "test"), None),
        ],
    )
    def test_consolidates_region_columns(self, input_data, expected_upd_region):
        """
        Test that the function consolidates region columns into a single column
        """
        input_df = pd.DataFrame(columns=self.joined_df_columns, data=[input_data])
        actual = clean_data.cleanse_master_joined_dataset(input_df)
        assert actual["upd_region"].values[0] == expected_upd_region

    def test_drops_unwanted_columns(self, empty_joined_df):
        """
        Test that the function drops unwanted columns
        """
        actual = clean_data.cleanse_master_joined_dataset(empty_joined_df)
        expected_columns = [
            "rag_status",
            "upd_high_level_device_type",
            "cln_manufacturer",
            "cln_manufacturer_device_name",
            "upd_region",
        ]
        assert list(actual.columns) == expected_columns

    @pytest.mark.parametrize(
        "input_data, expected_upd_region",
        [
            (("test1", "test2", "test", "test", "test", "test"), "test1"),
            (("&", None, "test", "test", "test", "test"), "and"),
            (("test1", "&", "test", "test", "test", "test"), "test1"),
            (("test&", "test2", "test", "test", "test", "test"), "testand"),
            (("test&1", "test2", "test", "test", "test", "test"), "testand1"),
        ],
    )
    def test_fixes_inconsistent_regions(self, input_data, expected_upd_region):
        """
        Test that the function fixes inconsistent region values
        """
        input_df = pd.DataFrame(columns=self.joined_df_columns, data=[input_data])
        actual = clean_data.cleanse_master_joined_dataset(input_df)
        assert actual["upd_region"].values[0] == expected_upd_region

    @pytest.mark.parametrize(
        "input_data, expected_rag_status",
        [
            (("test", "test", "test", None, "test", "test"), "test"),
            (("test", "test", None, "test", "test", "test"), "NULL"),
            (("test", "test", None, None, "test", "test"), "RED"),
            (("test", "test", "test", "test", "test", "test"), "test"),
        ],
    )
    def test_fills_missing_rag_status(self, input_data, expected_rag_status):
        """
        Test that the function fills missing rag_status values
        """
        input_df = pd.DataFrame(columns=self.joined_df_columns, data=[input_data])
        actual = clean_data.cleanse_master_joined_dataset(input_df)
        assert actual["rag_status"].values[0] == expected_rag_status

    @pytest.mark.parametrize(
        "input_data, expected_data",
        [
            (
                ("test", "test", "test", "test", "test", "test"),
                ("test", "test", "test", "test", "test"),
            ),
            (
                ("test", "test", "test", "test", "test", None),
                ("test", "test", "test", "NULL", "test"),
            ),
            (
                ("test", "test", "test", "test", None, None),
                ("test", "test", "NULL", "NULL", "test"),
            ),
            (("test", "test", "test", None, None, None), ("test", "NULL", "NULL", "NULL", "test")),
            (("test", "test", None, "test", None, None), ("NULL", "test", "NULL", "NULL", "test")),
            ((None, None, None, "test", None, None), ("NULL", "test", "NULL", "NULL", None)),
        ],
    )
    def test_fills_missing_values(self, input_data, expected_data):
        """
        Test that the function fills missing values
        """
        input_df = pd.DataFrame(columns=self.joined_df_columns, data=[input_data])
        actual = clean_data.cleanse_master_joined_dataset(input_df)
        expected_columns = [
            "rag_status",
            "upd_high_level_device_type",
            "cln_manufacturer",
            "cln_manufacturer_device_name",
            "upd_region",
        ]
        expected = pd.DataFrame(columns=expected_columns, data=[expected_data])

        pd.testing.assert_frame_equal(actual, expected)

    def test_columns_not_found_error(self, mock_error):
        """
        Test that the function raises a ColumnsNotFoundError when the required columns are not present
        """
        with pytest.raises(clean_data.ColumnsNotFoundError):
            clean_data.cleanse_master_joined_dataset(pd.DataFrame())

        mock_error.assert_called_once_with(
            "Columns were not found in the dataset. MISSING COLUMNS: CLEAN_COLUMNS: "
            "['cln_manufacturer', 'cln_manufacturer_device_name', 'nhs_england_region', "
            "'rag_status', 'region', 'upd_high_level_device_type']"
        )


class TestDropDuplicatesOnPriority:
    """
    Tests for clean_data.drop_duplicates_on_priority
    """

    exceptions_columns = ["provider_code", "dev_code", "rag_status"]

    @pytest.fixture
    def empty_exceptions_df(self):
        """
        Fixture to provide an empty exceptions DataFrame with the required columns
        """
        return pd.DataFrame(
            columns=self.exceptions_columns,
        )

    @pytest.fixture
    def default_kwargs(self):
        """
        Fixture to provide the default arguments for the drop_duplicates_on_priority function
        """
        return {
            "subset": ["provider_code", "dev_code"],
            "priority_column": "rag_status",
            "priority_order": ["AMBER", "RED", "YELLOW"],
        }

    @pytest.fixture
    def mock_check_duplicates(self, mocker):
        """
        Mock the check_duplicates function
        """
        return mocker.patch("devices_rap.clean_data.check_duplicates")

    def test_dataframe_returned(self, empty_exceptions_df, default_kwargs, mock_check_duplicates):
        """
        Test that the function returns a DataFrame
        """
        actual = clean_data.drop_duplicates_on_priority(empty_exceptions_df, **default_kwargs)
        expected_dtype = pd.DataFrame
        assert isinstance(actual, expected_dtype)

    @pytest.mark.parametrize(
        "input_data, expected_data",
        [
            (
                [
                    ("test1", "foo", "AMBER"),
                    ("test1", "foo", "RED"),
                ],
                [
                    ("test1", "foo", "AMBER"),
                ],
            ),
            (
                [
                    ("test2", "foo", "RED"),
                    ("test2", "foo", "YELLOW"),
                ],
                [
                    ("test2", "foo", "RED"),
                ],
            ),
            (
                [
                    ("test3", "foo", "A"),
                    ("test3", "foo", "B"),
                ],
                [
                    ("test3", "foo", "A"),
                ],
            ),
            (
                [
                    ("test4", "foo", "D"),
                    ("test4", "foo", "C"),
                ],
                [
                    ("test4", "foo", "C"),
                ],
            ),
            (
                [
                    ("test5", "foo", "E"),
                    ("test5", "bar", "E"),
                ],
                [
                    ("test5", "foo", "E"),
                    ("test5", "bar", "E"),
                ],
            ),
            (
                [
                    ("test6", "foo", "F"),
                    ("test6", "foo", "F"),
                ],
                [
                    ("test6", "foo", "F"),
                ],
            ),
        ],
    )
    def test_removes_duplicates(
        self, default_kwargs, mock_check_duplicates, input_data, expected_data
    ):
        """
        Test that the function removes duplicate exceptions with default rag_priorities
        """
        input_df = pd.DataFrame(columns=self.exceptions_columns, data=input_data)
        actual = clean_data.drop_duplicates_on_priority(input_df, **default_kwargs)
        expected = pd.DataFrame(columns=self.exceptions_columns, data=expected_data)
        pd.testing.assert_frame_equal(actual, expected)

    @pytest.mark.parametrize(
        "kwarg_name, kwarg_value, expected_data",
        (
            [
                ("subset", "test_column", [("test1", "foo", "AMBER", "bar")]),
                (
                    "subset",
                    ["provider_code", "dev_code", "test_column"],
                    [("test1", "foo", "AMBER", "bar"), ("test2", "foo", "RED", "bar")],
                ),
                (
                    "priority_column",
                    "test_column",
                    [("test1", "foo", "AMBER", "bar"), ("test2", "foo", "YELLOW", "bar")],
                ),
                (
                    "priority_order",
                    ["YELLOW", "RED", "AMBER"],
                    [
                        ("test2", "foo", "YELLOW", "bar"),
                        ("test1", "foo", "RED", "bar"),
                    ],
                ),
            ]
        ),
    )
    def test_removes_duplicates_with_different_kwargs(
        self, default_kwargs, mock_check_duplicates, kwarg_name, kwarg_value, expected_data
    ):
        """
        Test that the function removes duplicate exceptions with different kwargs
        """
        input_kwargs = default_kwargs.copy()
        input_kwargs[kwarg_name] = kwarg_value

        columns = self.exceptions_columns + ["test_column"]

        input_data = [
            ("test1", "foo", "AMBER", "bar"),
            ("test1", "foo", "RED", "bar"),
            ("test2", "foo", "YELLOW", "bar"),
            ("test2", "foo", "RED", "bar"),
        ]
        input_df = pd.DataFrame(columns=columns, data=input_data)

        actual = clean_data.drop_duplicates_on_priority(input_df, **input_kwargs)
        expected = pd.DataFrame(columns=columns, data=expected_data)

        pd.testing.assert_frame_equal(actual, expected)

    def test_columns_not_found_error(self, mock_error, default_kwargs):
        """
        Test that the function raises a ColumnsNotFoundError when the required columns are not present
        """
        with pytest.raises(clean_data.ColumnsNotFoundError):
            clean_data.drop_duplicates_on_priority(pd.DataFrame(), **default_kwargs)

        mock_error.assert_called_once_with(
            "Columns were not found in the dataset. MISSING COLUMNS: DROP_DUPLICATE_COLUMNS: "
            "['dev_code', 'provider_code', 'rag_status']"
        )

    def test_calls_check_duplicates_twice(self, mock_check_duplicates, default_kwargs):
        """
        Test that the function calls the check_duplicates function
        """
        input_data = [
            ("test1", "test1", "AMBER"),
            ("test1", "test1", "RED"),
            ("test2", "test1", "RED"),
            ("test2", "test1", "YELLOW"),
        ]
        input_df = pd.DataFrame(columns=self.exceptions_columns, data=input_data)
        clean_data.drop_duplicates_on_priority(input_df, **default_kwargs)

        assert mock_check_duplicates.call_count == 2

    @pytest.mark.parametrize("kwarg_to_check", ["data", "subset", "duplicate_severity"])
    @pytest.mark.parametrize(
        "call_count, kwargs",
        [
            (
                0,
                {
                    "data": pd.DataFrame(
                        columns=exceptions_columns,
                        data=[
                            ("test1", "test1", "AMBER"),
                            ("test1", "test1", "RED"),
                            ("test2", "test1", "RED"),
                            ("test2", "test1", "YELLOW"),
                        ],
                    ),
                    "subset": ["provider_code", "dev_code"],
                    "duplicate_severity": "INFO",
                },
            ),
            (
                1,
                {
                    "data": pd.DataFrame(
                        columns=exceptions_columns,
                        data=[
                            ("test1", "test1", "AMBER"),
                            ("test2", "test1", "RED"),
                        ],
                    ),
                    "subset": ["provider_code", "dev_code"],
                    "duplicate_severity": "ERROR",
                },
            ),
        ],
    )
    def test_check_calls_check_duplicates_kwargs(
        self, mock_check_duplicates, default_kwargs, kwarg_to_check, call_count, kwargs
    ):
        """
        Check that the first time that:
        - The data is input_data
        - The subset is ["provider_code", "dev_code"]
        - The duplicate_severity is INFO

        The second time that:
        - The data is input_data
        - The subset is ["provider_code", "dev_code"]
        - The duplicate_severity is ERROR
        """
        input_data = [
            ("test1", "test1", "AMBER"),
            ("test1", "test1", "RED"),
            ("test2", "test1", "RED"),
            ("test2", "test1", "YELLOW"),
        ]
        input_df = pd.DataFrame(columns=self.exceptions_columns, data=input_data)
        clean_data.drop_duplicates_on_priority(input_df, **default_kwargs)

        actual_kwargs = mock_check_duplicates.call_args_list[call_count].kwargs

        actual_kwarg = actual_kwargs[kwarg_to_check]
        expected_kwargs = kwargs[kwarg_to_check]

        if isinstance(expected_kwargs, pd.DataFrame):
            pd.testing.assert_frame_equal(actual_kwarg, expected_kwargs)
        else:
            assert actual_kwarg == expected_kwargs


class TestCleanseExceptions:
    """
    Tests for clean_data.cleanse_exceptions function
    """

    exceptions_columns = ["provider_code", "dev_code", "rag_status"]

    @pytest.fixture
    def empty_exceptions_df(self):
        """
        Fixture to provide an empty exceptions DataFrame with the required columns
        """
        return pd.DataFrame(
            columns=self.exceptions_columns,
        )

    @pytest.fixture
    def mock_convert_date_columns_to_datetime(self, mocker, empty_exceptions_df):
        """
        Mock the convert_date_columns_to_datetime function
        """
        return mocker.patch(
            "devices_rap.clean_data.convert_date_columns_to_datetime",
            return_value=empty_exceptions_df,
        )

    @pytest.fixture
    def mock_drop_duplicates_on_priority(self, mocker, empty_exceptions_df):
        """
        Mock the drop_duplicates_on_priority function
        """
        return mocker.patch(
            "devices_rap.clean_data.drop_duplicates_on_priority", return_value=empty_exceptions_df
        )

    def test_dataframe_returned(
        self,
        empty_exceptions_df,
        mock_convert_date_columns_to_datetime,
        mock_drop_duplicates_on_priority,
    ):
        """
        Test that the function returns a DataFrame
        """
        actual = clean_data.cleanse_exceptions(empty_exceptions_df)
        expected_dtype = pd.DataFrame
        assert isinstance(actual, expected_dtype)

    def test_calls_drop_duplicates_on_priority(
        self,
        empty_exceptions_df,
        mock_convert_date_columns_to_datetime,
        mock_drop_duplicates_on_priority,
    ):
        """
        Test that the function calls the drop_duplicates_on_priority function
        """
        clean_data.cleanse_exceptions(empty_exceptions_df)
        assert mock_drop_duplicates_on_priority.call_count == 1

    @pytest.mark.parametrize(
        "kwarg_name, expected_kwarg_value",
        (
            ("data", pd.DataFrame(columns=exceptions_columns, data=[["test1", "test1", "AMBER"]])),
            ("subset", ["provider_code", "dev_code"]),
            ("priority_column", "rag_status"),
            ("priority_order", ["AMBER", "RED", "YELLOW"]),
        ),
    )
    def test_calls_drop_duplicates_on_priority_kwargs(
        self,
        mock_convert_date_columns_to_datetime,
        mock_drop_duplicates_on_priority,
        kwarg_name,
        expected_kwarg_value,
    ):
        """
        Test that the function calls the drop_duplicates_on_priority function with the correct kwargs
        """
        input_df = pd.DataFrame(
            columns=self.exceptions_columns, data=[["test1", "test1", "AMBER"]]
        )
        mock_convert_date_columns_to_datetime.return_value = input_df
        clean_data.cleanse_exceptions(input_df)
        actual_kwargs = mock_drop_duplicates_on_priority.call_args.kwargs

        if isinstance(expected_kwarg_value, pd.DataFrame):
            pd.testing.assert_frame_equal(actual_kwargs[kwarg_name], expected_kwarg_value)
        else:
            assert actual_kwargs[kwarg_name] == expected_kwarg_value


class TestCheckDuplicates:
    """
    Tests for clean_data.check_duplicates function
    """

    @pytest.fixture
    def duplicate_df(self):
        """
        Returns a dataset with duplicate values
        """
        return pd.DataFrame(
            columns=["col1", "col2", "col3"],
            data=[
                ("test1", "test2", "test3"),
                ("test1", "test2", "test3"),
            ],
        )

    @pytest.fixture
    def no_duplicates_df(self):
        """
        Returns a dataset with no duplicate values
        """
        return pd.DataFrame(
            columns=["col1", "col2", "col3"],
            data=[
                ("test1", "test2", "test3"),
                ("test4", "test5", "test6"),
            ],
        )

    @pytest.fixture
    def one_column_duplicates_df(self):
        """
        Returns a dataset with duplicate values in one column
        """
        return pd.DataFrame(
            columns=["col1", "col2", "col3"],
            data=[
                ("test1", "test2", "test3"),
                ("test1", "test5", "test6"),
            ],
        )

    def test_raises_duplicate_data_error(self, mock_error, duplicate_df):
        """
        Test that the function raises a DuplicateDataError when duplicate values are found
        """
        with pytest.raises(clean_data.DuplicateDataError):
            clean_data.check_duplicates(duplicate_df, "ERROR")

        mock_error.assert_called_once_with("Found 2 duplicated rows in the dataset")

    def test_raises_no_error(self, mock_error, no_duplicates_df):
        """
        Test that the function does not raise an error when no duplicate values are found
        """
        clean_data.check_duplicates(no_duplicates_df, "ERROR")
        mock_error.assert_not_called()

    def test_raises_warning(self, mock_warning, duplicate_df):
        """
        Test that the function raises a warning when duplicate values are found
        """
        clean_data.check_duplicates(duplicate_df, "WARNING")
        mock_warning.assert_called_once_with("Found 2 duplicated rows in the dataset")

    def test_raises_no_warning(self, mock_warning, no_duplicates_df):
        """
        Test that the function does not raise a warning when no duplicate values are found
        """
        clean_data.check_duplicates(no_duplicates_df, "WARNING")
        mock_warning.assert_not_called()

    def test_logs_info(self, mock_info, duplicate_df):
        """
        Test that the function logs an info message when no duplicate values are found
        """
        clean_data.check_duplicates(duplicate_df, "INFO")
        mock_info.assert_called_once_with("Found 2 duplicated rows in the dataset")

    def test_logs_no_info(self, mock_info, no_duplicates_df):
        """
        Test that the function does not log an info message when duplicate values are found
        """
        clean_data.check_duplicates(no_duplicates_df, "INFO")
        mock_info.assert_not_called()

    def test_subset(self, mock_error, one_column_duplicates_df):
        """
        Test that the function raises a DuplicateDataError when duplicate values are found in a subset of columns
        """
        with pytest.raises(clean_data.DuplicateDataError):
            clean_data.check_duplicates(one_column_duplicates_df, "ERROR", subset=["col1"])

        mock_error.assert_called_once_with(
            "Found 2 duplicated rows in the dataset with subset columns: ['col1']"
        )


class TestConvertDateColumnsToDatetime:
    """
    Tests for clean_data.convert_date_columns_to_datetime
    """

    @pytest.fixture
    def test_dataframe(self):
        """
        Fixture to create a test DataFrame with date columns
        """
        return pd.DataFrame(
            {
                "date_col1": ["01/01/2023 12:00", "02/01/2023 12:00"],
                "date_col2": ["03/01/2023", "04/01/2023"],
                "excel_date_col": [44927, 44928],
                "non_date_col": ["test1", "test2"],
            }
        )

    @pytest.mark.parametrize(
        "data_columns, expected_data",
        (
            (
                ["date_col1"],
                {"date_col1": (pd.Timestamp("2023-01-01 12:00"), pd.Timestamp("2023-01-02 12:00"))},
            ),
            (
                ["date_col2"],
                {"date_col2": (pd.Timestamp("2023-01-03"), pd.Timestamp("2023-01-04"))},
            ),
            (
                ["excel_date_col"],
                {"excel_date_col": (pd.Timestamp("2023-01-01"), pd.Timestamp("2023-01-02"))},
            ),
        ),
    )
    def test_handles_dates_in_different_formats(self, test_dataframe, data_columns, expected_data):
        """
        Test that the function handles dates in different formats
        """
        actual = clean_data.convert_date_columns_to_datetime(test_dataframe, data_columns)[data_columns]
        expected = pd.DataFrame(expected_data)
        pd.testing.assert_frame_equal(actual, expected)

    def test_raises_columns_not_found_error(self, test_dataframe):
        """
        Test that the function raises ColumnsNotFoundError when a specified date column is missing
        """
        date_columns = ["missing_col"]
        with pytest.raises(clean_data.ColumnsNotFoundError) as exc_info:
            clean_data.convert_date_columns_to_datetime(test_dataframe, date_columns)

        assert "missing_col" in str(exc_info.value)

    def test_logs_conversion_process(self, test_dataframe, mock_info):
        """
        Test that the function logs the conversion process for each date column
        """
        date_columns = ["date_col1", "date_col2"]
        clean_data.convert_date_columns_to_datetime(test_dataframe, date_columns)

        mock_info.assert_any_call("Converting date_col1 values to datetime")
        mock_info.assert_any_call("Converting date_col2 values to datetime")
