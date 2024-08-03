#!/bin/bash
git clone https://github.com/tiangolo/typer regression_tests/typer
hatch test -p regression_tests/conftest.py regression_tests/typer/tests --ignore regression_tests/typer/tests/test_cli
rm -rf regression_tests/typer
