import importlib
import subprocess
import sys

import pytest
from typer.testing import CliRunner

import pydantic_typer

runner = CliRunner()


@pytest.fixture(params=["examples.pydantic_models.example_001_basic", "examples.pydantic_models.example_001_basic_an"])
def mod(request):
    return importlib.import_module(request.param)


@pytest.fixture
def app(mod):
    app = pydantic_typer.Typer()
    app.command()(mod.main)
    return app


def test_help(app):
    result = runner.invoke(app, ["--help"])
    assert "The id of the user." in result.output
    assert result.exit_code == 0


def test_parse_pydantic_model(mod, app):
    result = runner.invoke(app, ["1", "--user.id", "2", "--user.name", "John Doe"])
    assert "1 <class 'int'>" in result.output
    assert f"id=2 name='John Doe' <class '{mod.__name__}.User'>" in result.output


def test_script(mod):
    result = subprocess.run(
        [sys.executable, "-m", "coverage", "run", mod.__file__, "--help"],
        capture_output=True,
        encoding="utf-8",
        check=False,
    )
    assert "Usage" in result.stdout
