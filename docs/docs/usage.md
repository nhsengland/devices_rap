# Usage Guide

This guide provides step-by-step instructions for setting up and running the Devices RAP pipeline.

## 🛠️ Installation and Setup

### Prerequisites

Before you begin, ensure you have:

- **Python 3.12** or later installed
- **Git** for version control
- Access to **NHS England device databases**
- A **Linux-based development environment** (WSL, GitHub Codespaces, or native Linux)

### 1. Clone the Repository

```bash
git clone https://github.com/nhsengland/devices_rap.git
cd devices_rap
```

### 2. Environment Setup

Choose one of the following methods:

#### Option A: Using Make (Recommended)

```bash
# Create virtual environment and install dependencies
make create-environment
source .venv/bin/activate
make requirements
```

#### Option B: Using pip directly

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

**Linux/macOS:**

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### 3. Configure Your IDE (Visual Studio Code)

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Search for "Python: Select Interpreter"
3. Select the `.venv` virtual environment you just created

### 4. Set Up Pre-commit Hooks (For Contributors)

```bash
make pre-commits
```

This enables:

- **Gitleaks**: Prevents committing secrets and credentials
- **Linting**: Ensures code follows PEP8 standards using Flake8 and Black

## 🚀 Running the Pipeline

### Quick Start

Run the complete pipeline with default settings:

```bash
make run-pipeline
```

This will:

1. Load and process raw device data
2. Apply data cleansing and normalization
3. Generate Excel reports with multiple worksheets
4. Save outputs to the configured directory

### Available Make Commands

Use `make help` to see all available commands:

```bash
make help
```

Key commands include:

| Command | Description |
|---------|-------------|
| `make run-pipeline` | Execute the complete data processing pipeline |
| `make test` | Run the full test suite |
| `make lint` | Check code quality and formatting |
| `make docs-serve` | Start local documentation server |
| `make docs-build` | Build static documentation |
| `make clean` | Clean up temporary files and caches |

## 📊 Understanding the Output

### Excel Report Structure

The pipeline generates Excel workbooks containing multiple specialized worksheets:

#### Summary Worksheets
- **AMBER Summary**: High-level view of devices requiring attention
- **RED Summary**: Critical devices needing immediate action  
- **NON-MIGRATED Summary**: Devices not yet migrated to new systems

#### Detailed Worksheets
- **AMBER Detailed**: Comprehensive amber device information
- **RED Detailed**: Detailed critical device data
- **NON-MIGRATED Detailed**: Complete non-migrated device records

#### Raw Data
- **Data**: Complete dataset export for further analysis

### Output Locations

By default, outputs are saved to:
- **Reports**: `data/processed/YYYY/MM/` directory
- **Logs**: `logs/` directory  
- **Temporary files**: `data/interim/` directory

## ⚙️ Configuration

### Environment Variables

Set up your environment variables for database connections and file paths:

```bash
# Copy the example configuration
cp .env.example .env

# Edit with your specific settings
vim .env
```

### Pipeline Configuration

The pipeline behavior can be customized through:

- **`devices_rap/config.py`**: Main configuration settings
- **`amber_report_excel_config.yaml`**: Excel output formatting rules
- **Environment variables**: Database connections and file paths

### Data Sources

The pipeline expects data in the following locations:

- **Raw CSV files**: `data/raw/YYYY/MM/` directories
- **Lookup tables**: `data/raw/provider_codes_lookup.csv`
- **SQL databases**: Configured via environment variables

## 🧪 Testing

### Run All Tests

```bash
make test
```

### Test Categories

- **Unit Tests**: Test individual functions and modules
- **End-to-End Tests**: Test complete pipeline execution
- **Data Validation**: Verify output data quality and format

### Test Configuration

Tests are configured in:
- **`pytest.ini`**: Pytest configuration
- **`tests/`**: Test modules organized by functionality
- **`conftest.py`**: Shared test fixtures and setup

## 🔧 Troubleshooting

### Common Issues

#### Import Errors
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### Database Connection Issues
- Verify environment variables are set correctly
- Check VPN connection to NHS networks
- Confirm database credentials and permissions

#### Memory Issues with Large Datasets
- Monitor system memory usage during processing
- Consider processing data in smaller batches
- Increase available system memory if possible

### Getting Help

1. **Check the logs**: Review files in the `logs/` directory
2. **Run with verbose output**: Use `-v` flag for detailed information
3. **Consult the API docs**: Check function-specific documentation
4. **Create an issue**: Use GitHub Issues for bug reports

## 🚀 Advanced Usage

### Custom Pipeline Execution

For advanced users wanting to run specific pipeline components:

```python
from devices_rap.pipeline import run_pipeline
from devices_rap.config import Config

# Load configuration
config = Config()

# Run specific pipeline steps
run_pipeline(
    config=config,
    steps=['load_data', 'clean_data', 'generate_reports']
)
```

### Batch Processing

Process multiple months of data:

```bash
# Process specific financial year and month
python -m devices_rap.pipeline --year 2425 --month 12

# Process range of months
for month in {01..12}; do
    python -m devices_rap.pipeline --year 2425 --month $month
done
```

## 📈 Monitoring and Logging

The pipeline provides comprehensive logging:

- **INFO level**: General pipeline progress
- **DEBUG level**: Detailed processing information  
- **ERROR level**: Issues requiring attention
- **Performance metrics**: Timing and resource usage

Logs are automatically rotated and archived for analysis.

---

For more detailed information about specific functions and modules, see the [API Reference](api_reference/index.md).
