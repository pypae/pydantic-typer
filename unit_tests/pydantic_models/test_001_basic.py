import subprocess
import sys

from typer.testing import CliRunner

import pydantic_typer
from examples.pydantic_models import example_001_basic as mod

runner = CliRunner()

app = pydantic_typer.Typer()
app.command()(mod.main)


def test_help():
    result = runner.invoke(app, ["--help"])
    assert "The id of the user." in result.output
    assert result.exit_code == 0


def test_parse_pydantic_model():
    result = runner.invoke(app, ["1", "--user.id", "2", "--user.name", "John Doe"])
    assert "1 <class 'int'>" in result.output
    assert "id=2 name='John Doe' <class 'examples.pydantic_models.example_001_basic.User'>" in result.output


def test_script():
    result = subprocess.run(
        [sys.executable, "-m", "coverage", "run", mod.__file__, "--help"],
        capture_output=True,
        encoding="utf-8",
        check=False,
    )
    assert "Usage" in result.stdout
