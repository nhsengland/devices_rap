# RAP Devices

[![CCDS: Project Template](https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter)](https://cookiecutter-data-science.drivendata.org/ "cookiecutter-data-science")
[![RAP Status: Work in Progress](https://img.shields.io/badge/RAP_Status-WIP-red)](https://nhsdigital.github.io/rap-community-of-practice/introduction_to_RAP/levels_of_RAP/ "WIP RAP")
[![licence: MIT](https://img.shields.io/badge/Licence-MIT-yellow.svg)](https://opensource.org/licenses/MIT "MIT License")
[![licence: OGL3](https://img.shields.io/badge/Licence-OGL3-darkgrey "licence: Open Government Licence 3")](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)
[![JIRA EPIC: DC-477](https://img.shields.io/badge/JIRA-DC--477-purple?link=https%3A%2F%2Fnhsd-jira.digital.nhs.uk%2Fbrowse%2FDC-477)](https://nhsd-jira.digital.nhs.uk/browse/DC-477 "DC-477")
[![Tests and Linting](https://github.com/nhsengland/devices_rap/actions/workflows/python-package.yml/badge.svg?branch=main)](https://github.com/nhsengland/devices_rap/actions/workflows/python-package.yml)

This is the RAP rework of the Specialised Services Devices Programming (SSDP) reporting pipeline.

## What is RAP?

Reproducible Analytical Pipelines is a set of tools, principles, and techniques to help you improve your analytical processes.
Learn more about RAP on the [RAP Community of Practice Website](https://nhsdigital.github.io/rap-community-of-practice/)

## Prerequisites

To use this repository you will need:

* Python 3.10+ (Python 3.13+ recommended)
* [uv](https://docs.astral.sh/uv/) - A fast Python package manager (recommended)
    * Install: `pip install uv` or see [installation guide](https://docs.astral.sh/uv/getting-started/installation/)
<!-- TODO Add additional requirements regarding access to the SQL Databases and any config env files -->

It is recommended you have access to:

* A Linux based development environment: e.g. [WSL](https://learn.microsoft.com/en-us/windows/wsl/), [GitHub Codespaces](https://github.com/features/codespaces), etc.

## Getting Started

### 1 Clone the repository

To learn about what this means, and how to use Git, see the [Git guide](https://nhsdigital.github.io/rap-community-of-practice/training_resources/git/using-git-collaboratively/).

``` bash
git clone https://github.com/nhsengland/devices_rap.git
```

### 2 Set up your environment

We recommend using [uv](https://docs.astral.sh/uv/) for fast dependency management. All dependencies are now managed in `pyproject.toml`.

#### Using uv (Recommended)

```bash
# Install all dependencies (production only)
uv sync

# Install with development tools (for contributors)
uv sync --dev
```

#### Alternative: Using pip

If you prefer pip, you can still use it with the `pyproject.toml`:

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

**Linux/macOS:**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

For development with testing tools:

```bash
pip install -e ".[dev]"
```

#### Legacy: Using make

The `Makefile` is still available for backwards compatibility:

```bash
make create-environment
source .venv/bin/activate
make requirements
```

> **Note:** For Visual Studio Code, ensure you select the correct Python interpreter from your virtual environment (.venv). Use Ctrl-Shift-P, search for "Python: Select Interpreter" and choose the .venv option.

### 3 Set up Pre-commits (Only needed for developers not users of the pipeline)

Pre-commits allow us to automatically check our code before we commit changes. This can be important for ensuring security and quality in our code. Currently two hooks run:

* [Gitleaks](https://github.com/gitleaks/gitleaks "Gitleaks") - a SAST tool for detecting and preventing hardcoded secrets like passwords, API keys, and tokens in git repos.
* Linting checks - runs the `make lint` command, which uses Flake8 and Black to ensure that the repository is maintaining expected coding standards, such as [PEP8](https://peps.python.org/pep-0008/).

To set up the pre-commits run the following commands:

#### Using uv for pre-commits (Recommended)

```bash
uv run pre-commit autoupdate
uv run pre-commit install
uv run pre-commit run --all-files
```

#### Using make for pre-commits

```bash
make pre-commits
```

#### Manual pre-commit setup

```bash
pre-commit autoupdate
pre-commit install
pre-commit run --all-files
```

#### Platform-specific Git-Secrets Configuration

The project includes NHS git-secrets scanning with separate configurations for different platforms.

**Linux/macOS (Default):** The main `.pre-commit-config.yaml` uses bash implementation

* No additional setup required for Linux/macOS
* Works with standard Unix environments

**Windows:** Use the Windows-optimized configuration

```bash
# Use the Windows configuration directly
uv run pre-commit install --config .pre-commit-config-windows.yaml
uv run pre-commit run --config .pre-commit-config-windows.yaml --all-files

# Or for manual setup
pre-commit install --config .pre-commit-config-windows.yaml
pre-commit run --config .pre-commit-config-windows.yaml --all-files
```

Both implementations respect the same `.gitallowed` exclusion patterns.

> **Note:** The repository defaults to Linux/macOS configuration. Windows users should copy the Windows-specific config before running pre-commit setup.

## Notes for Migration

This project has been migrated from using `requirements.txt` to `pyproject.toml` + `uv.lock` for modern Python dependency management. The old `requirements.txt` file is still present for compatibility but can be removed once you're confident the new setup works for your use case.

To remove the legacy file:

```bash
rm requirements.txt  # On Unix/macOS/WSL
# or
del requirements.txt  # On Windows
```

## Running the code

Now the pipeline is set up and ready to run. Choose your preferred method:

### With uv

```bash
uv run python devices_rap/pipeline.py
```

### Using make

If using a shell with `make` installed:

```bash
make run_pipeline
```

### Direct Python execution

```bash
python devices_rap/pipeline.py
```

### Testing the code

When developing the code (or before you run the code), it is important to test the code to ensure it is working as expected. Regularly run the relevant commands.

#### With uv (Recommended)

```bash
# Run all tests
uv run pytest

# Run only unit tests
uv run pytest tests/unittests 

# Run only end-to-end tests
uv run pytest tests/e2e_tests
```

#### With make

If using a shell with `make` installed:

```bash
make test

# To only run unittests
make unittest

# To only run end-to-end tests
make e2e
```

#### Direct pytest execution

```bash
pytest

# To only run unittests
pytest tests/unittests 

# To only run end-to-end tests
pytest tests/e2e_tests
```

## Data Wrangler Compatibility

This project is fully compatible with [VS Code Data Wrangler](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.datawrangler) for interactive data exploration and analysis. All required dependencies (pandas, numpy, matplotlib, seaborn, jupyter, ipykernel) are included.

To use Data Wrangler:

1. Ensure you have the environment set up with `uv sync --dev`
2. Install the Data Wrangler extension in VS Code
3. Open any Python file or Jupyter notebook and start exploring your data interactively

## Project Organisation

```text
DEVICES_RAP
├── LICENSE
├── Makefile
├── README.md
├── docs
│   ├── README.md
│   ├── docs
│   │   ├── getting-started.md
│   │   └── index.md
│   └── mkdocs.yml
├── models
├── notebooks
├── pyproject.toml
├── devices_rap
│   ├── __init__.py
│   ├── config.py
│   ├── data_in.py
│   ├── data_out.py
│   ├── pipeline.py
│   ├── utils
│   └── utils.py
├── references
├── reports
│   └── figures
├── pyproject.toml
├── uv.lock
├── setup.cfg
└── tests
    ├── e2e_tests
    │   └── test_e2e_placeholder.py
    └── unittests
        ├── test_data_in.py
        ├── test_data_out.py
        ├── test_pipeline.py
        └── test_utils.py
```

> ### Update the project diagram
>
> To update the project diagram, run the following commands:
>
> ```bash
> make clean 
> tree
> ```
>
> Copy and paste the resulting tree over the old tree above.

### Root directory - `DEVICES_RAP`

This is the highest level of the repository containing the general files of project, such as:

* LICENCE - This tells others what they can and can't do with the project code.
* Makefile - Defines a series of convenient commands like `make create_environment` and `make run_pipeline`
* README.md - Top level information about this project for users and developers.
* pyproject.toml - Project configuration file with package metadata, dependencies, and tool configuration (replaces requirements.txt)
* uv.lock - Lock file with exact dependency versions for reproducible installations
* setup.cfg - configuration file for flake8, a linting tool (makes sure the code is layed out cleanly)

The root directory also contains empty folders ready for future use:

* docs - project documentation written in markdown
* notebooks - exploratory notebooks (blend of code, text, and graphs). Do not use to store source code.
* references - data dictionaries, manuals, and all other explanatory materials.
* reports - Generated analysis as HTML, PDF, LaTeX, etc. Contains a figures directory for graphics and figures to be used in reporting.

### Data folder - `data`

This folder contains saved checkpoints of data at various points in the pipeline. While we would want to process the data in one fell swoop, it makes sense to save the data. This can help cache the data for other parts of the pipeline to use, or for use to look at later and QA/debug. We will also save historical data in this folder to all us to perform backtesting (ensuring the pipeline replicates the manual process we are trying to recreate).

The sub folders in the data folder include:

* external - Data from third party sources.
* interim - Intermediate data that has been transformed.
* processed - The final, canonical data sets ready for output or modelling.
* raw - The original, immutable data dump.

### Source code - `devices_rap`

This contains the source code for use in this project. This is where the code to do everything important should sit.

* `__init__.py` - Makes devices_rap a Python module
* config.py - Stores useful variable and configuration settings (Note: should not contain sensitive or secret information, this should be stored in an .env file)
* pipeline.py - This is the main file containing function to run parts of pipeline (e.g. if only wanting to run one report) or all of the pipeline.

There are other files in here, however, these should include information about what they contain at the top of the file as a module docstring.

### Testing framework - `tests`

This repository uses `pytest` for testing the pipeline. The tests for a RAP Pipeline can be divided into two types, end-to-end tests and unit tests.

#### End-to-End Tests - `e2e_tests`

End-to-End tests, also know as integration tests or backtests, tests large portions of the pipeline at once. This to ensure discrete parts of the pipeline can work together and that the pipeline will work under "real-world" conditions. We might cut out/mock connections to external resources (e.g. SQL Servers or distributing reports via email)

Part of the end-to-end tests will include backtests where we use historial inputs and outputs to ensure the pipeline correctly replicates the historical process.

#### Unit Tests - `unittest`

Unit tests, test discrete parts of the pipeline, usually a function at a time. Each function will have multiple tests, testing the expected and unexpected cases the function will encounter.

--------

## Licence

Unless stated otherwise, the codebase is released under the [MIT Licence](./LICENSE). This covers both the codebase and any sample code in the documentation.

HTML and Markdown documentation is © Crown copyright and available under the terms of the [Open Government 3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/) licence.

<!-- [![RAP Status: Baseline](https://img.shields.io/badge/RAP_Status-Baseline-green)](https://nhsdigital.github.io/rap-community-of-practice/introduction_to_RAP/levels_of_RAP/#baseline-rap---getting-the-fundamentals-right "Baseline RAP") -->

<!-- [![RAP Status: Silver](https://img.shields.io/badge/RAP_Status-Silver-silver)](https://nhsdigital.github.io/rap-community-of-practice/introduction_to_RAP/levels_of_RAP/#silver-rap---implementing-best-practice "Silver RAP") -->

<!-- [![RAP Status: Gold](https://img.shields.io/badge/RAP_Status-Gold-gold)](https://nhsdigital.github.io/rap-community-of-practice/introduction_to_RAP/levels_of_RAP/#gold-rap---analysis-as-a-product, "Gold RAP") -->
