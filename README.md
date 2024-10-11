# RAP Devices

[![CCDS: Project Template](https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter)](https://cookiecutter-data-science.drivendata.org/ "cookiecutter-data-science")
[![RAP Status: Work in Progress](https://img.shields.io/badge/RAP_Status-WIP-red)](https://nhsdigital.github.io/rap-community-of-practice/introduction_to_RAP/levels_of_RAP/ "WIP RAP")
[![licence: MIT](https://img.shields.io/badge/Licence-MIT-yellow.svg)](https://opensource.org/licenses/MIT "MIT License")
[![licence: OGL3](https://img.shields.io/badge/Licence-OGL3-darkgrey "licence: Open Government Licence 3")](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)
[![JIRA EPIC: DC-477](https://img.shields.io/badge/JIRA-DC--477-purple?link=https%3A%2F%2Fnhsd-jira.digital.nhs.uk%2Fbrowse%2FDC-477)](https://nhsd-jira.digital.nhs.uk/browse/DC-477 "DC-477")

This is the RAP rework of the Specialised Services Devices Programming (SSDP) reporting pipeline. 

## What is RAP?

Reproducible Analytical Pipelines is a set of tools, principles, and techniques to help you improve your analytical processes.
Learn more about RAP on the [RAP Community of Practice Website](https://nhsdigital.github.io/rap-community-of-practice/)

## Prerequisites

To use this repository you will need access to:

* Python 3.12
<!-- TODO Add additional requirements regarding access to the SQL Databases and any config env files -->

It is recommended you have access to:

* A Linux based development environment: e.g. [WSL](https://learn.microsoft.com/en-us/windows/wsl/), [GitHub Codespaces](https://github.com/features/codespaces), etc.

## Getting Started

1. Clone the repository. To learn about what this means, and how to use Git, see the [Git guide](https://nhsdigital.github.io/rap-community-of-practice/training_resources/git/using-git-collaboratively/).

``` bash
git clone https://github.com/nhsengland/devices_rap.git
```

2. Set up your environment, _either_ using [pip](https://pypi.org/project/pip/) or make (if you are using a linux based development environment this will be already installed). For more information on how to use virtual environments and why they are important,. see the [virtual environments guide](https://nhsdigital.github.io/rap-community-of-practice/training_resources/python/virtual-environments/why-use-virtual-environments/).

### Using pip

If using Windows Powershell:

``` powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If using Linux:

``` bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

For Visual Studio Code it is necessary that you change your default interpreter to the virtual environment you just created .venv. To do this use the shortcut Ctrl-Shift-P, search for Python: Select interpreter and select .venv from the list. Sometimes it is nice as asks you once you create the environment, the eager to help thing.

### Using make

There is a handy `Makefile` with commands form `make` to use to set up and run the environment:

``` bash
make create-environment
source .venv/bin/activate
make requirements
```

These commands:

1. Creates a virtual environment in `.venv`
2. Activates the environment
3. Updates pip
4. Installs from `requirements.txt`

Make can also do other stuff, which will be touched on later, in the meantime, use `make help` to see the commands that can be run.

## Running the code

``` bash
make run_pipeline
```

### Testing the code

``` bash
make test

# To only run unittests
make unittest

# To only run end-to-end tests
make e2e
```

``` bash
pytest

# To only run unittests
pytest tests/unittests 

# To only run end-to-end tests
pytest tests/e2e_tests
```

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
├── rap_devices
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
├── requirements.txt
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
* pyproject.toml - Project configuration file with package metadata and configuration for tools like black
* requirements.txt - The requirements file for reproducing the analysis environment.
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

### Source code - `rap_devices`

This contains the source code for use in this project. This is where the code to do everything important should sit.

* `__init__.py` - Makes rap_devices a Python module
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
