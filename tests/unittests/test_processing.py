"""
Tests for devices_rap/processing.py
"""

import pytest

# from devices_rap import processing


pytestmark = pytest.mark.no_data_needed


class TestTranslateHighLeveLDevicesType:
    """
    Tests for processing.translate_high_level_devices_type
    """

    @pytest.mark.xfail()
    def test_empty_input(self):
        """
        _summary_
        """


class TestLookupProviderCodes:
    """
    Tests for processing.lookup_provider_codes
    """

    @pytest.mark.xfail()
    def test_empty_input(self):
        """
        _summary_
        """


class TestLookupTaxonomyTariff:
    """
    Tests for processing.lookup_taxonomy_tariff
    """

    @pytest.mark.xfail()
    def test_empty_input(self):
        """
        _summary_
        """


if __name__ == "__main__":
    pytest.main([__file__])
