# %%
"""
_summary_
"""

from typing import Any, Dict, List, Optional
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

    replace_values = (
        {
            "-": "",
            "  ": " ",
            "(": "",
            ")": "",
            "/": "_",
            ".": "_",
            " ": "_",
        }
        if not replace_values
        else replace_values
    )

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
device_taxonomy_df = pd.read_csv(
    r"/home/jowi60/direct_commissioning/devices_rap/data/external/device_taxonomy_2425.csv",
    na_values=na_values,
    skip_blank_lines=True,
)

device_taxonomy_df = normalise_column_names(device_taxonomy_df)

# %%


def convert_values_to(
    input: Any, match: Optional[List[Any]] = None, to: Any = "DEV02", invert_match: bool = False
) -> Any:
    """
    If input matches the match list then it is converted to the provided "to" value. If invert_match
    is true then every value not in the match list will be converted and only matches will
    be unchanged.

    Parameters
    ----------
    input : Any
        Value to convert if they are a match
    match : List[Any], optional
        List of values to match the input to, by default ["DEV34", "DEV35"]
    to : Any, optional
        Value to convert matched inputs to, by default "DEV02"
    invert_match : bool, optional
        Invert the match, and convert values that do not match the provided match list, defaults to
        False

    Returns
    -------
    Any
        Converted value or current value if not a match
    """
    match = ["DEV34", "DEV35"] if not match else match
    if invert_match:
        return to if input not in match else input
    else:
        return to if input in match else input


master_df["upd_high_level_device_type"] = master_df["der_high_level_device_type"].apply(
    convert_values_to
)

# %%
master_provider_df = pd.merge(
    left=master_df,
    left_on="der_provider_code",
    right=provider_codes_df,
    right_on="org_code",
    how="left",
    validate="many_to_one",
    indicator="_merge_with_provider_codes"
)

# %%
master_devices_df = pd.merge(
    left=master_provider_df,
    left_on="upd_high_level_device_type",
    right=device_taxonomy_df,
    right_on="dev_code",
    how="left",
    validate="many_to_one",
    indicator="_merge_with_device_taxonomy",
)

# %%
master_amber_df = pd.merge(
    left=master_devices_df,
    left_on=[
        "upd_high_level_device_type", "der_provider_code"],
    right=exception_df,
    right_on=["dev_code", "provider_code"],
    how="left",
    # validate="many_to_one",
    indicator="_merge_with_exception_report",
)

# %%
exception_cln_df = exception_df[exception_df["dev_code"].notna()]
master_amber_cln_df = pd.merge(
    left=master_devices_df,
    left_on=["upd_high_level_device_type", "der_provider_code"],
    right=exception_cln_df,
    right_on=["dev_code", "provider_code"],
    how="left",
    # validate="many_to_one",
    indicator="_merge_with_exception_report",
)

# %%
