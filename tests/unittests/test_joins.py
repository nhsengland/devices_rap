"""
Tests for devices_rap/joins.py
"""

import pandas as pd
import pytest
from loguru import logger
from nhs_herbot.errors import ColumnsNotFoundError

from devices_rap import joins


pytestmark = pytest.mark.no_data_needed


class TestJoinWrapperFunctions:
    """
    Tests for joins.join_provider_codes_lookup, joins.join_device_taxonomy,
    and joins.join_exceptions.

    Note: These tests are not exhaustive as the functions are wrappers around join_datasets.
    End-to-end tests are required to ensure that the functions work as expected.
    """

    functions = [
        joins.join_provider_codes_lookup,
        joins.join_device_taxonomy,
        joins.join_exceptions,
    ]

    @pytest.mark.parametrize(
        "func, drop_columns",
        zip(functions, [["org_code"], ["dev_code"], ["dev_code", "provider_code"]]),
    )
    def test_returns_dataframe(self, mocker, func, drop_columns):
        """
        Test that the function returns a DataFrame.
        """
        mocker.patch(
            "devices_rap.joins.join_datasets", return_value=pd.DataFrame(columns=drop_columns)
        )
        actual = func(pd.DataFrame(), pd.DataFrame())
        assert isinstance(actual, pd.DataFrame)

    expected_messages = [
        "Joining the provider_codes_lookup table onto the master_devices table",
        "Joining the device_taxonomy table onto the master_devices table",
        "Joining the exceptions table onto the master_devices table",
    ]

    @pytest.mark.parametrize("func, expected_message", zip(functions, expected_messages))
    def test_logging(self, mocker, func, expected_message):
        """
        Test that the function logs the correct message.
        """
        mock_logger = mocker.spy(logger, "info")
        mocker.patch("devices_rap.joins.join_datasets")

        func(pd.DataFrame(), pd.DataFrame())

        mock_logger.assert_called_once_with(expected_message)

    @pytest.mark.parametrize("func", functions)
    def test_calls_join_datasets(self, mocker, func):
        """
        Test that the function calls join_datasets.
        """
        mock_join_datasets = mocker.patch("devices_rap.joins.join_datasets")

        func(pd.DataFrame(), pd.DataFrame())

        mock_join_datasets.assert_called_once()

    expected_kwargs = [
        {
            "left": pd.DataFrame({"left": [1, 2, 3]}),
            "right": pd.DataFrame({"right": [1, 2, 3]}),
            "left_on": "der_provider_code",
            "right_on": "org_code",
            "validate": "many_to_one",
        },
        {
            "left": pd.DataFrame({"left": [1, 2, 3]}),
            "right": pd.DataFrame({"right": [1, 2, 3]}),
            "left_on": "upd_high_level_device_type",
            "right_on": "dev_code",
            "validate": "many_to_one",
        },
        {
            "left": pd.DataFrame({"left": [1, 2, 3]}),
            "right": pd.DataFrame({"right": [1, 2, 3]}),
            "left_on": ["upd_high_level_device_type", "der_provider_code"],
            "right_on": ["dev_code", "provider_code"],
            "validate": "many_to_many",
        },
    ]

    @pytest.mark.parametrize("func, expected_kwargs", zip(functions, expected_kwargs))
    @pytest.mark.parametrize(
        "kwarg",
        [
            "left",
            "right",
            "left_on",
            "right_on",
            "validate",
        ],
    )
    def test_calls_join_datasets_correctly(self, mocker, func, expected_kwargs, kwarg):
        """
        Test that the function calls join_datasets with the correct arguments.
        """
        mock_join_datasets = mocker.patch("devices_rap.joins.join_datasets")

        func(pd.DataFrame({"left": [1, 2, 3]}), pd.DataFrame({"right": [1, 2, 3]}))

        actual = mock_join_datasets.call_args.kwargs[kwarg]
        expected = expected_kwargs[kwarg]

        if isinstance(expected, pd.DataFrame):
            assert isinstance(actual, pd.DataFrame)
            pd.testing.assert_frame_equal(actual, expected)
        else:
            assert actual == expected

    def test_call_join_exceptions_strict(self, mocker):
        """
        Test that the function calls join_datasets with the correct arguments when strict_validate
        is True.
        """
        mock_join_datasets = mocker.patch("devices_rap.joins.join_datasets")

        joins.join_exceptions(
            pd.DataFrame({"left": [1, 2, 3]}),
            pd.DataFrame({"right": [1, 2, 3]}),
            strict_validate=True,
        )

        actual = mock_join_datasets.call_args.kwargs["validate"]
        expected = "many_to_one"

        assert actual == expected


class TestJoinMiniProviderCodesLookup:
    """
    Tests for joins.join_mini_provider_codes_lookup
    """

    @pytest.fixture
    def master_devices(self):
        """
        Return a master_devices DataFrame for testing.
        """
        return pd.DataFrame(
            columns=["upd_high_level_device_type", "der_provider_code"],
            data=[("type1", "code1"), ("type2", "code2"), ("type3", "code3")],
        )

    @pytest.fixture
    def provider_codes_lookup(self):
        """
        Return a provider_codes_lookup DataFrame for testing.
        """
        return pd.DataFrame(
            columns=["org_code", "current_name_in_proper_case"],
            data=[("code1", "name1"), ("code2", "name2"), ("code3", "name3")],
        )

    def test_returns_dataframe(self, master_devices, provider_codes_lookup, mocker):
        """
        Test that the function returns a DataFrame.
        """
        mocker.patch(
            "devices_rap.joins.join_provider_codes_lookup",
            return_value=pd.DataFrame(
                columns=["der_provider_code", "current_name_in_proper_case"]
            ),
        )
        actual = joins.join_mini_provider_codes_lookup(master_devices, provider_codes_lookup)
        assert isinstance(actual, pd.DataFrame)

    def test_logging(self, master_devices, provider_codes_lookup, mocker):
        """
        Test that the function logs the correct message.
        """
        mock_logger = mocker.spy(logger, "info")
        mocker.patch("devices_rap.joins.join_provider_codes_lookup")

        joins.join_mini_provider_codes_lookup(master_devices, provider_codes_lookup)

        mock_logger.assert_called_once_with(
            "Reducing the provider_codes_lookup table down to only join on the required columns: ['org_code', 'current_name_in_proper_case']"
        )

    def test_calls_join_provider_codes_lookup(self, master_devices, provider_codes_lookup, mocker):
        """
        Test that the function calls join_provider_codes_lookup.
        """
        mock_join_provider_codes_lookup = mocker.patch(
            "devices_rap.joins.join_provider_codes_lookup"
        )

        joins.join_mini_provider_codes_lookup(master_devices, provider_codes_lookup)

        mock_join_provider_codes_lookup.assert_called_once()

    def test_raises_columns_not_found_error(self, master_devices, mocker):
        """
        Test that the function raises ColumnsNotFoundError when required columns are not present.
        """
        provider_codes_lookup = pd.DataFrame(columns=["wrong_column", "another_wrong_column"])

        with pytest.raises(ColumnsNotFoundError):
            joins.join_mini_provider_codes_lookup(master_devices, provider_codes_lookup)

    def test_correct_columns_passed_to_join_provider_codes_lookup(self, master_devices, mocker):
        """
        Test that the correct columns are passed to join_provider_codes_lookup.
        """
        provider_codes_lookup = pd.DataFrame(
            columns=["org_code", "current_name_in_proper_case", "extra_column"],
            data=[
                ("code1", "name1", "extra1"),
                ("code2", "name2", "extra2"),
                ("code3", "name3", "extra3"),
            ],
        )
        expected_provider_codes_lookup = pd.DataFrame(
            columns=["org_code", "current_name_in_proper_case"],
            data=[("code1", "name1"), ("code2", "name2"), ("code3", "name3")],
        )

        mock_join_provider_codes_lookup = mocker.patch(
            "devices_rap.joins.join_provider_codes_lookup"
        )

        joins.join_mini_provider_codes_lookup(master_devices, provider_codes_lookup)

        actual = mock_join_provider_codes_lookup.call_args.kwargs["provider_codes_lookup"]
        pd.testing.assert_frame_equal(actual, expected_provider_codes_lookup)


class TestJoinMiniDeviceTaxonomy:
    """
    Tests for joins.join_mini_device_taxonomy
    """

    @pytest.fixture
    def master_devices(self):
        """
        Return a master_devices DataFrame for testing.
        """
        return pd.DataFrame(
            columns=["upd_high_level_device_type", "der_provider_code"],
            data=[("type1", "code1"), ("type2", "code2"), ("type3", "code3")],
        )

    @pytest.fixture
    def device_taxonomy(self):
        """
        Return a device_taxonomy DataFrame for testing.
        """
        return pd.DataFrame(
            columns=[
                "dev_code",
                "description_in_title_case",
                "upd_migrated_categories",
                "upd_non_migrated_categories",
            ],
            data=[
                ("type1", "desc1", "migrated1", "non_migrated1"),
                ("type2", "desc2", "migrated2", "non_migrated2"),
                ("type3", "desc3", "migrated3", "non_migrated3"),
            ],
        )

    def test_returns_dataframe(self, master_devices, device_taxonomy, mocker):
        """
        Test that the function returns a DataFrame.
        """
        mocker.patch(
            "devices_rap.joins.join_device_taxonomy",
            return_value=pd.DataFrame(
                columns=[
                    "dev_code",
                    "description_in_title_case",
                    "upd_migrated_categories",
                    "upd_non_migrated_categories",
                ]
            ),
        )
        actual = joins.join_mini_device_taxonomy(master_devices, device_taxonomy)
        assert isinstance(actual, pd.DataFrame)

    def test_logging(self, master_devices, device_taxonomy, mocker):
        """
        Test that the function logs the correct message.
        """
        mock_logger = mocker.spy(logger, "info")
        mocker.patch("devices_rap.joins.join_device_taxonomy")

        joins.join_mini_device_taxonomy(master_devices, device_taxonomy)

        mock_logger.assert_called_once_with(
            "Reducing the device_taxonomy table down to only join on the required columns: "
            "['dev_code', 'description_in_title_case', 'upd_migrated_categories', "
            "'upd_non_migrated_categories']"
        )

    def test_calls_join_device_taxonomy(self, master_devices, device_taxonomy, mocker):
        """
        Test that the function calls join_device_taxonomy.
        """
        mock_join_device_taxonomy = mocker.patch("devices_rap.joins.join_device_taxonomy")

        joins.join_mini_device_taxonomy(master_devices, device_taxonomy)

        mock_join_device_taxonomy.assert_called_once()

    def test_raises_columns_not_found_error(self, master_devices, mocker):
        """
        Test that the function raises ColumnsNotFoundError when required columns are not present.
        """
        device_taxonomy = pd.DataFrame(columns=["wrong_column", "another_wrong_column"])

        with pytest.raises(ColumnsNotFoundError):
            joins.join_mini_device_taxonomy(master_devices, device_taxonomy)

    def test_correct_columns_passed_to_join_device_taxonomy(
        self, 
        master_devices, 
        device_taxonomy, 
        mocker
    ):
        """
        Test that the correct columns are passed to join_device_taxonomy.
        """
        input_device_taxonomy = pd.DataFrame(
            columns=[
                "dev_code",
                "description_in_title_case",
                "upd_migrated_categories",
                "upd_non_migrated_categories",
                "extra_column",
            ],
            data=[
                ("type1", "desc1", "migrated1", "non_migrated1", "extra1"),
                ("type2", "desc2", "migrated2", "non_migrated2", "extra2"),
                ("type3", "desc3", "migrated3", "non_migrated3", "extra3"),
            ],
        )
        expected_device_taxonomy = device_taxonomy

        mock_join_device_taxonomy = mocker.patch("devices_rap.joins.join_device_taxonomy")

        joins.join_mini_device_taxonomy(master_devices, input_device_taxonomy)

        actual = mock_join_device_taxonomy.call_args.kwargs["device_taxonomy"]
        pd.testing.assert_frame_equal(actual, expected_device_taxonomy)


class TestJoinMiniExceptions:
    """
    Tests for joins.join_mini_exceptions
    """

    @pytest.fixture
    def master_devices(self):
        """
        Return a master_devices DataFrame for testing.
        """
        return pd.DataFrame(
            columns=["upd_high_level_device_type", "der_provider_code"],
            data=[("type1", "code1"), ("type2", "code2"), ("type3", "code3")],
        )

    @pytest.fixture
    def exceptions(self):
        """
        Return an exceptions DataFrame for testing.
        """
        return pd.DataFrame(
            columns=["provider_code", "dev_code", "handover_date_zcm", "handover_date_vcm"],
            data=[
                ("code1", "type1", "2021-01-01", "2021-01-02"),
                ("code2", "type2", "2021-02-01", "2021-02-02"),
                ("code3", "type3", "2021-03-01", "2021-03-02"),
            ],
        )

    def test_returns_dataframe(self, master_devices, exceptions, mocker):
        """
        Test that the function returns a DataFrame.
        """
        mocker.patch(
            "devices_rap.joins.join_exceptions",
            return_value=pd.DataFrame(columns=["upd_high_level_device_type", "der_provider_code"]),
        )
        actual = joins.join_mini_exceptions(master_devices, exceptions)
        assert isinstance(actual, pd.DataFrame)

    def test_logging(self, master_devices, exceptions, mocker):
        """
        Test that the function logs the correct message.
        """
        mock_logger = mocker.spy(logger, "info")
        mocker.patch("devices_rap.joins.join_exceptions")

        joins.join_mini_exceptions(master_devices, exceptions)

        mock_logger.assert_called_once_with(
            "Reducing the exceptions table down to only join on the required columns: ['provider_code', 'dev_code', 'handover_date_zcm', 'handover_date_vcm']"
        )

    def test_calls_join_exceptions(self, master_devices, exceptions, mocker):
        """
        Test that the function calls join_exceptions.
        """
        mock_join_exceptions = mocker.patch("devices_rap.joins.join_exceptions")

        joins.join_mini_exceptions(master_devices, exceptions)

        mock_join_exceptions.assert_called_once()

    def test_raises_columns_not_found_error(self, master_devices, mocker):
        """
        Test that the function raises ColumnsNotFoundError when required columns are not present.
        """
        exceptions = pd.DataFrame(columns=["wrong_column", "another_wrong_column"])

        with pytest.raises(ColumnsNotFoundError):
            joins.join_mini_exceptions(master_devices, exceptions)

    def test_correct_columns_passed_to_join_exceptions(self, master_devices, mocker):
        """
        Test that the correct columns are passed to join_exceptions.
        """
        exceptions = pd.DataFrame(
            columns=[
                "provider_code",
                "dev_code",
                "handover_date_zcm",
                "handover_date_vcm",
                "extra_column",
            ],
            data=[
                ("code1", "type1", "2021-01-01", "2021-01-02", "extra1"),
                ("code2", "type2", "2021-02-01", "2021-02-02", "extra2"),
                ("code3", "type3", "2021-03-01", "2021-03-02", "extra3"),
            ],
        )
        expected_exceptions = pd.DataFrame(
            columns=["provider_code", "dev_code", "handover_date_zcm", "handover_date_vcm"],
            data=[
                ("code1", "type1", "2021-01-01", "2021-01-02"),
                ("code2", "type2", "2021-02-01", "2021-02-02"),
                ("code3", "type3", "2021-03-01", "2021-03-02"),
            ],
        )

        mock_join_exceptions = mocker.patch("devices_rap.joins.join_exceptions")

        joins.join_mini_exceptions(master_devices, exceptions)

        actual = mock_join_exceptions.call_args.kwargs["exceptions"]
        pd.testing.assert_frame_equal(actual, expected_exceptions)

    def test_include_exception_notes(self, master_devices, exceptions, mocker):
        """
        Test that the function includes exception notes when include_exception_notes is True.
        """
        extended_exceptions = exceptions.copy()
        extended_exceptions["exception_notes"] = ["note1", "note2", "note3"]
        mock_create_exception_notes = mocker.patch(
            "devices_rap.joins.create_exception_notes", return_value=extended_exceptions
        )
        mock_join_exceptions = mocker.patch("devices_rap.joins.join_exceptions")

        joins.join_mini_exceptions(master_devices, exceptions, include_exception_notes=True)

        mock_create_exception_notes.assert_called_once_with(exceptions)
        mock_join_exceptions.assert_called_once()


class TestJoinMiniTables:
    """
    Tests for joins.join_mini_tables
    """

    @pytest.fixture
    def summary_table(self):
        """
        Return a summary_table DataFrame for testing.
        """
        return pd.DataFrame(
            columns=["upd_high_level_device_type", "der_provider_code"],
            data=[("type1", "code1"), ("type2", "code2"), ("type3", "code3")],
        )

    @pytest.fixture
    def provider_codes_lookup(self):
        """
        Return a provider_codes_lookup DataFrame for testing.
        """
        return pd.DataFrame(
            columns=["org_code", "current_name_in_proper_case"],
            data=[("code1", "name1"), ("code2", "name2"), ("code3", "name3")],
        )

    @pytest.fixture
    def device_taxonomy(self):
        """
        Return a device_taxonomy DataFrame for testing.
        """
        return pd.DataFrame(
            columns=["dev_code", "description_in_title_case"],
            data=[("type1", "desc1"), ("type2", "desc2"), ("type3", "desc3")],
        )

    @pytest.fixture
    def exceptions(self):
        """
        Return an exceptions DataFrame for testing.
        """
        return pd.DataFrame(
            columns=["provider_code", "dev_code", "handover_date_zcm", "handover_date_vcm"],
            data=[
                ("code1", "type1", "2021-01-01", "2021-01-02"),
                ("code2", "type2", "2021-02-01", "2021-02-02"),
                ("code3", "type3", "2021-03-01", "2021-03-02"),
            ],
        )

    @pytest.fixture
    def mock_called_functions(self, mocker, empty_df):
        """
        Return the functions that are called by join_mini_tables.
        """
        called_functioned = [
            "devices_rap.joins.join_mini_provider_codes_lookup",
            "devices_rap.joins.join_mini_device_taxonomy",
            "devices_rap.joins.join_mini_exceptions",
        ]
        mocks = (mocker.patch(func, return_value=empty_df) for func in called_functioned)
        return mocks

    def test_returns_dataframe(
        self,
        summary_table,
        provider_codes_lookup,
        device_taxonomy,
        exceptions,
        mock_called_functions,
    ):
        """
        Test that the function returns a DataFrame.
        """
        _, _, _ = mock_called_functions

        actual = joins.join_mini_tables(
            summary_table, provider_codes_lookup, device_taxonomy, exceptions
        )
        assert isinstance(actual, pd.DataFrame)

    def test_logging(
        self,
        summary_table,
        provider_codes_lookup,
        device_taxonomy,
        exceptions,
        mock_called_functions,
        mock_info,
    ):
        """
        Test that the function logs the correct message.
        """
        _, _, _ = mock_called_functions

        joins.join_mini_tables(summary_table, provider_codes_lookup, device_taxonomy, exceptions)

        mock_info.assert_called_once_with(
            "Joining the mini tables onto the master_devices table to add contextual columns"
        )

    @pytest.mark.parametrize("kwarg", ["master_devices", "provider_codes_lookup"])
    def test_calls_join_mini_provider_codes_lookup(
        self,
        summary_table,
        provider_codes_lookup,
        device_taxonomy,
        exceptions,
        mock_called_functions,
        kwarg,
    ):
        """
        Test that the function calls join_mini_provider_codes_lookup.
        """
        mock_join_mini_provider_codes_lookup, _, _ = mock_called_functions

        joins.join_mini_tables(summary_table, provider_codes_lookup, device_taxonomy, exceptions)

        actual = mock_join_mini_provider_codes_lookup.call_args.kwargs[kwarg]
        expected = summary_table if kwarg == "master_devices" else provider_codes_lookup

        pd.testing.assert_frame_equal(actual, expected)

    @pytest.mark.parametrize("kwarg", ["master_devices", "device_taxonomy"])
    def test_calls_join_mini_device_taxonomy(
        self,
        summary_table,
        provider_codes_lookup,
        device_taxonomy,
        exceptions,
        mock_called_functions,
        kwarg,
        empty_df,
    ):
        """
        Test that the function calls join_mini_device_taxonomy.
        """

        _, mock_join_mini_device_taxonomy, _ = mock_called_functions

        joins.join_mini_tables(summary_table, provider_codes_lookup, device_taxonomy, exceptions)

        actual = mock_join_mini_device_taxonomy.call_args.kwargs[kwarg]
        expected = empty_df if kwarg == "master_devices" else device_taxonomy

        pd.testing.assert_frame_equal(actual, expected)

    @pytest.mark.parametrize("kwarg", ["master_devices", "exceptions", "include_exception_notes"])
    @pytest.mark.parametrize("value", [True, False])
    def test_calls_join_mini_exceptions(
        self,
        summary_table,
        provider_codes_lookup,
        device_taxonomy,
        exceptions,
        mock_called_functions,
        kwarg,
        value,
        empty_df,
    ):
        """
        Test that the function calls join_mini_exceptions.
        """
        _, _, mock_join_mini_exceptions = mock_called_functions

        joins.join_mini_tables(
            summary_table,
            provider_codes_lookup,
            device_taxonomy,
            exceptions,
            include_exception_notes=value,
        )

        if kwarg == "include_exception_notes":
            assert mock_join_mini_exceptions.call_args.kwargs[kwarg] == value
        else:
            actual = mock_join_mini_exceptions.call_args.kwargs[kwarg]
            expected = empty_df if kwarg == "master_devices" else exceptions
            pd.testing.assert_frame_equal(actual, expected)


if __name__ == "__main__":
    pytest.main([__file__])
