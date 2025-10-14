# User Guide

Welcome to the Devices RAP User Guide. This section provides comprehensive documentation for both users and developers working with the Devices RAP pipeline.

## Overview

The Devices RAP (Rapid Analytics Platform) is a data processing pipeline designed for NHS England's Direct Commissioning team. It processes device commissioning data for reporting and analysis, supporting both local and remote data processing modes.

## Available Guides

### [User Guide](user.md)

*For end users who want to run the pipeline*

The user guide provides step-by-step instructions for setting up and running the Devices RAP pipeline. It covers:

* System requirements and prerequisites
* Installation instructions for Windows, Linux, and macOS
* Data preparation and file requirements
* Running the pipeline in local and remote modes
* Troubleshooting common issues
* Getting updates from git

**Who should use this:** Data analysts, researchers, and other users who need to run the pipeline to process device commissioning data.

### [Developer Guide](developer.md)

*For developers who want to contribute to or modify the pipeline*

The developer guide provides comprehensive information for developers working on the codebase. It covers:

* Development environment setup
* Project structure and architecture
* Code style guidelines and best practices
* Testing framework and guidelines
* Git workflow and contribution process
* Documentation development
* Release process

**Who should use this:** Software developers, data engineers, and technical contributors who want to modify, extend, or contribute to the pipeline codebase.

## Quick Start

### For Users

1. Read the [User Guide](user.md)
2. Install dependencies using uv or pip
3. Prepare your data files
4. Run the pipeline with `make run-pipeline-local` or `make run-pipeline-remote`

### For Developers

1. Read the [Developer Guide](developer.md)
2. Set up your development environment with `make install-dev`
3. Run tests with `make test`
4. Follow the git workflow for contributions

## Getting Help

If you need assistance:

* Check the troubleshooting sections in the respective guides
* Review the [API Reference](../api_reference/index.md) for technical details
* Contact the data science team for additional support
* Open an issue on GitHub for bugs or feature requests

## Additional Resources

* **[API Reference](../api_reference/index.md)** - Technical documentation for all modules and functions
* **[Data Dictionary](../data_dictionary.md)** - Information about data fields and structures
* **[Process Map](../amber_report_process_map.md)** - Visual overview of the pipeline process
* **[Excel Output Documentation](../worksheet_output_documentation.md)** - Details about the generated reports

---

Choose the appropriate guide based on your role and needs. Both guides are designed to be comprehensive and self-contained, providing all the information you need to work effectively with the Devices RAP pipeline.
