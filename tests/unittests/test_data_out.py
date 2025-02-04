"""
Tests for devices_rap/data_out.py
"""

from uuid import uuid4
import pytest
import pandas as pd
from xlsxwriter.format import Format

from devices_rap import data_out
from devices_rap.data_out import create_excel_reports, process_region

# from devices_rap import data_out


pytestmark = pytest.mark.no_data_needed


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

    def test_create_excel_reports_creates_output_dir(
        self, mocker, mock_output_directory, mock_process_region
    ):
        """
        Test that create_excel_reports creates the output directory
        """
        mocker.patch("devices_rap.data_out.PROCESSED_DATA_DIR", mock_output_directory)
        mocker.patch("devices_rap.data_out.FIN_YEAR", "2021")
        mocker.patch("devices_rap.data_out.FIN_MONTH", "01")

        expected_output_dir = mock_output_directory / "2021" / "01"

        create_excel_reports({})

        assert expected_output_dir.exists()

    @pytest.mark.parametrize("use_multiprocessing", [True, False])
    @pytest.mark.parametrize(
        "output_workbooks, call_count", [({}, 0), ({"region1": {"sheet1": pd.DataFrame()}}, 1)]
    )
    def test_create_excel_reports_calls_process_region(
        self,
        mocker,
        mock_output_directory,
        mock_process_region,
        use_multiprocessing,
        output_workbooks,
        call_count,
    ):
        """
        Test that create_excel_reports calls process_region
        """
        mocker.patch("devices_rap.data_out.USE_MULTIPROCESSING", use_multiprocessing)
        create_excel_reports(output_workbooks, output_directory=mock_output_directory)
        assert mock_process_region.call_count == call_count

    @pytest.mark.parametrize("use_multiprocessing", [True, False])
    @pytest.mark.parametrize(
        "kwarg, expected_value",
        [
            ("fin_output_directory", None),
            ("region", "region1"),
            ("worksheets", {"sheet1": pd.DataFrame()}),
        ],
    )
    def test_create_excel_reports_calls_process_region_with_correct_args(
        self,
        mocker,
        mock_output_directory,
        mock_process_region,
        use_multiprocessing,
        kwarg,
        expected_value,
    ):
        """
        Test that create_excel_reports calls process_region with the correct arguments
        """
        mocker.patch("devices_rap.data_out.USE_MULTIPROCESSING", use_multiprocessing)
        mocker.patch("devices_rap.data_out.FIN_YEAR", "2021")
        mocker.patch("devices_rap.data_out.FIN_MONTH", "01")

        output_workbooks = {"region1": {"sheet1": pd.DataFrame()}}
        create_excel_reports(output_workbooks, output_directory=mock_output_directory)
        actual = mock_process_region.call_args[1][kwarg]

        if kwarg == "fin_output_directory":
            assert actual == mock_output_directory / "2021" / "01"
        elif kwarg == "worksheets":
            assert actual.keys() == expected_value.keys()
            pd.testing.assert_frame_equal(actual["sheet1"], expected_value["sheet1"])
        else:
            assert actual == expected_value

    @pytest.mark.parametrize(
        "log_type, expected_message",
        [("info", "Creating excel reports"), ("success", "Excel reports created successfully.")],
    )
    def test_log_called(
        self,
        mock_log_levels,
        mock_output_directory,
        mock_process_region,
        log_type,
        expected_message,
    ):
        """
        Test that the loguru.logger is called
        """
        create_excel_reports({}, output_directory=mock_output_directory)

        mock_log = mock_log_levels[log_type]

        mock_log.assert_called_once_with(expected_message)


class TestProcessRegion:
    """
    Test class for data_out.process_region
    """

    @pytest.fixture
    def fin_output_directory(self, tmp_path):
        output_directory = tmp_path / "test_output" / "2021" / "01"
        output_directory.mkdir(parents=True, exist_ok=True)
        return output_directory

    @pytest.fixture
    def mock_create_excel_file(self, mocker):
        return mocker.patch("devices_rap.data_out.create_excel_file")

    def test_calls_create_excel_file_once(self, fin_output_directory, mock_create_excel_file):
        """
        Test that process_region calls create_excel_file once
        """
        region = "region1"
        worksheets = {"sheet1": pd.DataFrame()}
        process_region(fin_output_directory, region, worksheets)
        assert mock_create_excel_file.call_count == 1

    @pytest.mark.parametrize(
        "kwarg, expected_value",
        [
            ("output_file", "REGION1_RAG_STATUS_REPORT.xlsx"),
            ("worksheets", {"sheet1": pd.DataFrame()}),
        ],
    )
    def test_calls_create_excel_file_with_correct_args(
        self, fin_output_directory, mock_create_excel_file, kwarg, expected_value
    ):
        """
        Test that process_region calls create_excel_file with the correct arguments
        """
        region = "region1"
        worksheets = {"sheet1": pd.DataFrame()}
        process_region(fin_output_directory, region, worksheets)
        actual = mock_create_excel_file.call_args[1][kwarg]

        if kwarg == "output_file":
            assert actual == fin_output_directory / "REGION1_RAG_STATUS_REPORT.xlsx"
        else:
            assert actual.keys() == expected_value.keys()
            pd.testing.assert_frame_equal(actual["sheet1"], expected_value["sheet1"])

    def test_logs_success_message(
        self, fin_output_directory, mock_create_excel_file, mock_log_levels
    ):
        """
        Test that process_region logs a success message
        """
        region = "region1"
        worksheets = {"sheet1": pd.DataFrame()}

        process_region(fin_output_directory, region, worksheets)

        mock_success = mock_log_levels["success"]
        mock_success.assert_called_once_with("Excel report for region1 created successfully.")

    def test_logs_info_when_file_does_not_exist(
        self, fin_output_directory, mock_create_excel_file, mock_log_levels
    ):
        """
        Test that process_region logs an info message when the file does not exist
        """
        region = "region1"
        worksheets = {"sheet1": pd.DataFrame()}
        process_region(fin_output_directory, region, worksheets)
        mock_info = mock_log_levels["info"]
        mock_info.assert_called_once_with("Creating Excel report for region1")

    def test_logs_warning_when_file_exists(
        self, fin_output_directory, mock_create_excel_file, mock_log_levels
    ):
        """
        Test that process_region logs an info message when the file does not exist
        """
        region = "region1"
        worksheets = {"sheet1": pd.DataFrame()}

        output_file = fin_output_directory / "REGION1_RAG_STATUS_REPORT.xlsx"
        output_file.touch()

        process_region(fin_output_directory, region, worksheets)

        mock_warning = mock_log_levels["warning"]
        mock_warning.assert_called_once_with(f"Overwriting the existing Excel file: {output_file}")

    def test_deletes_file_when_file_exists(
        self, fin_output_directory, mock_create_excel_file, mock_log_levels
    ):
        """
        Test that process_region logs an info message when the file does not exist
        """
        region = "region1"
        worksheets = {"sheet1": pd.DataFrame()}

        output_file = fin_output_directory / "REGION1_RAG_STATUS_REPORT.xlsx"
        output_file.touch()

        process_region(fin_output_directory, region, worksheets)

        assert not output_file.exists()


class TestCreateExcelFile:
    """
    Test class for data_out.create_excel_file
    """

    @pytest.fixture
    def output_file(self, tmp_path):
        return tmp_path / "test_output.xlsx"

    @pytest.fixture
    def mock_create_header_format(self, mocker):
        return mocker.patch(
            "devices_rap.data_out.create_header_format", return_value="header_format"
        )

    @pytest.fixture
    def mock_write_worksheet(self, mocker):
        return mocker.patch("devices_rap.data_out.write_worksheet", return_value=None)

    @pytest.mark.parametrize("use_multiprocessing", [True, False])
    def test_calls_write_worksheet(
        self,
        mocker,
        output_file,
        mock_create_header_format,
        mock_write_worksheet,
        use_multiprocessing,
    ):
        """
        Test that create_excel_file calls write_worksheet
        """
        mocker.patch("devices_rap.data_out.USE_MULTIPROCESSING", use_multiprocessing)
        worksheets = {"sheet1": pd.DataFrame()}
        data_out.create_excel_file(output_file, worksheets)
        assert mock_write_worksheet.call_count == 1

    @pytest.mark.parametrize("use_multiprocessing", [True, False])
    @pytest.mark.parametrize(
        "kwarg, expected_value",
        [
            ("writer", None),
            ("sheet_name", "sheet1"),
            ("data", pd.DataFrame()),
            ("header_format", "header_format"),
            ("output_file", None),
        ],
    )
    def test_calls_write_worksheet_with_correct_args(
        self,
        mocker,
        output_file,
        mock_create_header_format,
        mock_write_worksheet,
        use_multiprocessing,
        kwarg,
        expected_value,
    ):
        """
        Test that create_excel_file calls write_worksheet with the correct arguments
        """
        mocker.patch("devices_rap.data_out.USE_MULTIPROCESSING", use_multiprocessing)
        worksheets = {"sheet1": pd.DataFrame()}
        data_out.create_excel_file(output_file, worksheets)
        actual = mock_write_worksheet.call_args[1][kwarg]

        if kwarg == "writer":
            assert isinstance(actual, pd.ExcelWriter)
        elif kwarg == "data":
            pd.testing.assert_frame_equal(actual, expected_value)
        elif kwarg == "output_file":
            assert actual == output_file
        else:
            assert actual == expected_value

    def test_calls_create_header_format_once(
        self, output_file, mock_create_header_format, mock_write_worksheet
    ):
        """
        Test that create_excel_file calls create_header_format once
        """
        worksheets = {"sheet1": pd.DataFrame()}
        data_out.create_excel_file(output_file, worksheets)
        assert mock_create_header_format.call_count == 1

    def test_logs_debug(
        self, output_file, mock_create_header_format, mock_write_worksheet, mock_log_levels
    ):
        """
        Test that create_excel_file logs a debug message
        """
        worksheets = {"sheet1": pd.DataFrame()}
        data_out.create_excel_file(output_file, worksheets)
        mock_debug = mock_log_levels["debug"]
        mock_debug.assert_called_once_with(f"Creating the Excel file: {output_file}")


class TestCreateHeaderFormat:
    """
    Test class for data_out.create_header_format
    """

    def test_returns_header_format(self, tmp_path):
        """
        Test that create_header_format returns an object
        """
        path = tmp_path / f"{uuid4()}_test_output.xlsx"
        with pd.ExcelWriter(path=path, engine="xlsxwriter") as writer:
            actual = data_out.create_header_format(writer.book)

            assert isinstance(actual, Format)

    @pytest.mark.parametrize(
        "attr, expected",
        [
            ("bold", True),
            ("text_wrap", True),
            ("text_v_align", 1),
            ("fg_color", "#D9E1F2"),
            ("top", 1),
            ("bottom", 1),
            ("left", 1),
            ("right", 1),
        ],
    )
    def test_header_format_has_correct_properties(self, tmp_path, attr, expected):
        """
        Test that the header format has the correct properties
        """
        path = tmp_path / f"{uuid4()}_test_output.xlsx"
        with pd.ExcelWriter(path=path, engine="xlsxwriter") as writer:
            header_format = data_out.create_header_format(writer.book)
            assert getattr(header_format, attr) == expected


class TestWriteWorksheet:
    """
    Test class for data_out.write_worksheet
    """

    @pytest.fixture
    def mock_to_excel(self, mocker):
        return mocker.patch("pandas.DataFrame.to_excel", return_value=None)

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
            "header_format": "header_format",
            "output_file": tmp_path / "output_file",
        }

    def test_calls_to_excel(self, default_args, mock_to_excel):
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
        self, mocker, default_args, mock_to_excel, kwarg, expected_value
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

    def test_calls_write_method(self, mocker, mock_to_excel, default_args):
        """
        Test that write_worksheet calls the write method
        """
        mock_writer = default_args["writer"]

        data_out.write_worksheet(
            **default_args,
        )

        assert mock_writer.sheets["sheet1"].write.call_count == 2

    @pytest.mark.parametrize(
        "expected_value",
        [
            (0, 0, "col1", "header_format"),
            (0, 1, "col2", "header_format"),
        ],
    )
    def test_calls_write_method_with_correct_args(
        self, mocker, mock_to_excel, default_args, expected_value
    ):
        """
        Test that write_worksheet calls the write method with the correct arguments
        """
        mock_writer = default_args["writer"]

        data_out.write_worksheet(
            **default_args,
        )

        mock_writer.sheets["sheet1"].write.assert_any_call(
            *expected_value,
        )


if __name__ == "__main__":
    # This code allows the tests in the file to be run by running the file itself.
    pytest.main([__file__])
