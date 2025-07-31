# Amber Report Excel Output Documentation

This document describes the structure and content of each worksheet in the Amber Report Excel output file.

## Overview

The Excel output contains multiple worksheets, each configured with specific columns, filters, and sorting criteria. The worksheets are designed to provide different views of the device data based on RAG (Red, Amber, Green) status and migration categories.

## Worksheet Descriptions

### AMBER Summary

- **Type**: Summary view
- **Purpose**: Provides a high-level summary of devices with AMBER status
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
    - Exception Notes
    - Change from Previous Month
- **Sorting**: By Region, Provider Code, High Level Device Type, RAG Status
- **Sub-totals**: Grouped by Region and Provider Code

### AMBER Detailed

- **Type**: Detailed view
- **Purpose**: Provides detailed device information for AMBER status items
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
- **Sorting**: By Region, Provider Code, High Level Device Type, RAG Status
- **Sub-totals**: Grouped by Region and Provider Code

### RED Summary

- **Type**: Summary view
- **Purpose**: Provides a high-level summary of devices with RED or YELLOW status
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
- **Sorting**: By Region, Provider Code, High Level Device Type, RAG Status
- **Sub-totals**: Grouped by Region and Provider Code

### RED Detailed

- **Type**: Detailed view
- **Purpose**: Provides detailed device information for RED and YELLOW status items
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
- **Sorting**: By Region, Provider Code, High Level Device Type, RAG Status
- **Sub-totals**: Grouped by Region and Provider Code

### NON-MIGRATED Summary

- **Type**: Summary view
- **Purpose**: Provides a high-level summary of non-migrated device categories
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
- **Sorting**: By Region, Provider Code, High Level Device Type, RAG Status
- **Sub-totals**: Grouped by Region and Provider Code

### NON-MIGRATED Detailed

- **Type**: Detailed view
- **Purpose**: Provides detailed device information for non-migrated categories
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
- **Columns**: All available data columns including:
    - Basic information (Region, Provider Code, Provider Name, Device Category)
    - Device details (Manufacturer, Device Name, Serial Number, Size, Quantity)
    - Financial data (Unit Prices, Total Cost, VAT information)
    - Temporal data (Activity Year/Month, Device Insertion Date)
    - Administrative data (Commissioner Code, Service Categories, GP Practice Code)
    - Technical identifiers (Devices Ident, Attendance Identifier)
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

Datetime columns use the default format "%b %Y" (e.g., "Jan 2025") unless otherwise specified.

## Migration Categories

The worksheets distinguish between:

- **Migrated Categories** (`upd_migrated_categories: True`): Device categories that have been migrated to the new system
- **Non-migrated Categories** (`upd_non_migrated_categories: True`): Device categories that have not yet been migrated
