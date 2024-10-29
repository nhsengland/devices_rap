"""
Tests for devices_rap/pipeline.py
"""

import pytest

# from devices_rap import pipeline


pytestmark = pytest.mark.no_data_needed


class TestAmberReportPipeline:
    """
    Test class for create_excel_reports
    """

    @pytest.mark.xfail()
    def test_tbc(self):
        """
        Test to be confirmed
        """


if __name__ == "__main__":
    # This code allows the tests in the file to be run by running the file itself.
    pytest.main([__file__])
