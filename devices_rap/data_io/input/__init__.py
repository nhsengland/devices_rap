"""
Data input module for loading various data formats.
"""

from devices_rap.data_io.input.csv_loader import load_devices_datasets
from devices_rap.data_io.input.sql_loader import load_sql_datasets

__all__ = ["load_devices_datasets", "load_sql_datasets"]
