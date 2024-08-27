import pytest
import typer

import pydantic_typer


@pytest.fixture(autouse=True)
def override_run():
    original_run = typer.run
    typer.run = pydantic_typer.run
    yield
    typer.run = original_run


@pytest.fixture(autouse=True)
def override_typer():
    original_typer = typer.Typer
    typer.Typer = pydantic_typer.Typer
    yield
    typer.Typer = original_typer
