<!---
Do not edit `README.md` manually, instead edit `docs/README.template.md` and run `python docs/scripts/make_docs.py`.
-->

# Pydantic Typer

[![PyPI - Version](https://img.shields.io/pypi/v/pydantic-typer.svg)](https://pypi.org/project/pydantic-typer)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pydantic-typer.svg)](https://pypi.org/project/pydantic-typer)

Typer extension to enable pydantic support

---

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Installation

```console
pip install pydantic-typer
```

_Note: `pydantic-typer` comes with `pydantic` and `typer` as dependencies, so you don't need to install anything else._

## Usage

All the code blocks below can be copied and used directly (they are tested Python files).
To run any of the examples, copy the code to a file `main.py`, and run it:

```console
python main.py
```

### Basic Usage

Simply add the `@enable_pydantic` decorator to any function that you use with `typer.run`:

{example_001_basic}

### Usage with nested models

`@enable_pydantic` also works with nested pydantic models:

{example_002_nested_models}

## License

`pydantic-typer` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
