"""
Entry point for running devices_rap as a module.

This allows the package to be run with:
    python -m devices_rap
    uv run python -m devices_rap
"""

from devices_rap.pipeline import app

if __name__ == "__main__":
    app()
