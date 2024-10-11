"""
Tests for rap_devices/pipeline.py
"""

import pytest

from rap_devices import pipeline


def test_main():
    pipeline.devices_pipeline()
    assert True


if __name__ == "__main__":
    # This code allows the tests in the file to be run by running the file itself.
    pytest.main([__file__])
