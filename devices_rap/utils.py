"""
Miscellaneous helper functions that can be used over multiple modules.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from devices_rap.errors import InvalidMonthError


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
        df.columns = df.columns.map(lambda x, pat=pat, repl=repl: x.replace(pat, repl))

    return df


def un_normalise_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes a DataFrame, removes any underscores from the column names, and converts them to title
    case, getting them ready for human friendly presentation.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame with normalised column names (lower case, underscores)

    Returns
    -------
    pd.DataFrame
        The DataFrame with un-normalised column names (title case, spaces)
    """
    df.columns = df.columns.str.replace("_", " ").str.title()
    return df


def convert_values_to(
    value: Any, match: Optional[List[Any]] = None, to: Any = "DEV02", invert_match: bool = False
) -> Any:
    """
    If value matches the match list then it is converted to the provided "to" value. If invert_match
    is true then every value not in the match list will be converted and only matches will
    be unchanged.

    Parameters
    ----------
    value : Any
        Value to convert if they are a match
    match : List[Any], optional
        List of values to match the value to, by default ["DEV34", "DEV35"]
    to : Any, optional
        Value to convert matched values to, by default "DEV02"
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
        return to if value not in match else value
    return to if value in match else value


def convert_fin_dates(fin_month: int, fin_year: int) -> pd.Timestamp:
    """
    Convert financial dates to a pandas datetime, assuming the financial year starts in April and
    the year is given in the form of CCYY1YY2 so 2024-2025 will be 202425

    Parameters
    ----------
    fin_month : int
        Financial month, assumes 1 is April and 12 is March
    fin_year : int
        Financial year, in the format CCYY1YY2, e.g. 202425 is equivalent to 2024-2025

    Returns
    -------
    pd.Timestamp
        Corresponding datetime
    """
    if fin_month < 1 or fin_month > 12:
        raise InvalidMonthError("Invalid month. Month should be between 1 and 12.")
    fin_year_str = str(fin_year)
    century = fin_year_str[:2]
    year_1 = fin_year_str[2:4]
    year_2 = fin_year_str[4:]
    if fin_month <= 9:
        year = century + year_1
        month = str(fin_month + 3)
    else:
        year = century + year_2
        month = str(fin_month - 9)

    return pd.to_datetime(f"{month}, {year}")


def parse_dates(date_str: str) -> Union[pd.Timestamp, pd.NaT, datetime]:  # type: ignore
    """
    Parses a date string into a pandas Timestamp, NaT, or datetime object.
    The function attempts to parse the input date string using the following formats:
        1. "%d/%m/%Y %H:%M" - Day/Month/Year Hour:Minute
        2. "%d/%m/%Y" - Day/Month/Year
        3. Excel serial date format - Days since 1899-12-30
    If the input string cannot be parsed using any of these formats, the function returns pandas NaT.

    Parameters:
        date_str (str): The date string to be parsed.
    Returns:
        pd.Timestamp | NaTType | datetime: The parsed date as a pandas Timestamp, NaT, or datetime object.
    """
    try:
        return pd.to_datetime(date_str, format="%d/%m/%Y %H:%M")
    except ValueError:
        try:
            return pd.to_datetime(date_str, format="%d/%m/%Y")
        except ValueError:
            try:
                return datetime(1899, 12, 30) + timedelta(days=float(date_str))
            except ValueError:
                return pd.NaT
