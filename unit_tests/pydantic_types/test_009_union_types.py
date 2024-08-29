import subprocess
import sys

from typer.testing import CliRunner

import pydantic_typer
from examples.pydantic_types import example_009_union_types as mod

runner = CliRunner()

app = pydantic_typer.Typer()
app.command()(mod.main)


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0


def test_bool():
    result = runner.invoke(app, ["--value", "True"])
    assert "bool" in result.output


def test_int():
    result = runner.invoke(app, ["--value", "2"])
    assert "int" in result.output


def test_float():
    result = runner.invoke(app, ["--value", "2.1"])
    assert "float" in result.output


def test_string():
    result = runner.invoke(app, ["--value", "Hello!"])
    assert "str" in result.output


def test_precedence():
    # Types left of the union operator take precedence over types to the right.
    # So in this case bool > int > float > str, if possible.
    result = runner.invoke(app, ["--value", "1"])
    assert "bool" in result.output

    result = runner.invoke(app, ["--value", "2.0"])
    assert "int" in result.output


def test_script():
    result = subprocess.run(
        [sys.executable, "-m", "coverage", "run", mod.__file__, "--help"],
        capture_output=True,
        encoding="utf-8",
        check=False,
    )
    assert "Usage" in result.stdout
