# Developer Guide

This guide provides comprehensive information for developers working on the Devices RAP pipeline, including setup, development workflow, testing, and contribution guidelines.

## Development Environment Setup

### Prerequisites

* Python 3.8 or higher
* Git
* [uv](https://docs.astral.sh/uv/) package manager (recommended)
* Make (Linux/macOS) or equivalent

### Initial Setup

#### 1. Clone and Set Up the Repository

```bash
git clone https://github.com/nhsengland/devices_rap.git
cd devices_rap
```

#### 2. Install Development Dependencies

**Using uv (Recommended):**

```bash
uv sync --dev
```

**Using pip:**

```bash
pip install -e ".[dev]"
```

**Using Make:**

```bash
make install
```

#### 3. Set Up Pre-commit Hooks

```bash
pre-commit install
```

### Development Tools

The project includes several development tools configured in `pyproject.toml`:

* **Testing:** pytest for unit and integration tests
* **Linting:** flake8, pylint for code quality
* **Formatting:** black for code formatting
* **Type Checking:** mypy for static type analysis
* **Documentation:** mkdocs with material theme

## Project Structure

```
devices_rap/
├── devices_rap/           # Main package
│   ├── __init__.py
│   ├── pipeline.py        # Main pipeline orchestration
│   ├── config.py          # Configuration management
│   ├── data_io/           # Data input/output utilities
│   │   ├── core.py
│   │   ├── utils.py
│   │   ├── input/
│   │   └── output/
│   └── ...                # Other modules
├── tests/
│   ├── unittests/         # Unit tests
│   └── e2e_tests/         # End-to-end tests
├── docs/                  # Documentation
├── data/                  # Data files (not in version control)
├── pyproject.toml         # Project configuration
└── Makefile              # Build automation
```

## Development Workflow

### 1. Creating a New Feature

```bash
# Create a new branch from main
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

### 2. Making Changes

* Write clean, documented code following the project style
* Add appropriate type hints
* Include docstrings for functions and classes
* Write tests for new functionality

### 3. Running Tests

**Run all tests:**

```bash
make test
```

**Run unit tests only:**

```bash
make unittest
```

**Run end-to-end tests only:**

```bash
make e2e
```

**Using pytest directly:**

```bash
# All tests
pytest

# Unit tests only
pytest tests/unittests

# End-to-end tests only
pytest tests/e2e_tests

# With coverage
pytest --cov=devices_rap
```

### 4. Code Quality Checks

**Run linting:**

```bash
make lint
```

**Run formatting:**

```bash
make format
```

**Run type checking:**

```bash
make typecheck
```

**Run all quality checks:**

```bash
make check
```

## Testing Guidelines

### Writing Tests

* Use pytest for all tests
* Follow the Arrange-Act-Assert pattern
* Use descriptive test names that explain what is being tested
* Mock external dependencies and database connections
* Place test files in appropriate directories under `tests/`

### Test Categories

* **Unit Tests:** Test individual functions and classes in isolation
* **Integration Tests:** Test interactions between components
* **End-to-End Tests:** Test complete pipeline workflows

### Example Test Structure

```python
import pytest
from devices_rap.module import function_to_test

class TestFunctionToTest:
    def test_should_return_expected_result_when_given_valid_input(self):
        # Arrange
        input_data = "test_input"
        expected = "expected_output"
        
        # Act
        result = function_to_test(input_data)
        
        # Assert
        assert result == expected
        
    def test_should_raise_exception_when_given_invalid_input(self):
        # Arrange
        invalid_input = None
        
        # Act & Assert
        with pytest.raises(ValueError):
            function_to_test(invalid_input)
```

## Code Style Guidelines

### Python Style

* Follow [PEP 8](https://pep8.org/) conventions
* Use [Black](https://black.readthedocs.io/) for automatic formatting
* Maximum line length: 88 characters (Black default)
* Use type hints for function parameters and return values

### Documentation Style

* Use [numpy-style docstrings](https://numpydoc.readthedocs.io/en/latest/format.html)
* Include parameter types and descriptions
* Document return values and exceptions

### Example Function Documentation

```python
def process_device_data(data: pd.DataFrame, config: Config) -> pd.DataFrame:
    """
    Process device data according to the specified configuration.
    
    Parameters
    ----------
    data : pd.DataFrame
        Raw device data to process
    config : Config
        Configuration object containing processing parameters
        
    Returns
    -------
    pd.DataFrame
        Processed device data
        
    Raises
    ------
    ValueError
        If input data is empty or malformed
    """
    pass
```

## Documentation Development

### Building Documentation Locally

```bash
# Build and serve docs locally
make docs-serve

# Build docs only
make docs-build
```

### Adding New Documentation

1. Create markdown files in `docs/content/`
2. Update `docs/mkdocs.yml` navigation
3. Use mkdocstrings for API documentation
4. Follow the existing documentation structure

## Git Workflow

### Commit Messages

Use clear, descriptive commit messages:

```
feat: add new data validation module
fix: resolve connection timeout in SQL loader
docs: update API reference for data_io module
test: add unit tests for config parser
```

### Branch Naming

Use the format: `<developer_name_short>/<jira_ticket>_<description>`

Examples:
* `jw/DEV-123_add-data-validation-module`
* `as/BUG-456_fix-sql-connection-timeout`
* `mk/DOC-789_update-api-reference`

### Pull Request Process

1. Create a pull request from your feature branch to `main`
2. Ensure all tests pass and code quality checks succeed
3. Include a clear description of changes
4. Request review from team members
5. Address feedback and update as needed

## Environment Variables

For development, copy `example.env` to `.env` and configure:

```bash
cp example.env .env
```

Key environment variables:

* `DATABASE_URL` - SQL server connection string
* `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
* `OUTPUT_PATH` - Path for pipeline outputs

## Troubleshooting Development Issues

### Common Problems

* **Import errors:** Ensure you've installed the package in development mode (`pip install -e .`)
* **Test failures:** Check that test data files are present and accessible
* **Linting errors:** Run `make format` to auto-fix formatting issues
* **Type checking errors:** Add appropriate type hints or type ignore comments

### Getting Help

* Check the [API Reference](../api_reference/index.md) for module documentation
* Review existing tests for examples
* Contact the development team for guidance
* Check GitHub issues for known problems and solutions

## Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` with release notes
3. Create a release branch
4. Run full test suite
5. Create pull request for review
6. Merge to main and tag release
7. Deploy documentation updates

---

For questions or suggestions about the development process, please open an issue or contact the development team.