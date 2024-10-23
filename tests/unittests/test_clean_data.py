"""
Tests for devices_rap/clean_data.py
"""

import pytest

# from devices_rap import clean_data


pytestmark = pytest.mark.no_data_needed


class TestCleanseMasterData:
    """
    Tests for clean_data.cleanse_master_data
    """

    @pytest.mark.xfail()
    def test_empty_input(self):
        """
        Tests if the function can handle an empty input correct
        """


class TestCleanseExceptionsData:
    """
    Tests for clean_data.cleanse_exceptions_data
    """

    @pytest.mark.xfail()
    def test_empty_input(self):
        """
        Tests if the function can handle an empty input correct
        """


class TestCleanseProviderData:
    """
    Tests for clean_data.cleanse_provider_data
    """

    @pytest.mark.xfail()
    def test_empty_input(self):
        """
        Tests if the function can handle an empty input correct
        """


if __name__ == "__main__":
    pytest.main([__file__])
