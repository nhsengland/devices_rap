"""
Perform end-to-end tests for the load_csv module.
"""

import pytest

from devices_rap.data_in.load_csv import NA_VALUES, load_csv_data


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
        result = load_csv_data("test", filepath_or_buffer=create_temp_csv_file)
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
