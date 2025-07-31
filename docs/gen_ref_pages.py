"""Generate static API reference pages from Python modules.

This script creates actual markdown files for each Python module in the devices_rap package.
The generated files use mkdocstrings directives to extract NumPy-style docstrings.

Run this script whenever you add new modules or want to regenerate the API reference files.

Usage
-----
    python docs/gen_ref_pages.py
"""

from pathlib import Path


def create_api_reference_files():
    """Create static API reference markdown files for all Python modules.

    This function scans the devices_rap package and generates markdown files
    for each Python module, creating the structure needed for mkdocstrings
    to extract NumPy-style docstrings.
    """

    # Get the project root and source directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    src_path = project_root / "devices_rap"
    docs_api_ref = script_dir / "docs" / "api_reference"

    # Ensure the api_reference directory exists
    docs_api_ref.mkdir(parents=True, exist_ok=True)

    # Track all modules for the main index
    modules = []

    # Process all Python files in the devices_rap package
    for path in sorted(src_path.rglob("*.py")):
        # Skip __pycache__ directories and files
        if "__pycache__" in str(path):
            continue

        # Calculate module path relative to the source
        module_path = path.relative_to(project_root).with_suffix("")

        # Convert file path to module notation
        parts = list(module_path.parts)

        if parts[-1] == "__init__":
            # Handle __init__.py files
            parts = parts[:-1]
            if len(parts) == 1:  # Main package __init__.py
                continue  # Skip main package init, we'll handle it separately

            # Create index.md for subpackages
            subpackage_dir = docs_api_ref / Path(*parts[1:])  # Skip 'devices_rap'
            subpackage_dir.mkdir(parents=True, exist_ok=True)

            module_name = ".".join(parts)
            file_path = subpackage_dir / "index.md"

            # Find submodules in this package
            package_path = project_root / Path(*parts)
            submodules = []
            for subfile in package_path.glob("*.py"):
                if subfile.name != "__init__.py":
                    submodule_name = subfile.stem
                    submodules.append((submodule_name, f"{submodule_name}.md"))

            content = f"# {parts[-1]}\n\n"
            if len(parts) > 1:
                content += f"{parts[-1].title()} utilities for the devices_rap package.\n\n"
            content += f"::: {module_name}\n"

            if submodules:
                content += "\n## Submodules\n\n"
                for submod_name, submod_file in submodules:
                    content += f"- [{submod_name}]({submod_file}) - {submod_name.replace('_', ' ').title()} utilities\n"

        elif parts[-1] == "__main__":
            continue  # Skip __main__.py files
        else:
            # Handle regular Python files
            module_name = ".".join(parts)

            # Create directory structure if needed
            if len(parts) > 2:  # It's in a subpackage
                subdir = docs_api_ref / Path(*parts[1:-1])  # Skip 'devices_rap' and filename
                subdir.mkdir(parents=True, exist_ok=True)
                file_path = subdir / f"{parts[-1]}.md"
            else:
                file_path = docs_api_ref / f"{parts[-1]}.md"

            content = f"# {parts[-1]}\n\n::: {module_name}\n"

            # Track for main index
            if len(parts) == 2:  # Top-level module
                modules.append(
                    (
                        parts[-1],
                        f"{parts[-1]}.md",
                        f"{parts[-1].replace('_', ' ').title()} utilities",
                    )
                )

        # Write the file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Created: {file_path.relative_to(script_dir)}")

    # Create the main API reference index
    index_content = """# API Reference

This section contains the API documentation for the devices_rap package.

## Main Package

::: devices_rap

## Modules

"""

    # Add modules to index
    for module_name, module_file, description in sorted(modules):
        if module_name == "data_in":
            index_content += f"- [{module_name}](data_in/index.md) - {description}\n"
        else:
            index_content += f"- [{module_name}]({module_file}) - {description}\n"

    index_path = docs_api_ref / "index.md"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_content)
    print(f"Created: {index_path.relative_to(script_dir)}")

    print("API reference files generated successfully!")
    print(f"Total files created: {len(list(docs_api_ref.rglob('*.md')))}")


if __name__ == "__main__":
    create_api_reference_files()
