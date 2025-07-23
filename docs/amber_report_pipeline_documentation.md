# Amber Report Pipeline Documentation

This document provides a comprehensive overview of the Amber Report Pipeline, explaining its purpose, architecture, data flow, and end-to-end functionality.

## Overview

The Amber Report Pipeline is a **Reproducible Analytical Pipeline (RAP)** designed to automate the creation of monthly device reports for all NHS England regions. It processes device commissioning data to generate Excel reports with multiple worksheets showing different views of device status based on RAG (Red, Amber, Green) ratings and migration categories.

### What is RAP?

RAP (Reproducible Analytical Pipelines) is a set of tools, principles, and techniques to improve analytical processes. This pipeline follows RAP principles by being:

- **Reproducible**: Consistent outputs from the same inputs
- **Auditable**: Clear data lineage and processing steps
- **Efficient**: Automated processing reducing manual effort
- **Quality-assured**: Built-in data validation and testing

## Pipeline Purpose

The pipeline serves the **Specialised Services Devices Programming (SSDP)** reporting requirements by:

1. **Processing raw device data** from multiple sources
2. **Applying business rules** for data cleansing and validation
3. **Creating summary and detailed views** of device information
4. **Generating regional reports** tailored to specific NHS England regions
5. **Producing Excel outputs** with consistent formatting and structure

## Architecture Overview

### Input Sources

The pipeline processes four main data sources:

1. **Master Devices Data** (`master_devices.csv`)
   - Core device transaction data
   - Contains device details, costs, dates, and identifiers

2. **Provider Codes Lookup** (`provider_codes_lookup.csv`)
   - Maps provider codes to provider names and regions
   - Provides organizational context

3. **Device Taxonomy** (`device_taxonomy.csv`)
   - Device categorization and classification
   - Defines high-level and subsidiary device types

4. **Exceptions Data** (`exceptions.csv`)
   - Special cases and business rule exceptions
   - RAG status overrides and exception notes

### Core Components

The pipeline is structured into several key functional modules:

#### 1. Configuration Management (`config.py`)

- Manages pipeline parameters (financial month/year, output formats)
- Defines file paths and dataset locations
- Handles logging configuration
- Validates required directories and files

#### 2. Data Loading (`data_in/load_csv.py`)

- Loads CSV files into pandas DataFrames
- Handles custom NA values and data type conversions
- Provides error handling for missing files

#### 3. Data Cleaning (`clean_data.py`)

- **Column Normalization**: Standardizes column names across datasets
- **Master Data Cleansing**: Converts data types, handles dates, calculates costs
- **Taxonomy Cleansing**: Processes device categorization data
- **Exception Cleansing**: Handles exception data and RAG status priorities

#### 4. Data Joining (`joins.py`)

- **Provider Lookup Join**: Links devices to providers and regions
- **Taxonomy Join**: Adds device categorization information
- **Exception Join**: Applies business rule exceptions and RAG overrides
- **Mini Table Joins**: Creates summary-level joins for reporting

#### 5. Summary Table Creation (`summary_tables.py`)

- **Device Category Summary**: Groups by device categories with cost totals
- **Device Detail Summary**: Device-level summaries with manufacturer details
- **Pivot Table Generation**: Creates time-series views with monthly breakdowns
- **Change Calculations**: Computes month-over-month changes

#### 6. Regional Cuts (`create_cuts.py`)

- Splits national data into regional datasets
- Creates separate tables for each NHS England region
- Maintains data integrity across regional boundaries

#### 7. Output Processing (`interpret_output_instructions.py`)

- **Worksheet Configuration**: Applies filtering rules from YAML config
- **Column Ordering**: Arranges columns per specification
- **Data Filtering**: Applies RAG status and migration filters
- **Sub-total Generation**: Creates regional and provider sub-totals
- **Date Formatting**: Standardizes datetime column presentations

#### 8. Data Output (`data_out.py`)

- **Excel Generation**: Creates formatted Excel workbooks
- **Multi-format Support**: Supports Excel, CSV, Pickle, and Zip outputs
- **File Management**: Organizes outputs by region, month, and year

## End-to-End Data Flow

### Phase 1: Initialization and Setup

```text
Input Parameters → Configuration Setup → Path Validation → Logging Setup
```

**Key Actions:**

- Load pipeline configuration with financial month/year
- Validate required directories exist
- Initialize logging system
- Set up output format specifications

### Phase 2: Data Ingestion

```text
Raw CSV Files → Data Loading → Initial Validation → DataFrame Creation
```

**Processing Steps:**

1. **Load Master Devices**: Primary transaction data with device costs and details
2. **Load Provider Lookup**: Organizational mapping for regions and provider names
3. **Load Device Taxonomy**: Device categorization and type definitions
4. **Load Exceptions**: Business rule overrides and special cases

**Data Quality Checks:**

- File existence validation
- Column presence verification
- Data type consistency
- Missing value handling

### Phase 3: Data Cleansing and Standardization

```text
Raw DataFrames → Column Normalization → Data Type Conversion → Business Rules Application
```

**Master Data Cleansing:**

- Normalize column names to standard format
- Convert financial dates to proper datetime objects
- Calculate total costs and validate financial data
- Apply data type conversions (numeric, categorical, dates)
- Handle missing values with appropriate defaults

**Lookup Data Cleansing:**

- Standardize provider codes and names
- Validate region mappings
- Clean device taxonomy hierarchies
- Process exception rules and RAG priorities

### Phase 4: Data Integration

```text
Cleansed DataFrames → Sequential Joins → Master Dataset Creation → Relationship Validation
```

**Join Sequence:**

1. **Master + Provider Lookup**: Add regional and organizational context
2. **+ Device Taxonomy**: Incorporate device categorization
3. **+ Exceptions**: Apply business rule overrides and RAG status assignments

**Data Enrichment:**

- Add calculated fields (derived region, high-level device types)
- Apply RAG status logic with priority handling
- Generate exception notes where applicable
- Validate referential integrity across joins

### Phase 5: Business Logic Application

```text
Joined Dataset → RAG Status Assignment → Migration Categorization → Data Validation
```

**RAG Status Logic:**

- **RED**: Critical issues requiring immediate attention
- **AMBER**: Items needing monitoring or review
- **YELLOW**: Warning conditions (reported with RED)
- **GREEN**: Satisfactory status
- **NULL**: No status assigned

**Migration Categories:**

- **Migrated**: Device categories moved to new system
- **Non-migrated**: Categories pending migration

### Phase 6: Summary Table Generation

```text
Master Dataset → Aggregation → Pivot Tables → Summary Views
```

**Summary Table Types:**

1. **Device Category Summary**:
   - Grouped by region, provider, device category
   - Monthly cost totals with time-series breakdown
   - RAG status summaries
   - Exception notes inclusion

2. **Device Detail Summary**:
   - Individual device records
   - Manufacturer and model details
   - Regional and provider context
   - No exception notes (detailed view)

**Aggregation Rules:**

- Sum total costs by grouping categories
- Preserve most recent RAG status
- Maintain audit trail through identifiers

### Phase 7: Regional Data Segmentation

```text
National Summaries → Regional Filtering → Region-Specific Datasets
```

**Regional Cuts:**

- Split data by NHS England regions
- Maintain consistency across summary and detailed views
- Preserve all data relationships within regional boundaries
- Create region-specific master datasets for comprehensive views

### Phase 8: Report Configuration and Filtering

```text
Regional Data → Worksheet Configuration → Filtering → Column Selection
```

**Worksheet Processing (per region):**

1. **AMBER Summary & Detailed**: Focus on AMBER status, migrated categories
2. **RED Summary & Detailed**: Focus on RED/YELLOW status, migrated categories  
3. **NON-MIGRATED Summary & Detailed**: Focus on non-migrated categories
4. **Data Sheet**: Complete raw data export

**Applied Filters:**

- RAG status filtering per worksheet type
- Migration category filtering (migrated vs non-migrated)
- Column selection based on worksheet purpose
- Sorting by region, provider, device type, RAG status

### Phase 9: Excel Output Generation

```text
Configured Worksheets → Excel Formatting → Multi-Sheet Workbooks → File Organization
```

**Output Features:**

- Multiple worksheets per region
- Consistent formatting and styling
- Sub-totals by region and provider
- Datetime columns with standard formatting
- Regional file naming conventions

**File Organization:**

```text
processed_data/
├── YYYY/
│   ├── MM/
│   │   ├── Region_1_YYYY_MM_RAG_STATUS_REPORT.xlsx
│   │   ├── Region_2_YYYY_MM_RAG_STATUS_REPORT.xlsx
│   │   └── ...
│   └── YYYY_MM_amber_report_all_regions.pkl (optional)
```

### Phase 10: Quality Assurance and Completion

```text
Generated Reports → Data Validation → Output Verification → Success Logging
```

**Final Validation:**

- Verify all expected regions have reports
- Validate worksheet completeness
- Check file integrity
- Confirm data consistency across worksheets

## Key Features and Capabilities

### Data Processing Features

1. **Robust Data Handling**:
   - Custom NA value processing
   - Automatic data type inference and conversion
   - Missing value imputation with business logic
   - Duplicate data detection and handling

2. **Advanced Joining Logic**:
   - Left joins preserving all master data
   - Validation of join keys
   - Error handling for unmatched records
   - Relationship integrity checking

3. **Time Series Processing**:
   - Financial year/month handling
   - Date parsing and standardization
   - Monthly aggregation and pivoting
   - Month-over-month change calculations

### Business Rule Implementation

1. **RAG Status Prioritization**:
   - Hierarchical status assignment
   - Exception-based overrides
   - Priority-based conflict resolution

2. **Migration Category Logic**:
   - Device category classification
   - Migration status tracking
   - Historical categorization

3. **Exception Handling**:
   - Business rule overrides
   - Custom status assignments
   - Exception note generation

### Output Flexibility

1. **Multiple Format Support**:
   - Excel workbooks with multiple sheets
   - CSV exports for data analysis
   - Pickle files for Python processing
   - Zip archives for distribution

2. **Configurable Worksheets**:
   - YAML-driven configuration
   - Flexible column selection
   - Dynamic filtering rules
   - Custom sorting and grouping

3. **Regional Customization**:
   - Region-specific reports
   - Tailored data views
   - Consistent cross-regional structure

## Performance and Scalability

### Optimization Features

1. **Efficient Data Processing**:
   - Pandas vectorized operations
   - Optimized join algorithms
   - Memory-efficient data handling

2. **Optional Multiprocessing**:
   - Parallel Excel generation
   - Concurrent regional processing
   - Scalable output creation

3. **Caching and Checkpointing**:
   - Intermediate data saving
   - Process restart capability
   - Historical data preservation

### Error Handling and Resilience

1. **Comprehensive Error Management**:
   - Custom exception classes
   - Detailed error logging
   - Graceful failure handling

2. **Data Validation**:
   - Input data quality checks
   - Process validation at each stage
   - Output integrity verification

3. **Audit Trail**:
   - Complete processing logs
   - Data lineage tracking
   - Change history maintenance

## Testing and Quality Assurance

### Testing Framework

1. **Unit Tests**:
   - Function-level testing
   - Edge case validation
   - Data transformation verification

2. **End-to-End Tests**:
   - Full pipeline testing
   - Historical data backtesting
   - Output validation

3. **Integration Tests**:
   - Component interaction testing
   - Data flow validation
   - Configuration testing

### Quality Measures

1. **Data Quality**:
   - Completeness validation
   - Consistency checking
   - Accuracy verification

2. **Process Quality**:
   - Reproducibility testing
   - Performance monitoring
   - Error rate tracking

## Usage and Deployment

### Running the Pipeline

```python
from devices_rap.pipeline import amber_report_pipeline

# Basic usage
amber_report_pipeline(
    fin_month="12",
    fin_year="2425",
    outputs=["excel"]
)

# Advanced usage with custom configuration
amber_report_pipeline(
    fin_month="12",
    fin_year="2425",
    outputs=["excel", "pickle"],
    use_multiprocessing=True,
    raw_data_dir="/custom/path/to/data"
)
```

### Configuration Options

- **Financial Period**: Month and year specification
- **Output Formats**: Excel, CSV, Pickle, Zip
- **Processing Options**: Multiprocessing, custom paths
- **Data Sources**: Configurable input directories

### Deployment Considerations

1. **Environment Requirements**:
   - Python 3.12+
   - Required dependencies (pandas, openpyxl, etc.)
   - Sufficient memory for data processing

2. **File System Access**:
   - Read access to source data directories
   - Write access to output directories
   - Temporary storage for processing

3. **Performance Tuning**:
   - Memory allocation for large datasets
   - Multiprocessing configuration
   - I/O optimization for file operations

## Maintenance and Extension

### Regular Maintenance Tasks

1. **Data Source Updates**:
   - Monitor input data quality
   - Update taxonomy classifications
   - Maintain provider lookup accuracy

2. **Configuration Management**:
   - Review and update YAML configurations
   - Validate worksheet specifications
   - Update business rules as needed

3. **Performance Monitoring**:
   - Track processing times
   - Monitor memory usage
   - Analyze error patterns

### Extension Opportunities

1. **Additional Output Formats**:
   - Database loading capabilities
   - API integration for automated distribution
   - Dashboard integration

2. **Enhanced Analytics**:
   - Trend analysis capabilities
   - Predictive modeling integration
   - Advanced statistical reporting

3. **Automation Enhancements**:
   - Scheduled execution
   - Email notification systems
   - Automated data quality monitoring

## Conclusion

The Amber Report Pipeline represents a comprehensive, automated solution for processing NHS device commissioning data. By implementing RAP principles, it provides:

- **Reliability**: Consistent, reproducible results
- **Efficiency**: Automated processing reducing manual effort
- **Scalability**: Capable of handling growing data volumes
- **Maintainability**: Clear structure enabling ongoing development
- **Quality**: Built-in validation and testing ensuring data integrity

The pipeline successfully transforms complex, multi-source device data into actionable regional reports, supporting NHS England's device commissioning oversight and decision-making processes.
