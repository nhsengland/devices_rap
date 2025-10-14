# Amber Report Excel Output Documentation

This document describes the structure and content of each worksheet in the Amber Report Excel output file.

## Overview

The Excel output contains multiple worksheets, each configured with specific columns, filters, and sorting criteria. The worksheets are designed to provide different views of the device data based on RAG status and migration status.

## Types of Worksheets

The Amber Report Excel output includes the following types of worksheets:

| Worksheet Type   | Aggregation |
|------------------|-------------|
 Summary | Sum Total Cost per Month. <br>Grouped by Region, Provider Code, High-Level Device Type, RAG Status | <!-- markdownlint-disable-line MD033 MD056 MD055-->
| Detailed | Sum Total Cost per Month. <br>Grouped by Region, Provider Code, High-Level Device Type, Manufacturer, Manufacturer Device Name, RAG Status | <!-- markdownlint-disable-line MD033 MD056 MD055-->
| Data | No Aggregation, a raw view of the underlying data |

## Worksheet Descriptions

### AMBER Summary

- **Type**: Summary view
- **Purpose**: Provides a [summary](#types-of-worksheets) view of AMBER status migrated devices, showing total cost per month over the last 12 months.
- **Filters**:
    - RAG Status: AMBER only
    - Migration Status: Migrated categories only (`upd_migrated_categories: True`)
- **Columns**:
    - Region
    - Provider Code
    - Provider Name
    - High Level Device Type
    - Device Category
    - RAG Status
    - ZCM Handover Date
    - VCM Handover Date
    - Total Cost (showing the last 12 months of data)
    - Exception Notes
    - Change from Previous Month
- **Sorting**: By Region, Provider Code, High Level Device Type, RAG Status
- **Sub-totals**: Grouped by Region and Provider Code

### AMBER Detailed

- **Type**: Detailed view
- **Purpose**: Provides a [detailed](#types-of-worksheets) view of AMBER status migrated devices, showing total cost per month over the last 12 months.
- **Filters**:
    - RAG Status: AMBER only
    - Migration Status: Migrated categories only (`upd_migrated_categories: True`)
- **Columns**:
    - Region
    - Provider Code
    - Provider Name
    - High Level Device Type
    - Device Category
    - Manufacturer
    - Manufacturer Device Name
    - RAG Status
    - Total Cost (showing the last 12 months of data)
- **Sorting**: By Region, Provider Code, High Level Device Type, RAG Status
- **Sub-totals**: Grouped by Region and Provider Code

### RED Summary

- **Type**: Summary view
- **Purpose**: Provides a [summary](#types-of-worksheets) view of RED and YELLOW status migrated devices, showing total cost per month over the last 12 months.
- **Filters**:
    - RAG Status: RED and YELLOW
    - Migration Status: Migrated categories only (`upd_migrated_categories: True`)
- **Columns**:
    - Region
    - Provider Code
    - Provider Name
    - High Level Device Type
    - Device Category
    - RAG Status
    - ZCM Handover Date
    - VCM Handover Date
    - Total Cost (showing the last 12 months of data)
- **Sorting**: By Region, Provider Code, High Level Device Type, RAG Status
- **Sub-totals**: Grouped by Region and Provider Code

### RED Detailed

- **Type**: Detailed view
- **Purpose**: Provides a [detailed](#types-of-worksheets) view of RED and YELLOW status migrated devices, showing total cost per month over the last 12 months.
- **Filters**:
    - RAG Status: RED and YELLOW
    - Migration Status: Migrated categories only (`upd_migrated_categories: True`)
- **Columns**:
    - Region
    - Provider Code
    - Provider Name
    - High Level Device Type
    - Device Category
    - Manufacturer
    - Manufacturer Device Name
    - RAG Status
    - Total Cost (showing the last 12 months of data)
- **Sorting**: By Region, Provider Code, High Level Device Type, RAG Status
- **Sub-totals**: Grouped by Region and Provider Code

### NON-MIGRATED Summary

- **Type**: Summary view
- **Purpose**: Provides a [summary](#types-of-worksheets) view of non-migrated devices, showing total cost per month over the last 12 months.
- **Filters**:
    - RAG Status: All except NULL values (using `not: ["NULL"]`)
    - Migration Status: Non-migrated categories only (`upd_non_migrated_categories: True`)
- **Columns**:
    - Region
    - Provider Code
    - Provider Name
    - High Level Device Type
    - Device Category
    - RAG Status
    - ZCM Handover Date
    - VCM Handover Date
    - Total Cost (showing the last 12 months of data)
- **Sorting**: By Region, Provider Code, High Level Device Type, RAG Status
- **Sub-totals**: Grouped by Region and Provider Code

### NON-MIGRATED Detailed

- **Type**: Detailed view
- **Purpose**: Provides a [detailed](#types-of-worksheets) view of non-migrated devices, showing total cost per month over the last 12 months.
- **Filters**:
    - RAG Status: All except NULL values (using `not: ["NULL"]`)
    - Migration Status: Non-migrated categories only (`upd_non_migrated_categories: True`)
- **Columns**:
    - Region
    - Provider Code
    - Provider Name
    - High Level Device Type
    - Device Category
    - Manufacturer
    - Manufacturer Device Name
    - RAG Status
- **Sorting**: By Region, Provider Code, High Level Device Type, RAG Status
- **Sub-totals**: Grouped by Region and Provider Code

### Data

- **Type**: Raw data export
- **Purpose**: Contains comprehensive device data with all available fields
- **Filters**: None (all data included)
- **Columns**:
    - Region
    - Provider Code
    - Provider Name
    - High Level Device Type
    - Device Category
    - Manufacturer
    - Manufacturer Device Name
    - Activity Year
    - Activity Month
    - Devices Ident
    - Device Insertion Date
    - Purchase Device Contract
    - Device Serial Number
    - Size
    - Quantity
    - Supplier Unit Price
    - Commissioner Unit Price
    - Total Cost
    - Commissioner Code
    - NHSE Service Line
    - GP Practice Code
    - High Level Device Type
    - Purchase Device Contract
    - VAT Charged
    - Attendance Identifier
- **Sorting**: No specific sorting applied
- **Sub-totals**: None

## Common Features

### Standard Sort Order

Most worksheets (except Data) are sorted by:

1. Region (`upd_region`)
2. Provider Code (`der_provider_code`)
3. High Level Device Type (`upd_high_level_device_type`)
4. RAG Status (`rag_status`)

### Standard Sub-totals

Summary and detailed worksheets include sub-totals grouped by:

- Region (`upd_region`)
- Provider Code (`der_provider_code`)

### Date Formatting

Column with a Datetime name use the default format "%b %Y" (e.g., "Jan 2025") unless otherwise specified.

## Migration Categories

The worksheets distinguish between:

- **Migrated Categories** (`upd_migrated_categories: True`): Device categories that have been migrated to the NHS Supply Chain
- **Non-migrated Categories** (`upd_non_migrated_categories: True`): Device categories that have not yet been migrated
