"""
Tests for devices_rap/data_in.py
"""

import pandas as pd
import pytest

from devices_rap.data_in import load_data


pytestmark = pytest.mark.data_needed


class TestProviderCodesLookup:
    """
    Tests for load_data_master
    """

    # @pytest.mark.xfail()
    def test_loads_dataframe(self):
        """
        Tests if a dataframe is returned
        """
        actual = load_data.load_provider_codes_lookup()

        assert isinstance(actual, pd.DataFrame)

    @pytest.mark.xfail()
    def test_correct_schema(self):
        """
        Test if the dataframe has the correct schema
        """
        actual = load_data.load_provider_codes_lookup()
        expected = ...

        assert actual == expected


if __name__ == "__main__":
    # This code allows the tests in the file to be run by running the file itself.
    pytest.main([__file__])
