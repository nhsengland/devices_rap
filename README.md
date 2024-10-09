# RAP Devices

[![CCDS: Project Template](https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter)](https://cookiecutter-data-science.drivendata.org/ "cookiecutter-data-science")
![RAP Status: Work in Progress](https://img.shields.io/badge/RAP_Status-WIP-red)
[![licence: MIT](https://img.shields.io/badge/Licence-MIT-yellow.svg)](https://opensource.org/licenses/MIT "MIT License")
[![licence: OGL3](https://img.shields.io/badge/Licence-OGL3-darkgrey "licence: Open Government Licence 3")](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)

This is the RAP rework of the Specialised Services Devices Programming (SSDP) reporting pipeline.

## What is RAP?

Reproducible Analytical Pipelines is a set of tools, principles, and techniques to help you improve your analytical processes.
Learn more about RAP on the [RAP Community of Practice Website](https://nhsdigital.github.io/rap-community-of-practice/)

## Prerequisites

To use this repository you will need access to:

* Python 3.12
<!-- TODO Add additional requirements regarding access to the SQL Databases and any config env files -->
* Recommended - A Linux based development environment: e.g. [WSL](https://learn.microsoft.com/en-us/windows/wsl/), [GitHub Codespaces](https://github.com/features/codespaces), etc.

## Getting Started

> Tell the user how to get started (using a numbered list can be helpful). List one action per step with example code if possible.

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

## Project Organization

```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default mkdocs project; see www.mkdocs.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         rap_devices and configuration for tools like black
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
└── rap_devices   <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes rap_devices a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── dataset.py              <- Scripts to download or generate data
    │
    ├── features.py             <- Code to create features for modeling
    │
    ├── modeling                
    │   ├── __init__.py 
    │   ├── predict.py          <- Code to run model inference with trained models          
    │   └── train.py            <- Code to train models
    │
    └── plots.py                <- Code to create visualizations
```

--------

