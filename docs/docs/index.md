# NHS England Devices RAP Documentation

Welcome to the **Devices RAP** (Reproducible Analytical Pipeline) documentation. This project is a modern RAP implementation of the NHS England Direct Commissioning Specialised Services Devices Programming (SSDP) reporting pipeline.

## 🎯 Project Overview

The Devices RAP processes and analyzes medical device data across NHS England regions, generating comprehensive reports that track device deployment, migration status, and performance metrics. The pipeline supports commissioning decisions by providing insights into device categories, provider performance, and regional variations.

### Key Features

- **📊 Multi-format Reporting**: Generates Excel workbooks with multiple specialized worksheets
- **🔄 Data Processing Pipeline**: Automated ETL processes for device data cleansing and transformation  
- **📈 RAG Status Analysis**: Red, Amber, Green status tracking for device categories
- **🏥 Regional Analysis**: Provider-level and regional-level reporting capabilities
- **🔍 Migration Tracking**: Monitors device category migration status across the system

## 📋 What This Pipeline Does

The Devices RAP pipeline:

1. **Ingests** raw device data from multiple sources (CSV files, SQL databases)
2. **Cleanses** and normalizes data using standardized taxonomies
3. **Joins** datasets including provider lookups, exceptions, and device taxonomies
4. **Analyzes** device performance using RAG (Red/Amber/Green) status indicators
5. **Generates** comprehensive Excel reports with multiple specialized worksheets:
   - **AMBER Summary/Detailed**: Devices requiring attention
   - **RED Summary/Detailed**: High-priority devices needing immediate action
   - **NON-MIGRATED Summary/Detailed**: Devices not yet migrated to new systems
   - **Data**: Complete raw data export

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Access to NHS England device databases
- Linux-based development environment (recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/nhsengland/devices_rap.git
cd devices_rap

# Set up environment
make create-environment
source .venv/bin/activate
make requirements

# Set up development tools (for contributors)
make pre-commits
```

### Running the Pipeline

```bash
# Run the complete pipeline
make run-pipeline

# Generate documentation
make docs-serve

# Run tests
make test
```

## 📊 Report Outputs

The pipeline generates Excel workbooks containing multiple worksheets tailored for different analytical needs:

| Worksheet Type | Purpose | Focus |
|----------------|---------|-------|
| **AMBER Summary** | High-level overview of amber status devices | Regional summaries |
| **AMBER Detailed** | Detailed amber device information | Device-level analysis |
| **RED Summary** | Critical and yellow status device overview | Priority actions |
| **RED Detailed** | Detailed critical device information | Urgent interventions |
| **NON-MIGRATED Summary** | Non-migrated device categories overview | Migration planning |
| **NON-MIGRATED Detailed** | Detailed non-migrated device data | Migration execution |
| **Data** | Complete dataset export | Raw data analysis |

## 🏗️ Architecture

The pipeline follows RAP (Reproducible Analytical Pipeline) principles with a modular design:

- **`data_in/`**: Data ingestion from CSV and SQL sources
- **`clean_data.py`**: Data cleansing and normalization functions
- **`joins.py`**: Dataset joining and merging operations
- **`create_cuts.py`**: Regional and categorical data segmentation
- **`summary_tables.py`**: Aggregation and summary table generation
- **`data_out.py`**: Excel report generation and formatting
- **`pipeline.py`**: Main orchestration and workflow management

## 📚 Documentation Structure

- **[Usage Guide](usage.md)**: Step-by-step instructions for running the pipeline
- **[API Reference](api_reference/index.md)**: Comprehensive code documentation
- **[Worksheet Documentation](worksheet_output_documentation.md)**: Detailed Excel output specifications

## 🤝 Contributing

This project follows NHS England RAP standards and coding practices:

- **Code Quality**: Pre-commit hooks with linting and security scanning
- **Testing**: Comprehensive unit and end-to-end test coverage
- **Documentation**: Auto-generated API docs from NumPy-style docstrings
- **Version Control**: Git workflows with protected main branch

## 📈 RAP Compliance

[![RAP Status: Work in Progress](https://img.shields.io/badge/RAP_Status-WIP-red)](https://nhsdigital.github.io/rap-community-of-practice/introduction_to_RAP/levels_of_RAP/)

This project implements Reproducible Analytical Pipeline (RAP) principles. Learn more about RAP at the [NHS Digital RAP Community of Practice](https://nhsdigital.github.io/rap-community-of-practice/).

## 📞 Support

- **Project Repository**: [GitHub - nhsengland/devices_rap](https://github.com/nhsengland/devices_rap)
- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Email**: [datascience@nhs.net](mailto:datascience@nhs.net)

---

*This documentation is automatically generated from the codebase using MkDocs and reflects the current state of the Devices RAP pipeline.*

