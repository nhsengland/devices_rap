"""
Perform end-to-end tests for the load_csv module.
"""

from uuid import uuid4

from nhs_herbot.load_csv import load_csv_data
import pandas as pd
import pytest

from devices_rap.data_io.utils import NA_VALUES


@pytest.fixture
def create_temp_csv_file(tmp_path):
    """
    Fixture to create a temporary CSV file with test data, returning the file path, and then
    deleting the file and the _test directory after the test has run.
    """

    test_csv_data = {
        "columns": ["column_1", "column_2"],
        "data": [
            ("test_valid_1", "foo"),
            ("test_valid_2", "bar"),
            ("test_valid_3", "baz"),
            *[(f"test_{NA_VALUES.index(na_value)}", na_value) for na_value in NA_VALUES],
            (None, None),
            (None, None),
        ],
    }
    test_csv_df = pd.DataFrame(**test_csv_data)

    test_csv_file_path = tmp_path / f"_{uuid4()}_test_data.csv"

    assert not test_csv_file_path.exists()

    test_csv_df.to_csv(test_csv_file_path, index=False)

    return test_csv_file_path


def test_fixture_create_temp_csv_file(create_temp_csv_file):
    """
    Test that the create_temp_csv_file fixture creates a temporary CSV file.
    """
    assert create_temp_csv_file.exists()


class TestLoadCSVData:
    """
    End-to-end tests (with an actual CSV) for the load_csv_data function.
    """

    @pytest.mark.parametrize("na_value", [None, *NA_VALUES])
    def test_no_na_values(self, create_temp_csv_file, na_value):
        """
        Test that the function loads a CSV file with no NA values.
        """
        result = load_csv_data("test", filepath_or_buffer=create_temp_csv_file, na_values=na_value)
        assert na_value not in result.values

    def test_skipped_blank_lines(self, create_temp_csv_file):
        """
        Test that the function skips blank lines in the CSV file.
        """
        actual = len(load_csv_data("test", filepath_or_buffer=create_temp_csv_file))
        expected = 3 + len(NA_VALUES)
        assert actual == expected


if __name__ == "__main__":
    pytest.main([__file__])
