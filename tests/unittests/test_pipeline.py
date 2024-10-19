"""
Tests for devices_rap/pipeline.py
"""

import pytest

from devices_rap import pipeline


def test_main():
    pipeline.amber_report_pipeline()
    assert True


if __name__ == "__main__":
    # This code allows the tests in the file to be run by running the file itself.
    pytest.main([__file__])
