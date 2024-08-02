import subprocess
import sys

from typer.testing import CliRunner

from examples import example_005_multi_commands as mod

runner = CliRunner()

app = mod.app


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0


def test_all_commands():
    result = runner.invoke(app, ["hi", "--user.id", "1"])
    assert "Hi id=1 name='John'" in result.output
    result = runner.invoke(app, ["bye", "--user.id", "1"])
    assert "Bye id=1 name='John'" in result.output


def test_script():
    result = subprocess.run(
        [sys.executable, "-m", "coverage", "run", mod.__file__, "--help"],
        capture_output=True,
        encoding="utf-8",
        check=False,
    )
    assert "Usage" in result.stdout
