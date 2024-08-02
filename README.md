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

> [!NOTE] > `pydantic-typer` comes with `pydantic` and `typer` as dependencies, so you don't need to install anything else.

## Usage

For general `typer` usage, please refer to the [typer documentation](https://typer.tiangolo.com/).

All the code blocks below can be copied and used directly (they are tested Python files).
To run any of the examples, copy the code to a file `main.py`, and run it:

```console
python main.py
```

### Basic Usage

Simply add the `@enable_pydantic` decorator to any function that you use with `typer.run`:

```python
import pydantic
import typer

from pydantic_typer import enable_pydantic


class User(pydantic.BaseModel):
    id: int
    name: str = "Jane Doe"


@enable_pydantic
def main(num: int, user: User):
    print(num, type(num))
    print(user, type(user))


if __name__ == "__main__":
    typer.run(main)
```

### Usage with nested models

`@enable_pydantic` also works with nested pydantic models:

```python
from __future__ import annotations

from typing import Optional

import pydantic
import typer

from pydantic_typer import enable_pydantic


class Pet(pydantic.BaseModel):
    name: str
    species: str


class Person(pydantic.BaseModel):
    name: str
    age: Optional[float] = None  # noqa: UP007 typer does not support float | None yet, see https://github.com/tiangolo/typer/pull/548
    pet: Pet


@enable_pydantic
def main(person: Person):
    print(person, type(person))


if __name__ == "__main__":
    typer.run(main)
```

### Use `pydantic` models with `typer.Argument`

You can annotate the parameters with `typer.Argument` to make all model fields CLI arguments:

```python
from __future__ import annotations

import pydantic
import typer
from typing_extensions import Annotated

from pydantic_typer import enable_pydantic


class User(pydantic.BaseModel):
    id: int
    name: str


@enable_pydantic
def main(num: Annotated[int, typer.Option()], user: Annotated[User, typer.Argument()]):
    print(num, type(num))
    print(user, type(user))


if __name__ == "__main__":
    typer.run(main)
```

<details>
<summary>:bulb: You can also override annotations directly on the pydantic model fields:</summary>

```python
from __future__ import annotations

import pydantic
import typer
from typing_extensions import Annotated

from pydantic_typer import enable_pydantic


class User(pydantic.BaseModel):
    id: Annotated[int, typer.Argument(metavar="THE_ID")]
    name: Annotated[str, typer.Option()]


@enable_pydantic
def main(num: Annotated[int, typer.Option()], user: Annotated[User, typer.Argument()]):
    print(num, type(num))
    print(user, type(user))


if __name__ == "__main__":
    typer.run(main)
```

Here, `User` is a `typer.Argument`, but we manually override the fields again:

- We override the `metavar` of to `User.id` be `THE_ID`
- And `User.name` to be a `typer.Option`

</details>

### Use pydantic models in multiple commands

For larger `typer` apps, you can use `pydantic_typer.PydanticTyper` instead of annotating each command function individually to enable pydantic models on all commands:

```python
from __future__ import annotations

import pydantic
import typer
from typing_extensions import Annotated

from pydantic_typer import PydanticTyper

app = PydanticTyper()


class User(pydantic.BaseModel):
    id: int
    name: Annotated[str, typer.Option()] = "John"


@app.command()
def hi(user: User):
    print(f"Hi {user}")


@app.command()
def bye(user: User):
    print(f"Bye {user}")


if __name__ == "__main__":
    app()
```

### Use pydantic types

You can also annotate arguments with [pydantic types](https://docs.pydantic.dev/latest/concepts/types/) and they will be validated:

```python
import click
import typer
from pydantic import HttpUrl, conint

from pydantic_typer import enable_pydantic_type_validation

EvenInt = conint(multiple_of=2)


@enable_pydantic_type_validation
def main(num: EvenInt, url: HttpUrl, ctx: click.Context):  # type: ignore
    print(num, type(num))
    print(url, type(url))


if __name__ == "__main__":
    typer.run(main)
```

## License

`pydantic-typer` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
