"""
Backtests for the pipeline using month 12 data frome the financial year 2024-2025.
This file contains end-to-end tests for the pipeline, ensuring that it can handle the data correctly
and produce the expected results.
"""

import sys
import zipfile
import pickle
from pathlib import Path

import pytest
import pandas as pd

from devices_rap.pipeline import amber_report_pipeline
from devices_rap.constants import DATA_DIR


if sys.version_info < (3, 11):
    # For Python versions < 3.11, use the backport of ExceptionGroup
    from exceptiongroup import ExceptionGroup


def compare_nested_dicts(actual, expected, path=""):
    """
    Recursively compare two dictionaries whose values may be dictionaries or pandas DataFrames.
    Collects assertion errors and raises them as an ExceptionGroup at the end.
    Uses assert statements and error catching.
    """
    errors = []

    def _compare(actual, expected, path):
        try:
            if isinstance(expected, dict):
                assert isinstance(actual, dict), f"{path}: Actual value is not a dict"
                assert set(actual.keys()) == set(
                    expected.keys()
                ), f"{path}: Keys mismatch. Actual: {set(actual.keys())}, Expected: {set(expected.keys())}"
                assert len(actual) == len(
                    expected
                ), f"{path}: Dict size mismatch. Actual: {len(actual)}, Expected: {len(expected)}"
                for k in expected:
                    if k in actual:
                        _compare(actual[k], expected[k], f"{path}.{k}" if path else k)
            elif isinstance(expected, pd.DataFrame):
                assert isinstance(actual, pd.DataFrame), f"{path}: Actual value is not a DataFrame"
                try:
                    pd.testing.assert_frame_equal(actual, expected, check_dtype=True)
                except AssertionError as err:
                    errors.append(err)
            else:
                assert (
                    actual == expected
                ), f"{path}: Value mismatch. Actual: {actual}, Expected: {expected}"
        except AssertionError as err:
            errors.append(err)

    _compare(actual, expected, path)

    if errors:
        raise AssertionError from ExceptionGroup(
            "Nested dictionary comparison failed",
            errors
        )
        # raise ExceptionGroup("Nested dictionary comparison failed", errors)


class TestMonth12Year2425PipelineBacktest:
    """
    Test the pipeline with month 12 data from the financial year 2024-2025.
    This test ensures that the pipeline can handle the data correctly and produce the expected results.
    """

    @pytest.fixture
    def test_file_paths(self, tmp_path):
        """
        Unpacks the test files from a zip file into a temporary directory for testing.
        """
        test_zip_path = Path(DATA_DIR) / "2425_12_backtesting_data.zip"

        assert test_zip_path.exists(), f"Test zip file {test_zip_path} does not exist."

        # Unpack the zip file into the temporary directory
        with zipfile.ZipFile(test_zip_path, "r") as zip_ref:
            zip_ref.extractall(tmp_path)

        # Ensure the unpacked directory structure is correct
        assert (tmp_path / "input_data").exists(), "Input data directory does not exist."

        # Check that the files are in the correct location
        expected_files = [
            tmp_path / "input_data" / "provider_codes_lookup.csv",
            tmp_path / "input_data" / "2425" / "device_taxonomy.csv",
            tmp_path / "input_data" / "2425" / "12" / "master_data.csv",
            tmp_path / "input_data" / "2425" / "12" / "exception_report.csv",
            tmp_path / "expected.pkl",
        ]

        for file in expected_files:
            assert file.exists(), f"Expected file {file} does not exist."

        return tmp_path

    @pytest.fixture
    def expected_data(self, test_file_paths):
        """
        Loads the expected output data from the pickle file.
        """
        expected_output_path = test_file_paths / "expected.pkl"
        with open(expected_output_path, "rb") as f:
            expected_data = pickle.load(f)

        assert isinstance(expected_data, dict), "Expected data should be a dictionary."

        return expected_data

    def test_pipeline_backtest(self, expected_data, tmp_path):
        """
        Runs the pipeline with the test data and compares the output to the expected data.
        """
        raw_data_dir = tmp_path / "input_data"
        processed_data_dir = tmp_path / "processed_data"
        amber_report_pipeline(
            fin_month="12",
            fin_year="2425",
            use_multiprocessing=False,
            outputs=["pickle"],
            raw_data_dir=raw_data_dir,
            processed_data_dir=processed_data_dir,
        )

        # Load the actual output data
        actual_output_path = (
            processed_data_dir / "2425" / "12" / "2425_12_amber_report_all_regions.pkl"
        )
        assert (
            actual_output_path.exists()
        ), f"Actual output file {actual_output_path} does not exist."
        with open(actual_output_path, "rb") as f:
            actual_data = pickle.load(f)

        assert isinstance(actual_data, dict), "Actual data should be a dictionary."
        
        compare_nested_dicts(actual_data, expected_data)

