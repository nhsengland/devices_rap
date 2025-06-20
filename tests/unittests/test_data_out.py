"""
Tests for devices_rap/data_out.py
"""

from unittest import mock
import pytest
import pandas as pd

from devices_rap import data_out
from devices_rap.data_out import create_excel_reports, process_region

# from devices_rap import data_out


pytestmark = pytest.mark.no_data_needed


class TestOutputData:
    """
    Test class for data_out.output_data
    """

    # Mock pipeline_config fixture

    @pytest.fixture
    def mock_pipeline_config(self, mocker, tmp_path):
        """
        Mock the pipeline_config to return a mock output directory.
        """
        mock_pipeline_config = mocker.MagicMock()
        mock_pipeline_config.create_output_directory.return_value = tmp_path
        mock_pipeline_config.use_multiprocessing = False
        mock_pipeline_config.fin_month = "test_month"
        mock_pipeline_config.fin_year = "test_year"

        return mock_pipeline_config

    @pytest.fixture
    def mock_create_excel_reports(self, mocker):
        """
        Mock the create_excel_reports function.
        """
        return mocker.patch("devices_rap.data_out.create_excel_reports", return_value=None)

    @pytest.fixture
    def mock_create_pickle(self, mocker):
        """
        Mock the create_pickle function.
        """
        return mocker.patch("devices_rap.data_out.create_pickle", return_value=None)

    # Test logs warning when pipeline_config.outputs is empty
    def test_output_data_logs_warning_when_outputs_empty(self, mock_pipeline_config, mock_warning):
        """
        Test that output_data logs a warning when pipeline_config.outputs is empty
        """
        mock_pipeline_config.outputs = []
        data_out.output_data(
            output_workbooks={},
            pipeline_config=mock_pipeline_config,
        )
        mock_warning.assert_called_once_with("No outputs configured. Skipping output data.")

    # Test does not log warning when pipeline_config.outputs is not empty
    def test_output_data_does_not_log_warning_when_outputs_not_empty(
        self, mock_pipeline_config, mock_warning
    ):
        """
        Test that output_data does not log a warning when pipeline_config.outputs is not empty
        """
        mock_pipeline_config.outputs = ["excel"]
        data_out.output_data(
            output_workbooks={},
            pipeline_config=mock_pipeline_config,
        )
        mock_warning.assert_not_called()

    # Test calls implemented output functions based on pipeline_config.outputs
    @pytest.mark.parametrize(
        "outputs, expected_calls",
        [
            (["excel"], ["create_excel_reports"]),
            (["pickle"], ["create_pickle"]),
            (["excel", "pickle"], ["create_excel_reports", "create_pickle"]),
        ],
    )
    def test_output_data_calls_implemented_outputs(
        self,
        mock_pipeline_config,
        mock_create_excel_reports,
        mock_create_pickle,
        outputs,
        expected_calls,
    ):
        """
        Test that output_data calls the implemented output functions based on pipeline_config.outputs
        """
        mock_pipeline_config.outputs = outputs

        data_out.output_data(
            output_workbooks={},
            pipeline_config=mock_pipeline_config,
        )

        for call in expected_calls:
            if call == "create_excel_reports":
                mock_create_excel_reports.assert_called_once()
            elif call == "create_pickle":
                mock_create_pickle.assert_called_once()

    # Test logs warning for unimplemented outputs
    @pytest.mark.parametrize("output", ["csv", "sql", "excel_zip"])
    def test_output_data_logs_warning_for_unimplemented_outputs(
        self, mock_pipeline_config, mock_warning, output
    ):
        """
        Test that output_data logs a warning for unimplemented outputs
        """
        mock_pipeline_config.outputs = [output]

        data_out.output_data(
            output_workbooks={},
            pipeline_config=mock_pipeline_config,
        )

        mock_warning.assert_called_once_with(
            f"{output} output is not implemented yet. Skipping {output} output."
        )


class TestCreateExcelReports:
    """
    Test class for data_out.create_excel_reports
    """

    @pytest.fixture
    def mock_process_region(self, mocker):
        return mocker.patch("devices_rap.data_out.process_region", return_value=None)

    @pytest.fixture
    def mock_output_directory(self, tmp_path):
        return tmp_path / "test_output"

    @pytest.fixture
    def mock_pipeline_config(self, mocker, mock_output_directory):
        """
        Mock the pipeline_config to return a mock output directory.
        """
        mock_pipeline_config = mocker.MagicMock()
        mock_pipeline_config.create_output_directory.return_value = mock_output_directory
        mock_pipeline_config.use_multiprocessing = False
        return mock_pipeline_config

    @pytest.mark.parametrize("use_multiprocessing", [True, False])
    @pytest.mark.parametrize(
        "output_workbooks, call_count", [({}, 0), ({"region1": {"sheet1": pd.DataFrame()}}, 1)]
    )
    def test_create_excel_reports_calls_process_region(
        self,
        mock_pipeline_config,
        mock_output_directory,
        mock_process_region,
        use_multiprocessing,
        output_workbooks,
        call_count,
    ):
        """
        Test that create_excel_reports calls process_region
        """
        create_excel_reports(
            output_workbooks=output_workbooks,
            output_directory=mock_output_directory,
            use_multiprocessing=use_multiprocessing,
        )
        assert mock_process_region.call_count == call_count

    @pytest.mark.parametrize("use_multiprocessing", [True, False])
    @pytest.mark.parametrize(
        "kwarg, expected_value",
        [
            ("output_directory", None),
            ("region", "region1"),
            ("worksheets", {"sheet1": pd.DataFrame()}),
            ("use_multiprocessing", None),
        ],
    )
    def test_create_excel_reports_calls_process_region_with_correct_args(
        self,
        mock_pipeline_config,
        mock_output_directory,
        mock_process_region,
        use_multiprocessing,
        kwarg,
        expected_value,
    ):
        """
        Test that create_excel_reports calls process_region with the correct arguments
        """
        mock_pipeline_config.use_multiprocessing = use_multiprocessing

        output_workbooks = {"region1": {"sheet1": pd.DataFrame()}}

        create_excel_reports(
            output_workbooks=output_workbooks,
            output_directory=mock_output_directory,
            use_multiprocessing=use_multiprocessing,
        )

        actual = mock_process_region.call_args[1][kwarg]

        if kwarg == "output_directory":
            assert actual == mock_output_directory
        elif kwarg == "worksheets":
            assert actual.keys() == expected_value.keys()
            pd.testing.assert_frame_equal(actual["sheet1"], expected_value["sheet1"])
        elif kwarg == "use_multiprocessing":
            assert actual == use_multiprocessing
        else:
            assert actual == expected_value

    @pytest.mark.parametrize(
        "log_type, expected_message",
        [("info", "Creating excel reports"), ("success", "Excel reports created successfully.")],
    )
    def test_log_called(
        self,
        mock_log_levels,
        mock_pipeline_config,
        mock_process_region,
        mock_output_directory,
        log_type,
        expected_message,
    ):
        """
        Test that the loguru.logger is called
        """
        create_excel_reports(
            output_workbooks={},
            output_directory=mock_output_directory,
            use_multiprocessing=False,
        )

        mock_log = mock_log_levels[log_type]

        mock_log.assert_called_once_with(expected_message)


class TestProcessRegion:
    """
    Test class for data_out.process_region
    """

    @pytest.fixture
    def output_directory(self, tmp_path):
        output_directory = tmp_path / "test_output" / "2021" / "01"
        output_directory.mkdir(parents=True, exist_ok=True)
        return output_directory

    @pytest.fixture
    def mock_create_excel_file(self, mocker):
        return mocker.patch("devices_rap.data_out.create_excel_file")

    def test_calls_create_excel_file_once(self, output_directory, mock_create_excel_file):
        """
        Test that process_region calls create_excel_file once
        """
        region = "region1"
        worksheets = {"sheet1": pd.DataFrame()}
        use_multiprocessing = False

        process_region(
            output_directory=output_directory,
            region=region,
            worksheets=worksheets,
            use_multiprocessing=use_multiprocessing,
        )
        assert mock_create_excel_file.call_count == 1

    @pytest.mark.parametrize(
        "kwarg, expected_value",
        [
            ("output_file", "REGION1_RAG_STATUS_REPORT.xlsx"),
            ("worksheets", {"sheet1": pd.DataFrame()}),
            ("use_multiprocessing", False),
        ],
    )
    def test_calls_create_excel_file_with_correct_args(
        self, output_directory, mock_create_excel_file, kwarg, expected_value
    ):
        """
        Test that process_region calls create_excel_file with the correct arguments
        """
        region = "region1"
        worksheets = {"sheet1": pd.DataFrame()}
        use_multiprocessing = False

        process_region(
            output_directory=output_directory,
            region=region,
            worksheets=worksheets,
            use_multiprocessing=use_multiprocessing,
        )

        actual = mock_create_excel_file.call_args[1][kwarg]

        if kwarg == "output_file":
            assert actual == output_directory / "REGION1_RAG_STATUS_REPORT.xlsx"
        elif kwarg == "worksheets":
            assert isinstance(actual, dict)
            assert actual.keys() == expected_value.keys()
            pd.testing.assert_frame_equal(actual["sheet1"], expected_value["sheet1"])
        elif kwarg == "use_multiprocessing":
            assert actual == expected_value
        else:
            assert actual == expected_value

    def test_logs_success_message(self, output_directory, mock_create_excel_file, mock_log_levels):
        """
        Test that process_region logs a success message
        """
        region = "region1"
        worksheets = {"sheet1": pd.DataFrame()}
        use_multiprocessing = False

        process_region(
            output_directory=output_directory,
            region=region,
            worksheets=worksheets,
            use_multiprocessing=use_multiprocessing,
        )

        mock_success = mock_log_levels["success"]
        mock_success.assert_called_once_with("Excel report for region1 created successfully.")

    def test_logs_info_when_file_does_not_exist(
        self, output_directory, mock_create_excel_file, mock_log_levels
    ):
        """
        Test that process_region logs an info message when the file does not exist
        """
        region = "region1"
        worksheets = {"sheet1": pd.DataFrame()}
        use_multiprocessing = False

        process_region(
            output_directory=output_directory,
            region=region,
            worksheets=worksheets,
            use_multiprocessing=use_multiprocessing,
        )

        mock_info = mock_log_levels["info"]
        mock_info.assert_called_once_with("Creating Excel report for region1")

    def test_logs_warning_when_file_exists(
        self, output_directory, mock_create_excel_file, mock_log_levels
    ):
        """
        Test that process_region logs an info message when the file does not exist
        """
        region = "region1"
        worksheets = {"sheet1": pd.DataFrame()}
        use_multiprocessing = False

        output_file = output_directory / "REGION1_RAG_STATUS_REPORT.xlsx"
        output_file.touch()

        process_region(
            output_directory=output_directory,
            region=region,
            worksheets=worksheets,
            use_multiprocessing=use_multiprocessing,
        )

        mock_warning = mock_log_levels["warning"]
        mock_warning.assert_called_once_with(f"Overwriting the existing Excel file: {output_file}")

    def test_deletes_file_when_file_exists(
        self, output_directory, mock_create_excel_file, mock_log_levels
    ):
        """
        Test that process_region logs an info message when the file does not exist
        """
        region = "region1"
        worksheets = {"sheet1": pd.DataFrame()}
        use_multiprocessing = False

        output_file = output_directory / "REGION1_RAG_STATUS_REPORT.xlsx"
        output_file.touch()

        process_region(
            output_directory=output_directory,
            region=region,
            worksheets=worksheets,
            use_multiprocessing=use_multiprocessing,
        )

        assert not output_file.exists()


class TestCreateExcelFile:
    """
    Test class for data_out.create_excel_file
    """

    @pytest.fixture
    def output_file(self, tmp_path):
        return tmp_path / "test_output.xlsx"

    @pytest.fixture
    def mock_create_formats(self, mocker):
        return mocker.patch("devices_rap.data_out.create_formats", return_value="formats")

    @pytest.fixture
    def mock_write_worksheet(self, mocker):
        return mocker.patch("devices_rap.data_out.write_worksheet", return_value=None)

    @pytest.mark.parametrize("use_multiprocessing", [True, False])
    def test_calls_write_worksheet(
        self,
        mocker,
        output_file,
        mock_create_formats,
        mock_write_worksheet,
        use_multiprocessing,
    ):
        """
        Test that create_excel_file calls write_worksheet
        """
        worksheets = {"sheet1": pd.DataFrame()}
        data_out.create_excel_file(output_file, worksheets, use_multiprocessing)
        assert mock_write_worksheet.call_count == 1

    @pytest.mark.parametrize("use_multiprocessing", [True, False])
    @pytest.mark.parametrize(
        "kwarg, expected_value",
        [
            ("writer", None),
            ("sheet_name", "sheet1"),
            ("data", pd.DataFrame()),
            ("formats", "formats"),
            ("output_file", None),
        ],
    )
    def test_calls_write_worksheet_with_correct_args(
        self,
        mocker,
        output_file,
        mock_create_formats,
        mock_write_worksheet,
        use_multiprocessing,
        kwarg,
        expected_value,
    ):
        """
        Test that create_excel_file calls write_worksheet with the correct arguments
        """
        worksheets = {"sheet1": pd.DataFrame()}
        data_out.create_excel_file(output_file, worksheets, use_multiprocessing)
        actual = mock_write_worksheet.call_args[1][kwarg]

        if kwarg == "writer":
            assert isinstance(actual, pd.ExcelWriter)
        elif kwarg == "data":
            pd.testing.assert_frame_equal(actual, expected_value)
        elif kwarg == "output_file":
            assert actual == output_file
        else:
            assert actual == expected_value

    def test_calls_create_formats_once(
        self, output_file, mock_create_formats, mock_write_worksheet
    ):
        """
        Test that create_excel_file calls create_formats once
        """
        worksheets = {"sheet1": pd.DataFrame()}
        data_out.create_excel_file(output_file, worksheets, False)
        assert mock_create_formats.call_count == 1

    def test_logs_debug(
        self, output_file, mock_create_formats, mock_write_worksheet, mock_log_levels
    ):
        """
        Test that create_excel_file logs a debug message
        """
        worksheets = {"sheet1": pd.DataFrame()}
        data_out.create_excel_file(output_file, worksheets, False)
        mock_debug = mock_log_levels["debug"]
        mock_debug.assert_called_once_with(f"Creating the Excel file: {output_file}")


class TestCreateFormats:
    """
    Test class for data_out.create_formats
    """

    @pytest.fixture
    def mock_workbook(self, mocker):
        mock = mocker.MagicMock()
        # add_format returns a new MagicMock for each call
        mock.add_format.side_effect = lambda config=None: mocker.MagicMock()
        return mock

    def test_returns_dict_with_expected_keys(self, mock_workbook):
        """
        Test that create_formats returns a dict with the correct keys
        """
        formats = data_out.create_formats(mock_workbook)
        assert set(formats.keys()) == {"default", "cost", "header", "total"}

    def test_add_format_called_with_correct_configs(self, mocker, mock_workbook):
        """
        Test that add_format is called with the correct configs for each format
        """
        expected_calls = [
            ({"num_format": "£#,##0"},),
            (
                {
                    "bold": True,
                    "text_wrap": True,
                    "valign": "top",
                    "fg_color": "#D9E1F2",
                    "border": 1,
                },
            ),
            (
                {
                    "bold": True,
                    "fg_color": "#C6EFCE",
                    "num_format": "£#,##0",
                },
            ),
        ]
        # Call function
        data_out.create_formats(mock_workbook)
        # The first call is for "default" (empty dict), which should call add_format() with no args
        assert mock_workbook.add_format.call_args_list[0][0] == ()
        # The next calls are for "cost", "header", "total" in order
        for idx, expected in enumerate(expected_calls, start=1):
            assert mock_workbook.add_format.call_args_list[idx][0] == expected

    def test_returns_values_from_add_format(self, mocker, mock_workbook):
        """
        Test that the returned dict values are the objects returned by add_format
        """
        # Prepare unique mocks for each call
        format_mocks = [mocker.MagicMock(name=f"format_{k}") for k in range(4)]
        mock_workbook.add_format.side_effect = format_mocks
        formats = data_out.create_formats(mock_workbook)
        # Should return the mocks in the order: default, cost, header, total
        assert list(formats.values()) == format_mocks

    def test_default_format_calls_add_format_with_no_args(self, mocker, mock_workbook):
        """
        Test that add_format is called with no arguments for the 'default' format
        """
        data_out.create_formats(mock_workbook)
        # The first call is for 'default'
        assert mock_workbook.add_format.call_args_list[0][0] == ()


class TestWriteWorksheet:
    """
    Test class for data_out.write_worksheet
    """

    @pytest.fixture
    def mock_to_excel(self, mocker):
        return mocker.patch("pandas.DataFrame.to_excel", return_value=None)

    @pytest.fixture
    def mock_apply_excel_formatting(self, mocker):
        return mocker.patch("devices_rap.data_out.apply_excel_formatting", return_value=None)

    @pytest.fixture
    def mock_writer(self, mocker):
        return mocker.MagicMock()

    @pytest.fixture
    def default_args(self, mock_writer, tmp_path):
        """
        Fixture to return the default arguments for write_worksheet function
        """
        return {
            "writer": mock_writer,
            "sheet_name": "sheet1",
            "data": pd.DataFrame(columns=["col1", "col2"], data=[["val1", "val2"]]),
            "formats": {"header": "header_format", "cost": "cost_format"},
            "output_file": tmp_path / "output_file",
        }

    def test_calls_to_excel(self, default_args, mock_to_excel, mock_apply_excel_formatting):
        """
        Test that write_worksheet calls to_excel
        """

        data_out.write_worksheet(
            **default_args,
        )

        assert mock_to_excel.call_count == 1

    @pytest.mark.parametrize(
        "kwarg, expected_value",
        [
            ("excel_writer", None),
            ("sheet_name", "sheet1"),
            ("index", False),
            ("startrow", 1),
            ("header", False),
        ],
    )
    def test_calls_to_excel_with_correct_args(
        self,
        mocker,
        default_args,
        mock_to_excel,
        mock_apply_excel_formatting,
        kwarg,
        expected_value,
    ):
        """
        Test that write_worksheet calls to_excel with the correct arguments
        """
        data_out.write_worksheet(
            **default_args,
        )
        actual = mock_to_excel.call_args[1][kwarg]

        if kwarg == "excel_writer":
            assert isinstance(actual, mocker.MagicMock)
        else:
            assert actual == expected_value

    def test_calls_apply_excel_formatting(
        self, mocker, mock_to_excel, mock_apply_excel_formatting, default_args
    ):
        """
        Test that write_worksheet calls the write method
        """

        data_out.write_worksheet(
            **default_args,
        )

        assert mock_apply_excel_formatting.call_count == 1

    @pytest.mark.parametrize(
        "kwarg, expected_value",
        [
            ("writer", None),
            ("data", pd.DataFrame(columns=["col1", "col2"], data=[["val1", "val2"]])),
            ("formats", {"header": "header_format", "cost": "cost_format"}),
            ("sheet_name", "sheet1"),
        ],
    )
    def test_calls_apply_excel_formatting_with_correct_args(
        self,
        mocker,
        default_args,
        mock_to_excel,
        mock_apply_excel_formatting,
        kwarg,
        expected_value,
    ):
        """
        Test that write_worksheet calls the write method with the correct arguments
        """
        data_out.write_worksheet(
            **default_args,
        )
        actual = mock_apply_excel_formatting.call_args[1][kwarg]

        if kwarg == "writer":
            assert isinstance(actual, mocker.MagicMock)
        elif kwarg == "data":
            pd.testing.assert_frame_equal(actual, expected_value)
        else:
            assert actual == expected_value


class TestApplyExcelFormatting:
    """
    Test class for data_out.apply_excel_formatting
    """

    @pytest.fixture
    def mock_worksheet(self, mocker):
        """
        Create a mock worksheet with the required methods.
        """
        ws = mocker.MagicMock()
        return ws

    @pytest.fixture
    def mock_writer(self, mocker, mock_worksheet):
        """
        Create a mock writer with a mock worksheet.
        """
        writer = mocker.MagicMock()
        writer.sheets = {"Sheet1": mock_worksheet}
        return writer

    @pytest.fixture
    def test_formats(self, mocker):
        """
        Create mock formats for testing.
        """
        return {
            "header": mocker.MagicMock(name="header_format"),
            "total": mocker.MagicMock(name="total_format"),
            "cost": mocker.MagicMock(name="cost_format"),
        }

    @pytest.fixture
    def test_data(self):
        """Create a DataFrame with some test data."""
        data = pd.DataFrame(
            {
                "Provider Code": ["abc", "Total123", "def"],
                "Region": ["xyz", "uvw", "Total456"],
                "A": [1.0, 2.0, 3.0],
                "B": [3, 4, 5],
                "C": [5.0, 6.0, 7.0],
            }
        )
        data = data.astype({"A": "float64", "B": "int64", "C": "float32"})
        return data

    def test_writes_headers_with_format(self, mock_writer, test_formats, test_data):
        """
        Ensure "Provider Code" and "Region" are always present
        """
        data_out.apply_excel_formatting(mock_writer, test_data, test_formats, "Sheet1")
        ws = mock_writer.sheets["Sheet1"]
        assert ws.write.call_count == len(test_data.columns)
        for col_num, value in enumerate(test_data.columns.values):
            ws.write.assert_any_call(0, col_num, value, test_formats["header"])

    def test_sets_autofilter(self, mock_writer, test_formats, test_data):
        """
        Ensure that autofilter is set for the header row
        """
        data_out.apply_excel_formatting(mock_writer, test_data, test_formats, "Sheet1")
        ws = mock_writer.sheets["Sheet1"]
        ws.autofilter.assert_called_once_with(0, 0, test_data.shape[0], test_data.shape[1] - 1)

    @pytest.mark.parametrize(
        "row_idx, col_name, value, should_format",
        [
            (2, "Provider Code", "Total123", True),  # Row 2, Provider Code is "Total123"
            (3, "Region", "Total456", True),  # Row 3, Region is "Total456"
            (1, "Provider Code", "abc", False),  # Row 1, Provider Code is not total
            (1, "Region", "xyz", False),  # Row 1, Region is not total
        ],
    )
    def test_sets_total_row_formatting(
        self, mocker, mock_writer, test_formats, test_data, row_idx, col_name, value, should_format
    ):
        """
        Ensure that the total row formatting is applied correctly
        """
        data_out.apply_excel_formatting(mock_writer, test_data, test_formats, "Sheet1")
        ws = mock_writer.sheets["Sheet1"]
        calls = [call[0][0] for call in ws.set_row.call_args_list]
        if should_format:
            assert row_idx in calls
            ws.set_row.assert_any_call(row_idx, None, test_formats["total"])
        else:
            assert row_idx not in calls

    @pytest.mark.parametrize(
        "col_idx, col_name, should_format",
        [
            (0, "Provider Code", False),
            (1, "Region", False),
            (2, "A", True),
            (3, "B", False),
            (4, "C", True),
        ],
    )
    def test_sets_cost_column_formatting(
        self, mock_writer, test_formats, test_data, col_idx, col_name, should_format
    ):
        """
        Ensure that the cost column formatting is applied correctly
        """
        data_out.apply_excel_formatting(mock_writer, test_data, test_formats, "Sheet1")
        ws = mock_writer.sheets["Sheet1"]
        if should_format:
            ws.set_column.assert_any_call(col_idx, col_idx, None, test_formats["cost"])
        else:
            col_args = [call[0][0] for call in ws.set_column.call_args_list]
            assert col_idx not in col_args

    def test_calls_autofit(self, mock_writer, test_formats, test_data):
        data_out.apply_excel_formatting(mock_writer, test_data, test_formats, "Sheet1")
        ws = mock_writer.sheets["Sheet1"]
        ws.autofit.assert_called_once_with()


class TestCreatePickle:
    """
    Test class for data_out.create_pickle
    """

    @pytest.fixture
    def mock_to_pickle(self, mocker):
        return mocker.patch("pandas.to_pickle", return_value=None)

    @pytest.fixture
    def default_args(self, tmp_path):
        """
        Fixture to return the default arguments for create_pickle function
        """
        return {
            "output_workbooks": {
                "test": {"test": pd.DataFrame(columns=["col1", "col2"], data=[["val1", "val2"]])}
            },
            "output_directory": tmp_path,
            "fin_year": "test_year",
            "fin_month": "test_month",
        }

    @pytest.mark.parametrize(
        "call_count, expected_message",
        [
            (0, "Creating pickle file"),
            (1, "Creating pickle file for all regions for test_month test_year"),
        ],
    )
    def test_log_info_called(self, mock_log_levels, default_args, call_count, expected_message):
        """
        Test that create_pickle logs the correct info message
        """
        data_out.create_pickle(**default_args)
        mock_info = mock_log_levels["info"]

        assert mock_info.call_args_list[call_count][0][0] == expected_message

    def test_calls_warning_if_file_already_exists(
        self, mock_log_levels, default_args, mock_warning, tmp_path
    ):
        """
        Test that create_pickle logs a warning if the file already exists
        """
        output_file = tmp_path / "test_year_test_month_amber_report_all_regions.pkl"

        output_file.touch()  # Create the file to simulate it already existing
        data_out.create_pickle(**default_args)
        mock_warning.assert_called_once_with(
            f"Overwriting the existing pickle file: {output_file}"
        )

    def test_unlinks_file_if_already_exists(
        self, mock_log_levels, default_args, tmp_path, mock_to_pickle, mocker
    ):
        """
        Test that create_pickle unlinks the file if it already exists
        """
        mock_unlink = mocker.patch("os.unlink", return_value=None)  # Mock os.unlink to avoid actual file deletion
        output_file = tmp_path / "test_year_test_month_amber_report_all_regions.pkl"
        output_file.touch()

        data_out.create_pickle(**default_args)

        mock_unlink.assert_called_once()

    def test_calls_to_pickle(self, default_args, mock_to_pickle, tmp_path):
        """
        Test that create_pickle calls to_pickle with the correct arguments
        """
        data_out.create_pickle(**default_args)

        mock_to_pickle.assert_called_once()

        expected_file = tmp_path / "test_year_test_month_amber_report_all_regions.pkl"

        assert mock_to_pickle.call_args.args[0] == default_args["output_workbooks"]
        assert mock_to_pickle.call_args.args[1].name == str(expected_file)

    def test_calls_logger_success(self, mock_log_levels, default_args):
        """
        Test that create_pickle logs a success message
        """
        data_out.create_pickle(**default_args)

        mock_success = mock_log_levels["success"]
        expected_message = (
            "Pickle file for all regions for test_month test_year created successfully."
        )
        mock_success.assert_called_once_with(expected_message)
