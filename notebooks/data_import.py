# %%
"""
_summary_
"""

from typing import Dict, Optional
import pandas as pd
import numpy as np

# %%
na_values = [
    "(blank)",
    "tbc",
    "-",
    "......................",
    "NA",
    "n/a",
    "Not Specified",
    "tbc ",
    "…...................",
    # "00:00.0",
    "(NOT KNOWN)",
]


# %%
def normalise_column_names(
    df: pd.DataFrame,
    to_lower: bool = True,
    strip: bool = True,
    replace_values: Optional[Dict[str, str]] = None,
) -> pd.DataFrame:
    """
    Normalise the column names of a dataframe. By default:
        * The column names are cast to all lower case
        * Whitespace around the columns are remove
        * Punctuation and spaces are removed or replaced with underscores, "_".

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe with messy column names
    to_lower : bool, optional
        Cast column names to lower case, by default True
    strip : bool, optional
        Strip whitespace from start and end of column names, by default True
    replace_values : Optional[Dict[str, str]], optional
        Dictionary of values to be replaces, by default {
        "-": "",
        "  ": " ",
        "(": "",
        ")": "",
        "/": "_",
        ".": "_",
        " ": "_",
    }

    Returns
    -------
    pd.DataFrame
        Dataframe with cleaned column names
    """
    if to_lower:
        df.columns = df.columns.str.lower()

    if strip:
        df.columns = df.columns.str.strip()

    replace_values = {
        "-": "",
        "  ": " ",
        "(": "",
        ")": "",
        "/": "_",
        ".": "_",
        " ": "_",
    } if not replace_values else replace_values

    for pat, repl in replace_values.items():
        df.columns = df.columns.map(lambda x: x.replace(pat, repl))

    return df


# %%
master_df = pd.read_csv(
    r"/home/jowi60/direct_commissioning/devices_rap/data/raw/data_2425_master_m6.csv",
    na_values=na_values,
    skip_blank_lines=True,
    low_memory=False,
)

master_df = normalise_column_names(master_df)

# %%
exception_df = pd.read_csv(
    r"/home/jowi60/direct_commissioning/devices_rap/data/raw/exception_report_m6.csv",
    na_values=na_values,
    skip_blank_lines=True,
)

exception_df = exception_df[~(exception_df["PLCM Data Ref"].isna())]

exception_df = normalise_column_names(exception_df)


# %%
provider_codes_df = pd.read_csv(
    r"/home/jowi60/direct_commissioning/devices_rap/data/external/provider_codes_lookup.csv",
    na_values=na_values,
    skip_blank_lines=True,
)

provider_codes_df = normalise_column_names(provider_codes_df)

# %%
device_taxonomy = pd.read_csv(
    r"/home/jowi60/direct_commissioning/devices_rap/data/external/device_taxonomy_2425.csv",
    na_values=na_values,
    skip_blank_lines=True,
)

device_taxonomy = normalise_column_names(device_taxonomy)

# %%

