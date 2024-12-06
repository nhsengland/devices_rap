# %%
"""
_summary_
"""
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from pandas._libs.tslibs.nattype import NaTType

from devices_rap.utils import (
    convert_fin_dates,
    convert_values_to,
    normalise_column_names,
    parse_dates,
)

# %%
PROJ_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJ_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
EXTERNAL_DATA_DIR.mkdir(parents=True, exist_ok=True)


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
    "unknown",
    "UNKNOWN",
    "na",
    "Not Known",
    "N/a",
    "NOT KNOWN",
    "<r>",
    "Not known",
    "***NOT LISTED/UNKNOWN/999999***",
]

# %%
master_df = pd.read_csv(
    RAW_DATA_DIR / "data_2425_master_m6.csv",
    na_values=na_values,
    skip_blank_lines=True,
    low_memory=False,
)

master_df = normalise_column_names(master_df)

# %%
exception_df = pd.read_csv(
    RAW_DATA_DIR / "exception_report_m6.csv",
    na_values=na_values,
    skip_blank_lines=True,
)

exception_df = exception_df[~(exception_df["PLCM Data Ref"].isna())]

exception_df = normalise_column_names(exception_df)


# %%
provider_codes_df = pd.read_csv(
    EXTERNAL_DATA_DIR / "provider_codes_lookup.csv",
    na_values=na_values,
    skip_blank_lines=True,
)

provider_codes_df = normalise_column_names(provider_codes_df)

# %%
device_taxonomy_df = pd.read_csv(
    EXTERNAL_DATA_DIR / "device_taxonomy_2425.csv",
    na_values=na_values,
    skip_blank_lines=True,
)

device_taxonomy_df = normalise_column_names(device_taxonomy_df)

# %%

master_df["upd_high_level_device_type"] = master_df["der_high_level_device_type"].apply(
    convert_values_to
)

master_df["upd_activity_year"] = master_df["cln_activity_year"].apply(
    convert_values_to, match=[2425], to=202425
)


# %%
# master_df["temp_activity_date"] = master_df.apply(
#     lambda df: (df["cln_activity_month"], df["upd_activity_year"]), axis=1
# )
master_df["activity_date"] = master_df.apply(
    lambda df: convert_fin_dates(df["cln_activity_month"], df["upd_activity_year"]), axis=1
)

# %%
master_df["activity_date_str"] = master_df["activity_date"].dt.strftime("%b %Y")

# %%
master_provider_df = pd.merge(
    left=master_df,
    left_on="der_provider_code",
    right=provider_codes_df,
    right_on="org_code",
    how="left",
    validate="many_to_one",
    indicator="_merge_with_provider_codes",
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
    left_on=["upd_high_level_device_type", "der_provider_code"],
    right=exception_df,
    right_on=["dev_code", "provider_code"],
    how="left",
    # validate="many_to_one",
    indicator="_merge_with_exception_report",
)

# %%
# Find values in exception_df that are not in master_devices_df
exception_not_in_master = exception_df[
    ~exception_df.set_index(["dev_code", "provider_code"]).index.isin(
        master_devices_df.set_index(["upd_high_level_device_type", "der_provider_code"]).index
    )
]

# Save the result to a CSV file
exception_not_in_master.groupby(["rag_status", "exception_status_combined"]).size().to_frame(
    "count"
)

# %%
# master_devices_df["provref"] = master_devices_df["der_provider_code"].fillna(
#     "NULL"
# ) + master_devices_df["upd_high_level_device_type"].fillna("NULL")

# alt_master_amber_df = pd.merge(
#     left=master_devices_df,
#     left_on="provref",
#     right=exception_df,
#     right_on="provref",
#     how="left",
#     # validate="many_to_one",
#     indicator="_merge_with_exception_report",
# )

# # %%
# master_devices_not_in_exception = master_amber_df[
#     master_amber_df["_merge_with_exception_report"] == "left_only"
# ]
# master_devices_not_in_taxonomy = master_devices_df[
#     master_devices_df["_merge_with_device_taxonomy"] == "left_only"
# ]
# master_devices_not_in_providers = master_devices_df[
#     master_devices_df["_merge_with_provider_codes"] == "left_only"
# ]

# # %%
# master_devices_not_in_exception.to_csv(PROCESSED_DATA_DIR / "master_devices_not_in_exception.csv")
# master_devices_not_in_taxonomy.to_csv(PROCESSED_DATA_DIR / "master_devices_not_in_taxonomy.csv")
# master_devices_not_in_providers.to_csv(PROCESSED_DATA_DIR / "master_devices_not_in_providers.csv")

# # %%
# devices_not_in_exception = (
#     master_devices_not_in_exception.groupby(["upd_high_level_device_type", "description_2024_25"])
#     .size()
#     .to_frame("count")
# )
# providers_not_in_exception = (
#     master_devices_not_in_exception.groupby(["der_provider_code"]).size().to_frame("count")
# )
# providers_devices_not_in_exception = (
#     master_devices_not_in_exception.groupby(
#         ["der_provider_code", "upd_high_level_device_type", "description_2024_25"]
#     )
#     .size()
#     .to_frame("count")
# )
# devices_not_in_taxonomy = (
#     master_devices_not_in_taxonomy.groupby(["upd_high_level_device_type"]).size().to_frame("count")
# )
# providers_not_in_lookup = (
#     master_devices_not_in_providers.groupby(["der_provider_code"]).size().to_frame("count")
# )

# # %%
# devices_not_in_exception.to_csv(PROCESSED_DATA_DIR / "devices_not_in_exception.csv")
# providers_not_in_exception.to_csv(PROCESSED_DATA_DIR / "providers_not_in_exception.csv")
# providers_devices_not_in_exception.to_csv(
#     PROCESSED_DATA_DIR / "providers_devices_not_in_exception.csv"
# )
# devices_not_in_taxonomy.to_csv(PROCESSED_DATA_DIR / "devices_not_in_taxonomy.csv")
# providers_not_in_lookup.to_csv(PROCESSED_DATA_DIR / "providers_not_in_lookup.csv")

# %%
master_amber_df["cln_activity_month"].unique()


# %%
values = "cln_total_cost"
index = ["nhs_england_region", "der_provider_code", "der_high_level_device_type", "rag_status"]
columns = "activity_date_str"
master_amber_pivot = pd.pivot_table(
    data=master_amber_df, values=values, index=index, columns=columns, aggfunc="sum"
).reset_index()


master_amber_detail_pivot = master_amber_pivot = pd.pivot_table(
    data=master_amber_df,
    values=values,
    index=[*index, "cln_manufacturer_device_name"],
    columns=columns,
    aggfunc="sum",
).reset_index()

# %%
rag_statuses = master_amber_df["rag_status"].unique()

for rag_status in rag_statuses:
    master_amber_pivot_rag = master_amber_pivot[master_amber_pivot["rag_status"] == rag_status]
    master_amber_pivot_rag.to_csv(PROCESSED_DATA_DIR / f"master_amber_pivot_{rag_status}.csv")


# %%
# master_df["raw_created_datetime"].unique()
# master_df["upt_device_insertion_date"] = pd.to_datetime(master_df["cln_device_insertion_date"], errors="coerce", dayfirst=True)

# master_df["cln_vat_charged"].unique()  # ? ['N', 'Y', nan, '0', 'S']  What is 'S'?


master_df["raw_created_datetime"] = master_df["raw_created_datetime"].apply(parse_dates)  # type: ignore


# %%
def dump_unique_values(df, df_name):
    """
    Dumps unique values of each column in the exception_df to a txt file.

    Args:
        exception_df (pd.DataFrame): The DataFrame containing the columns to be processed.
        data_dir (Path): The root data directory.
    """
    temp_dir = DATA_DIR / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    for column in df.columns:
        if df[column].dtype == "object":
            unique_values = df[column].unique()
            file_path = temp_dir / f"{df_name}_{column}.txt"
            with open(file_path, "w", encoding="utf-8") as file:
                for value in unique_values:
                    file.write(f"{value}\n")


# Example usage
# dump_unique_values(master_df, "master_df")

# %%
