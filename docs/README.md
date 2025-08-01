# Documentation Structure

This directory contains the complete MkDocs documentation system for the Devices RAP project.

## Directory Structure

```text
docs/
├── mkdocs.yml                    # MkDocs configuration file
├── gen_ref_pages.py             # Script to generate API reference files
├── overrides/                   # MkDocs theme customizations
│   ├── main.html               # Main template override
│   └── partials/               # Template partials
│       ├── header.html         # Custom header with NHS branding
│       └── footer.html         # Custom footer with NHS branding
├── assets/                     # Static assets (not rendered as pages)
│   ├── images/                 # Images and logos
│   │   ├── logo/              # NHS England logos
│   │   └── favicon/           # Favicon files
│   └── stylesheets/           # CSS files
│       └── nhs_style.css      # NHS England custom styling
├── content/                    # Documentation content (rendered as pages)
│   ├── index.md               # Homepage
│   ├── usage.md               # Usage guide
│   ├── worksheet_output_documentation.md # Excel output docs
│   ├── api_reference/         # Auto-generated API documentation
│   ├── functional_process_maps/ # Process documentation
│   └── user_guide/            # User guides
└── site/                      # Generated static site (build output)
```

### Individual commands

```bash
# Generate API reference files
make docs-generate

# Build static documentation
make docs-build

# Serve documentation locally
make docs-serve
```

## How it works

1. **Static Generation**: The `gen_ref_pages.py` script scans all Python modules in the `devices_rap` package and creates markdown files with `:::` directives that tell mkdocstrings which modules to document.

2. **Docstring Extraction**: MkDocs uses the mkdocstrings plugin to automatically extract NumPy-style docstrings from your Python code and render them as formatted documentation.

3. **NumPy Style**: The configuration is set to parse NumPy-style docstrings (which the existing codebase uses) rather than Google-style.

4. **Material Theme**: The documentation uses the Material theme for a modern, responsive design.

## Adding Documentation

### Module Documentation

Simply add docstrings to your Python modules, classes, and functions using NumPy-style formatting:

```python
def my_function(param1: str, param2: int) -> bool:
    """Brief description of the function.
    
    Parameters
    ----------
    param1 : str
        Description of param1
    param2 : int
        Description of param2
        
    Returns
    -------
    bool
        Description of return value
        
    Raises
    ------
    ValueError
        When something goes wrong
    """
    pass
```

### Adding New Modules

When you add new Python modules to the package:

1. Run `make docs-generate` to create new API reference files
2. The new modules will automatically appear in the documentation

## Manual Build Commands

If you prefer not to use make:

```bash
# Generate API reference files
python docs/gen_ref_pages.py

# Build documentation  
mkdocs build --config-file docs/mkdocs.yml

# Serve locally
mkdocs serve --config-file docs/mkdocs.yml
```
