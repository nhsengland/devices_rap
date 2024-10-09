from pathlib import Path

import pytest
import typer
from loguru import logger
from tqdm import tqdm

from rap_devices import pipeline

app = typer.Typer()


def test_main():
    pipeline.main()
    assert False


if __name__ == "__main__":
    pytest.main([__file__])
