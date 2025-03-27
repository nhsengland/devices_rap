"""
Tests for devices_rap/pipeline.py
"""

from unittest import mock
import pandas as pd
import pytest
import test

from devices_rap import pipeline


pytestmark = pytest.mark.no_data_needed


class TestAmberReportPipeline:
    """
    Test class for pipeline.amber_report_pipeline
    """

    # We want to define the pipeline functions and their return values in a list of tuples
    pipeline_functions = {
        "check_paths": None,
        "load_devices_datasets": "datasets",
        "batch_normalise_column_names": {
            "master_devices": {
                "data": pd.DataFrame(columns=["batch_normalise_column_names.master_devices"])
            },
            "provider_codes_lookup": {
                "data": pd.DataFrame(
                    columns=["batch_normalise_column_names.provider_codes_lookup"]
                )
            },
            "device_taxonomy": {
                "data": pd.DataFrame(columns=["batch_normalise_column_names.device_taxonomy"])
            },
            "exceptions": {
                "data": pd.DataFrame(columns=["batch_normalise_column_names.exceptions"])
            },
        },
        "cleanse_master_data": pd.DataFrame(columns=["cleanse_master_data"]),
        "cleanse_exceptions": pd.DataFrame(columns=["cleanse_exceptions"]),
        "join_provider_codes_lookup": pd.DataFrame(columns=["join_provider_codes_lookup"]),
        "join_device_taxonomy": pd.DataFrame(columns=["join_device_taxonomy"]),
        "join_exceptions": pd.DataFrame(columns=["join_exceptions"]),
        "cleanse_master_joined_dataset": pd.DataFrame(
            columns=["cleanse_master_joined_dataset", "upd_region"]
        ),
        "create_device_category_summary_table": pd.DataFrame(
            columns=["create_device_category_summary_table"]
        ),
        "create_device_summary_table": pd.DataFrame(columns=["create_device_summary_table"]),
        "join_mini_tables": pd.DataFrame(columns=["join_mini_tables"]),
        "create_regional_table_cuts": {
            "test": pd.DataFrame(columns=["create_regional_table_cuts"])
        },
        "interpret_output_instructions": {
            "region_1": {"test": pd.DataFrame(columns=["interpret_output_instructions"])}
        },
        "create_excel_reports": None,
    }

    @pytest.fixture
    def mock_pipeline_functions(self, mocker):
        """
        Mock the pipeline functions
        """
        mock_functions = {}
        for function, return_value in self.pipeline_functions.items():
            mock_functions[function] = mocker.patch(
                f"devices_rap.pipeline.{function}", return_value=return_value
            )

        return mock_functions

    @pytest.mark.parametrize("function", pipeline_functions.keys())
    def test_calls_functions(self, mock_pipeline_functions, function):
        """
        Test that amber_report_pipeline calls the correct functions the correct number of times
        """
        pipeline.amber_report_pipeline()

        expected_call_count = 2 if function == "join_mini_tables" else 1

        assert mock_pipeline_functions[function].call_count == expected_call_count

    def test_calls_check_paths_with_no_args(self, mock_pipeline_functions):
        """
        Test that amber_report_pipeline calls check_paths with no arguments
        """
        pipeline.amber_report_pipeline()

        mock_pipeline_functions["check_paths"].assert_called_once_with()

    def test_calls_load_devices_datasets_with_correct_args(self, mocker, mock_pipeline_functions):
        """
        Test that amber_report_pipeline calls load_devices_datasets with the correct arguments
        """
        mocker.patch("devices_rap.pipeline.DATASETS", "datasets")
        pipeline.amber_report_pipeline()
        mock_pipeline_functions["load_devices_datasets"].assert_called_once_with("datasets")

    def test_calls_batch_normalise_column_names_with_correct_args(self, mock_pipeline_functions):
        """
        Test that amber_report_pipeline calls batch_normalise_column_names with the correct arguments
        """
        pipeline.amber_report_pipeline()
        mock_pipeline_functions["batch_normalise_column_names"].assert_called_once_with("datasets")

    def test_calls_cleanse_master_data_with_correct_args(self, mock_pipeline_functions):
        """
        Test that amber_report_pipeline calls cleanse_master_data with the correct arguments
        """
        pipeline.amber_report_pipeline()

        actual = mock_pipeline_functions["cleanse_master_data"].call_args.args[0]
        expected = self.pipeline_functions["batch_normalise_column_names"]["master_devices"][
            "data"
        ]

        pd.testing.assert_frame_equal(actual, expected)

    def test_calls_cleanse_exceptions_with_correct_args(self, mock_pipeline_functions):
        """
        Test that amber_report_pipeline calls cleanse_exceptions with the correct arguments
        """
        pipeline.amber_report_pipeline()

        actual = mock_pipeline_functions["cleanse_exceptions"].call_args.args[0]
        expected = self.pipeline_functions["batch_normalise_column_names"]["exceptions"]["data"]

        pd.testing.assert_frame_equal(actual, expected)

    @pytest.mark.parametrize("arg", [0, 1])
    def test_calls_join_provider_codes_lookup_with_correct_args(
        self, mock_pipeline_functions, arg
    ):
        """
        Test that amber_report_pipeline calls join_provider_codes_lookup with the correct arguments
        """
        pipeline.amber_report_pipeline()

        actual = mock_pipeline_functions["join_provider_codes_lookup"].call_args.args[arg]
        expected = (
            self.pipeline_functions["cleanse_master_data"]
            if arg == 0
            else self.pipeline_functions["batch_normalise_column_names"]["provider_codes_lookup"][
                "data"
            ]
        )

        pd.testing.assert_frame_equal(actual, expected)

    @pytest.mark.parametrize("arg", [0, 1])
    def test_calls_join_device_taxonomy_with_correct_args(self, mock_pipeline_functions, arg):
        """
        Test that amber_report_pipeline calls join_device_taxonomy with the correct arguments
        """
        pipeline.amber_report_pipeline()

        actual = mock_pipeline_functions["join_device_taxonomy"].call_args.args[arg]
        expected = (
            self.pipeline_functions["join_provider_codes_lookup"]
            if arg == 0
            else self.pipeline_functions["batch_normalise_column_names"]["device_taxonomy"]["data"]
        )

        pd.testing.assert_frame_equal(actual, expected)

    @pytest.mark.parametrize("arg", [0, 1])
    def test_calls_join_exceptions_with_correct_args(self, mock_pipeline_functions, arg):
        """
        Test that amber_report_pipeline calls join_exceptions with the correct arguments
        """
        pipeline.amber_report_pipeline()

        actual = mock_pipeline_functions["join_exceptions"].call_args.args[arg]
        expected = (
            self.pipeline_functions["join_device_taxonomy"]
            if arg == 0
            else self.pipeline_functions["cleanse_exceptions"]
        )

        pd.testing.assert_frame_equal(actual, expected)

    def test_calls_cleanse_master_joined_dataset_with_correct_args(self, mock_pipeline_functions):
        """
        Test that amber_report_pipeline calls cleanse_master_joined_dataset with the correct arguments
        """
        pipeline.amber_report_pipeline()

        actual = mock_pipeline_functions["cleanse_master_joined_dataset"].call_args.args[0]
        expected = self.pipeline_functions["join_exceptions"]

        pd.testing.assert_frame_equal(actual, expected)

    def test_calls_create_device_category_summary_table_with_correct_args(
        self, mock_pipeline_functions
    ):
        """
        Test that amber_report_pipeline calls create_device_category_summary_table with the correct arguments
        """
        pipeline.amber_report_pipeline()

        actual = mock_pipeline_functions["create_device_category_summary_table"].call_args.kwargs[
            "master_devices_data"
        ]
        expected = self.pipeline_functions["cleanse_master_joined_dataset"]

        pd.testing.assert_frame_equal(actual, expected)

    def test_calls_create_device_summary_table_with_correct_args(self, mock_pipeline_functions):
        """
        Test that amber_report_pipeline calls create_device_summary_table with the correct arguments
        """
        pipeline.amber_report_pipeline()

        actual = mock_pipeline_functions["create_device_summary_table"].call_args.kwargs[
            "master_devices_data"
        ]
        expected = self.pipeline_functions["cleanse_master_joined_dataset"]

        pd.testing.assert_frame_equal(actual, expected)


    @pytest.mark.parametrize(
        "call_num, previous_function",
        [(1, "create_device_summary_table")],
    )
    def test_calls_join_mini_tables_with_correct_args(
        self, mock_pipeline_functions, call_num, previous_function
    ):
        """
        Test that amber_report_pipeline calls join_mini_tables with the correct arguments
        """
        pipeline.amber_report_pipeline()

        actual = mock_pipeline_functions["join_mini_tables"].call_args_list[call_num].args[0]
        expected = self.pipeline_functions[previous_function]

        pd.testing.assert_frame_equal(actual, expected)

    @pytest.mark.parametrize("call_num, include_exception_notes", [(0, True), (1, False)])
    @pytest.mark.parametrize(
        "kwarg, expected_value",
        [
            (
                "provider_codes_lookup",
                pipeline_functions["batch_normalise_column_names"]["provider_codes_lookup"][
                    "data"
                ],
            ),
            (
                "device_taxonomy",
                pipeline_functions["batch_normalise_column_names"]["device_taxonomy"]["data"],
            ),
            ("exceptions", pipeline_functions["cleanse_exceptions"]),
            ("include_exception_notes", None),
        ],
    )
    def test_calls_join_mini_tables_with_correct_kwargs(
        self, mock_pipeline_functions, kwarg, expected_value, call_num, include_exception_notes
    ):
        """
        Test that amber_report_pipeline calls join_mini_tables with the correct keyword arguments
        """
        pipeline.amber_report_pipeline()

        actual = mock_pipeline_functions["join_mini_tables"].call_args_list[call_num].kwargs[kwarg]

        expected = (
            include_exception_notes if kwarg == "include_exception_notes" else expected_value
        )

        if isinstance(expected, pd.DataFrame):
            pd.testing.assert_frame_equal(actual, expected)
        else:
            assert actual == expected

    @pytest.mark.parametrize(
        "table, expected",
        [
            ("summary", pipeline_functions["join_mini_tables"]),
            ("detailed", pipeline_functions["join_mini_tables"]),
            ("data", pipeline_functions["cleanse_master_joined_dataset"]),
        ],
    )
    def test_calls_create_regional_table_cuts_with_correct_tables(
        self, mock_pipeline_functions, table, expected
    ):
        """
        Test that amber_report_pipeline calls create_regional_table_cuts with the correct tables
        """
        pipeline.amber_report_pipeline()

        tables = mock_pipeline_functions["create_regional_table_cuts"].call_args.kwargs["tables"]
        actual = tables[table]

        pd.testing.assert_frame_equal(actual, expected)

    @pytest.mark.parametrize(
        "kwarg, expected_value",
        [
            ("instructions", "AMBER_OUTPUT_INSTRUCTIONS"),
            ("region_cuts", pipeline_functions["create_regional_table_cuts"]),
        ],
    )
    def test_calls_interpret_output_instructions_with_correct_kwarg(
        self, mocker, mock_pipeline_functions, kwarg, expected_value
    ):
        """
        Test that amber_report_pipeline calls interpret_output_instructions with the correct keyword arguments
        """
        mocker.patch("devices_rap.pipeline.AMBER_OUTPUT_INSTRUCTIONS", expected_value)

        pipeline.amber_report_pipeline()

        actual = mock_pipeline_functions["interpret_output_instructions"].call_args.kwargs[kwarg]
        expected = expected_value

        if kwarg == "region_cuts":
            assert "test" in actual
            pd.testing.assert_frame_equal(actual["test"], expected["test"])
        else:
            assert actual == expected

    def test_calls_create_excel_reports_with_correct_args(self, mock_pipeline_functions):
        """
        Test that amber_report_pipeline calls create_excel_reports with the correct arguments
        """
        pipeline.amber_report_pipeline()

        actual = mock_pipeline_functions["create_excel_reports"].call_args.kwargs[
            "output_workbooks"
        ]

        assert "region_1" in actual
        assert "test" in actual["region_1"]

        actual_df = actual["region_1"]["test"]
        expected_df = self.pipeline_functions["interpret_output_instructions"]["region_1"]["test"]

        pd.testing.assert_frame_equal(actual_df, expected_df)

    def test_calls_logger_success_with_correct_message(self, mock_log_levels, mock_pipeline_functions):
        """
        Test that amber_report_pipeline calls logger.success with the correct message
        """
        pipeline.amber_report_pipeline()

        mock_log_levels["success"].assert_called_once_with("Pipeline complete.")



if __name__ == "__main__":
    # This code allows the tests in the file to be run by running the file itself.
    pytest.main([__file__])
