"""
Tests for devices_rap/data_in.py
"""

import pandas as pd
import pytest

from devices_rap.data_in import load_exceptions_data


pytestmark = pytest.mark.data_needed


class TestLoadExceptionsData:
    """
    Tests for load_data_master
    """

    @pytest.mark.xfail()
    def test_loads_dataframe(self):
        """
        Tests if a dataframe is returned
        """
        actual = load_exceptions_data.load_exceptions_data()

        assert isinstance(actual, pd.DataFrame)

    @pytest.mark.xfail()
    def test_correct_schema(self):
        """
        Test if the dataframe has the correct schema
        """
        actual = load_exceptions_data.load_exceptions_data()
        expected = ...

        assert actual == expected


if __name__ == "__main__":
    # This code allows the tests in the file to be run by running the file itself.
    pytest.main([__file__])
