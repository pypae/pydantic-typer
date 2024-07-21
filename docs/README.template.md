<!---
Do not edit `README.md` manually, instead edit `docs/README.template.md` and run `python docs/scripts/make_docs.py`.
-->

# Pydantic Typer

[![PyPI - Version](https://img.shields.io/pypi/v/pydantic-typer.svg)](https://pypi.org/project/pydantic-typer)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pydantic-typer.svg)](https://pypi.org/project/pydantic-typer)
[![Test Coverage](https://coverage-badge.samuelcolvin.workers.dev/pypae/pydantic-typer.svg)](https://coverage-badge.samuelcolvin.workers.dev/redirect/pypae/pydantic-typer)

[Typer](https://github.com/tiangolo/typer) extension to enable pydantic support

> [!WARNING]  
> This package is still in early development and some things might not work as expected, or change between versions.

---

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Installation

```console
pip install pydantic-typer
```

> [!NOTE]
> `pydantic-typer` comes with `pydantic` and `typer` as dependencies, so you don't need to install anything else.

## Usage

For general `typer` usage, please refer to the [typer documentation](https://typer.tiangolo.com/).

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

### Use `pydantic` models with `typer.Argument`

You can annotate the parameters with `typer.Argument` to make all model fields CLI arguments:

{example_003_annotated_argument}

<details>
<summary>:bulb: You can also override annotations directly on the pydantic model fields:</summary>

{example_004_argument_override}

Here, `User` is a `typer.Argument`, but we manually override the fields again:

- We override the `metavar` of to `User.id` be `THE_ID`
- And `User.name` to be a `typer.Option`

</details>

### Use pydantic models in multiple commands

For larger `typer` apps, you can use `pydantic_typer.PydanticTyper` instead of annotating each command function individually to enable pydantic models on all commands:

{example_005_multi_commands}

## License

`pydantic-typer` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
