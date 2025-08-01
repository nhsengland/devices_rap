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

## Key Concepts

### Rendered vs Non-Rendered Files

- **`content/`**: Contains all markdown files that become web pages
- **`assets/`**: Contains images, CSS, and other static files referenced by pages
- **`overrides/`**: Contains theme customization templates
- **`site/`**: Generated output (do not edit directly)

### Configuration Files

- **`mkdocs.yml`**: Main configuration specifying site settings, theme, plugins, and navigation
- **`gen_ref_pages.py`**: Build script that generates API reference markdown files from Python docstrings

## Usage

### Building Documentation

```bash
# Generate API reference files (run when modules change)
make docs-generate

# Build static documentation
make docs-build

# Start development server with live reload
make docs-serve

# Generate and serve (combined)
make docs
```

### Adding New Content

1. **New Pages**: Add markdown files to `content/` and update navigation in `mkdocs.yml`
2. **Images**: Add to `assets/images/` and reference as `assets/images/filename.jpg`
3. **Styling**: Modify `assets/stylesheets/nhs_style.css`
4. **API Docs**: Run `make docs-generate` after adding new Python modules

### Theme Customization

- **Header/Footer**: Edit files in `overrides/partials/`
- **Styling**: Modify `assets/stylesheets/nhs_style.css`
- **Templates**: Add new templates to `overrides/`

## NHS England Branding

The documentation uses official NHS England branding:

- **Logo**: NHS England blue-on-white logo in header
- **Colors**: NHS England indigo primary color scheme
- **Fonts**: Arial font family for accessibility
- **Favicon**: NHS England favicon for browser tabs

All branding assets are stored in `assets/images/` and referenced in `mkdocs.yml`.

## Maintenance

- **Dependencies**: Specified in project `requirements.txt`
- **Auto-generation**: API docs are generated from NumPy-style docstrings
- **Versioning**: Documentation is version-controlled with the code
- **Deployment**: Built site in `site/` directory ready for hosting

For more information, see the [MkDocs documentation](https://www.mkdocs.org/) and [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).
