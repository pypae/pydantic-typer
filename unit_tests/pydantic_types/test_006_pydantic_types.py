import subprocess
import sys

from typer.testing import CliRunner

import pydantic_typer
from examples.pydantic_types import example_006_pydantic_types as mod

runner = CliRunner()

app = pydantic_typer.Typer()
app.command()(mod.main)


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0


def test_valid_input():
    result = runner.invoke(app, ["2", "https://google.com"])
    assert "2 <class 'int'>" in result.output
    assert "https://google.com/ <class 'pydantic_core._pydantic_core.Url'>" in result.output


def test_invalid_url():
    result = runner.invoke(app, ["2", "ftp://ftp.google.com"])
    assert "Invalid value for url: URL scheme should be 'http' or 'https'" in result.output


def test_script():
    result = subprocess.run(
        [sys.executable, "-m", "coverage", "run", mod.__file__, "--help"],
        capture_output=True,
        encoding="utf-8",
        check=False,
    )
    assert "Usage" in result.stdout
