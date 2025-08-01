# MkDocs Documentation

This directory contains the MkDocs documentation system for the Devices RAP project.

## Quick Start

```bash
# Build and serve documentation locally
make docs-serve

# Or individual commands:
make docs-generate    # Generate API reference from docstrings
make docs-build       # Build static site
```

## Directory Structure

```text
docs/
├── mkdocs.yml                    # MkDocs configuration
├── gen_ref_pages.py             # API reference generator script
├── STRUCTURE.md                 # This file - complete documentation guide
├── overrides/                   # Theme customizations
│   ├── main.html               # Main template override
│   └── partials/               # Template partials
│       ├── header.html         # NHS header
│       └── footer.html         # NHS footer
├── content/                    # ALL CONTENT (rendered as website)
│   ├── index.md               # Homepage
│   ├── usage.md               # Usage guide
│   ├── worksheet_output_documentation.md
│   ├── api_reference/         # Auto-generated API docs
│   ├── functional_process_maps/
│   ├── images/                # Images and logos
│   │   ├── logo/             # NHS England logos
│   │   └── favicon/          # Favicons
│   └── stylesheets/          # CSS files
│       └── nhs_style.css     # NHS styling
└── site/                     # Generated website (do not edit)
```

## Key Organization

* **`content/`** = Everything that becomes part of the website (pages + assets)
* **`overrides/`** = Theme customization templates  
* **Root files** = Configuration and build scripts
* **`site/`** = Generated output (ignored by git)

## Adding Content

### New Documentation Pages

1. Add markdown files to `content/`
2. Update navigation in `mkdocs.yml`
3. Run `make docs-build` to generate

### API Documentation

1. Add NumPy-style docstrings to Python code:

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
    """
    pass
```

2. Run `make docs-generate` to create API reference files
3. New modules automatically appear in documentation

### Assets (Images, CSS)

* Add images to `content/images/`
* Add CSS to `content/stylesheets/`
* Reference in markdown as `images/filename.jpg` or `stylesheets/style.css`

## Dependencies

Documentation dependencies are in the main project `requirements.txt`:

* `mkdocs` - Static site generator
* `mkdocs-material` - Material Design theme
* `mkdocstrings[python]` - API documentation from docstrings
* `pymdown-extensions` - Advanced markdown features

## NHS England Branding

The documentation uses official NHS England styling with:

* NHS England logo and favicon
* Indigo color scheme
* Arial fonts for accessibility
* Custom header and footer templates

All branding assets are in `content/images/` and styling in `content/stylesheets/nhs_style.css`.

For more information about the main project, see the [project README](../README.md#documentation).
