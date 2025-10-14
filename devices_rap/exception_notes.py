""" """

from loguru import logger
from nhs_herbot.errors import ColumnsNotFoundError
import pandas as pd
import tqdm

tqdm.tqdm.pandas()


def column_summary_notes(
    row, columns_to_summarise: dict[str, str], match_summaries: dict[str, str]
) -> pd.Series:
    """
    Generate a summary of the columns in the row that match the given values. The function will
    loop through the groups in match_summaries and check the keys in columns_to_summarise for
    matches. If a match is found, the note for the column is added to the summary (which is the
    value of the columns_to_summarise).

    Parameters
    ----------
    row : pd.Series
        The row to summarise
    columns_to_summarise : dict
        The columns to summarise with the note to add to the summary
    match_summaries : dict
        The matches to summarise with the group to add to the summary

    Returns
    -------
    pd.Series
        The summary of the row

    Examples
    --------
    >>> row = pd.Series({"col1": "Y", "col2": "N", "col3": "Ceased"})
    >>> columns_to_summarise = {col1: "Note 1", col2: "Note 2", col3: "Note 3"}
    >>> match_summaries = {"Group 1": "Y", "Group 2": "Ceased"}
    >>> column_summary_notes(row, columns_to_summarise, match_summaries)
    summary    Group 1: Note 1. Group 2: Note 3.
    """
    summary = ""

    try:
        for group, match in match_summaries.items():
            group_list = []
            for col, note in columns_to_summarise.items():
                if row[col] == match:
                    group_list.append(note)
            if group_list:
                group_list_end = ", ".join(group_list)
                group_list_str = f"{group.title()}: {group_list_end}. "
            else:
                group_list_str = ""
            summary += group_list_str

        summary = summary.strip()
    except KeyError as e:
        raise ColumnsNotFoundError(
            dataset_columns=row.index, match_columns=columns_to_summarise.keys()
        ) from e

    if not summary:
        summary = None

    return pd.Series(summary, index=["summary"], dtype="string")


def create_exception_notes(exceptions: pd.DataFrame, drop_columns: bool = True) -> pd.DataFrame:
    """
    Function to create a summary of the exception columns in the exceptions DataFrame. The function
    is a wrapper apply function that calls the column_summary_notes function to generate the
    `exception_notes` column, where the `columns_to_summarise` is defined as:
    ```python
    {
        "exception_status_legacy_list": "Legacy List",
        "exception_status_planned_migration": "Planned Migration",
        "exception_status_category_list": "Category List",
        "exception_status_product_list": "Product List",
        "exception_status_hcted_category": "Hcted Category",
        "exception_status_stock_<180_days": "Stock <180 Days",
    }
    ```
    and the `match_summaries` is defined as:
    ```python
    {
        "Exceptions": "Y",
        "Ceased": "Ceased",
    }
    ```

    Parameters
    ----------
    exceptions : pd.DataFrame
        The exceptions DataFrame to create the exception notes for

    Returns
    -------
    pd.DataFrame
        The exceptions DataFrame with the `exception_notes` column added
    """
    logger.info("Creating exception notes column")
    columns_to_summarise = {
        "exception_status_legacy_list": "Legacy List",
        "exception_status_planned_migration": "Planned Migration",
        "exception_status_category_list": "Category List",
        "exception_status_product_list": "Product List",
        "exception_status_hcted_category": "Hcted Category",
        "exception_status_stock_<180_days": "Stock <180 Days",
    }

    match_summaries = {
        "Exceptions": "Y",
        "Ceased": "Ceased",
    }

    exceptions["exception_notes"] = exceptions.progress_apply(
        column_summary_notes,
        axis=1,
        columns_to_summarise=columns_to_summarise,
        match_summaries=match_summaries,
    )  # type: ignore

    if drop_columns:
        exceptions = exceptions.drop(columns=list(columns_to_summarise.keys()))

    return exceptions
