import subprocess
import sys

from typer.testing import CliRunner

import pydantic_typer
from examples import example_003_annotated_argument as mod

runner = CliRunner()

app = pydantic_typer.Typer()
app.command()(mod.main)


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0


def test_parse_pydantic_model():
    result = runner.invoke(app, '--num 1 2 "John Doe"')
    assert "1 <class 'int'>" in result.output
    assert "id=2 name='John Doe' <class 'examples.example_003_annotated_argument.User'>" in result.output


def test_wrong_order():
    result = runner.invoke(app, '--num 1 "John Doe" 2')
    assert result.exit_code == 2
    assert "Usage" in result.output


def test_script():
    result = subprocess.run(
        [sys.executable, "-m", "coverage", "run", mod.__file__, "--help"],
        capture_output=True,
        encoding="utf-8",
        check=False,
    )
    assert "Usage" in result.stdout
