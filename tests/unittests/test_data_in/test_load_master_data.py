"""
Tests for devices_rap/data_in.py
"""

import pandas as pd
import pytest

from devices_rap.data_in import load_master_data


class TestLoadDataMaster:
    """
    Tests for load_data_master
    """

    def test_loads_dataframe(self):
        """
        Tests if a dataframe is returned
        """
        actual = load_master_data.load_master_data()

        assert isinstance(actual, pd.DataFrame)

    def test_correct_schema(self):
        """
        Test if the dataframe has the correct schema
        """
        actual = load_master_data.load_master_data()
        expected = ...

        assert actual == expected


if __name__ == "__main__":
    # This code allows the tests in the file to be run by running the file itself.
    pytest.main([__file__])
