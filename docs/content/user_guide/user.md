# User Guide: Setting Up and Running the Devices RAP Pipeline

This guide explains how to set up and run the Devices RAP pipeline in both local and remote modes, with instructions for Windows and Linux/macOS users.

## Overview

The pipeline processes device commissioning data for reporting and analysis. You can run it in two modes:

* **Local mode:** Uses local CSV files for all data inputs
* **Remote mode:** Connects to a remote SQL server for master data and uses local files for other inputs

## Prerequisites

### System Requirements

* Python 3.8 or higher
* Git
* [uv](https://docs.astral.sh/uv/) package manager (recommended) or pip

### Data Requirements

#### Local Mode

Place all required CSV files in the `data/` directory:

* `master_data.csv` (extracted manually from SQL server)
* `device_taxonomy.csv` (lookup table)
* `exceptions_report.csv` (emailed monthly)
* Other lookup tables as required by the pipeline

#### Remote Mode

Place the following files in the `data/` directory:

* `device_taxonomy.csv` (lookup table)
* `exceptions_report.csv` (emailed monthly)

Fill in the `.env` file with your SQL server credentials and connection details.

#### How to Obtain Data Files

* **Exception Report:** Emailed to you each month by the reporting team
* **Master Data:** Extract manually from the SQL server using your organization's standard process
* **Lookup Tables:** Provided as CSV files (e.g., `device_taxonomy.csv`)

## Initial Setup

### 1. Clone the Repository

**Windows (Command Prompt/PowerShell):**

```cmd
git clone https://github.com/nhsengland/devices_rap.git
cd devices_rap
```

**Linux/macOS (Terminal):**

```bash
git clone https://github.com/nhsengland/devices_rap.git
cd devices_rap
```

### 2. Install Dependencies

#### Option A: Using uv (Recommended)

First, install uv if you haven't already:

Windows:

```cmd
winget install astral-sh.uv
```

Linux/macOS:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then install dependencies:

```bash
uv sync
```

#### Option B: Using pip (Fallback)

```bash
pip install -e .
```

#### Option C: Using Make (Linux/macOS only)

```bash
make install
```

### 3. Prepare Data Files

Place the required data files in the `data/` directory as described in the prerequisites section.

### 4. Configure Environment (Remote Mode Only)

Copy the example environment file and fill in your details:

**Windows:**

```cmd
copy example.env .env
```

**Linux/macOS:**

```bash
cp example.env .env
```

Edit the `.env` file with your SQL server credentials and connection details.

## Running the Pipeline

### Using uv (Recommended)

**Local Mode:**

```bash
uv run python -m devices_rap.pipeline --mode local
```

**Remote Mode:**

```bash
uv run python -m devices_rap.pipeline --mode remote
```

### Using Make (Linux/macOS)

**Local Mode:**

```bash
make run_pipeline_local
```

**Remote Mode:**

```bash
make run_pipeline_remote
```

### Using Python Directly (Fallback)

**Local Mode:**

```bash
python -m devices_rap.pipeline --mode local
```

**Remote Mode:**

```bash
python -m devices_rap.pipeline --mode remote
```

## Getting Updates

To get the latest updates from the repository:

### 1. Check Current Status

```bash
git status
```

### 2. Pull Latest Changes

```bash
git pull origin main
```

### 3. Update Dependencies

**Using uv:**

```bash
uv sync
```

**Using pip:**

```bash
pip install -e . --upgrade
```

### 4. Check for Breaking Changes

Always review the commit messages or release notes for any breaking changes that might affect your setup.

## Troubleshooting

### Common Issues

* **Missing files:** Ensure all required files are present in the `data/` directory
* **Connection errors (Remote mode):** Verify your `.env` file is correctly filled and you have access to the SQL server
* **Permission errors:** Make sure you have write permissions to the output directory
* **Python version:** Ensure you're using Python 3.8 or higher

### Getting Help

* Check the logs for detailed error messages
* Refer to the [API Reference](../api_reference/index.md) for module-specific guidance
* Contact the data science team for additional support

### Useful Commands

**Check Python version:**

```bash
python --version
```

**Check uv version:**

```bash
uv --version
```

**View pipeline help:**

```bash
uv run python -m devices_rap.pipeline --help
```
