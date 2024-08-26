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

<table>
<tr>
<td>

Simply use `pydantic_typer.run` instead of `typer.run` to enable pydantic support

</td>
</tr>
<tr>
<td>

```python
from typing import Annotated

import pydantic
import typer

import pydantic_typer


class User(pydantic.BaseModel):
    id: Annotated[int, pydantic.Field(description="The id of the user.")]
    name: Annotated[str, pydantic.Field(description="The name of the user.")] = "Jane Doe"


def main(num: int, user: User):
    print(num, type(num))
    print(user, type(user))


if __name__ == "__main__":
    pydantic_typer.run(main)
```

</td>
</tr>

<tr>
<td>
<details>
  <summary>
    :t-rex: Non-Annotated Version
  </summary>

```python
import pydantic
import typer

import pydantic_typer


class User(pydantic.BaseModel):
    id: int = pydantic.Field(description="The id of the user.")
    name: str = pydantic.Field("Jane Doe", description="The name of the user.")


def main(num: int, user: User):
    print(num, type(num))
    print(user, type(user))


if __name__ == "__main__":
    pydantic_typer.run(main)
```

</td>
</tr>

</table>

### Usage with nested models

`pydantic_typer.run` also works with nested pydantic models:

```python
from __future__ import annotations

from typing import Optional

import pydantic

import pydantic_typer


class Pet(pydantic.BaseModel):
    name: str
    species: str


class Person(pydantic.BaseModel):
    name: str
    age: Optional[float] = None  # noqa: UP007 typer does not support float | None yet, see https://github.com/tiangolo/typer/pull/548
    pet: Pet


def main(person: Person):
    print(person, type(person))


if __name__ == "__main__":
    pydantic_typer.run(main)
```

### Use `pydantic` models with `typer.Argument`

You can annotate the parameters with `typer.Argument` to make all model fields CLI arguments:

```python
from __future__ import annotations

import pydantic
import typer
from typing_extensions import Annotated

import pydantic_typer


class User(pydantic.BaseModel):
    id: int
    name: str


def main(num: Annotated[int, typer.Option()], user: Annotated[User, typer.Argument()]):
    print(num, type(num))
    print(user, type(user))


if __name__ == "__main__":
    pydantic_typer.run(main)
```

<details>
<summary>:bulb: You can also override annotations directly on the pydantic model fields:</summary>

```python
from __future__ import annotations

import pydantic
import typer
from typing_extensions import Annotated

import pydantic_typer


class User(pydantic.BaseModel):
    id: Annotated[int, typer.Argument(metavar="THE_ID")]
    name: Annotated[str, typer.Option()]


def main(num: Annotated[int, typer.Option()], user: Annotated[User, typer.Argument()]):
    print(num, type(num))
    print(user, type(user))


if __name__ == "__main__":
    pydantic_typer.run(main)
```

Here, `User` is a `typer.Argument`, but we manually override the fields again:

- We override the `metavar` of to `User.id` be `THE_ID`
- And `User.name` to be a `typer.Option`

</details>

### Use pydantic models in multiple commands

For larger `typer` apps, you can use `pydantic_typer.Typer` instead of annotating each command function individually to enable pydantic models on all commands:

```python
from __future__ import annotations

import pydantic
import typer
from typing_extensions import Annotated

from pydantic_typer import Typer

app = Typer()


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
from pydantic import HttpUrl, conint

import pydantic_typer

EvenInt = conint(multiple_of=2)


def main(num: EvenInt, url: HttpUrl, ctx: click.Context):  # type: ignore
    print(num, type(num))
    print(url, type(url))


if __name__ == "__main__":
    pydantic_typer.run(main)
```

Pydantic types also work in lists and tuples:

```python
from typing import List

import typer
from pydantic import AnyHttpUrl

import pydantic_typer


def main(urls: List[AnyHttpUrl] = typer.Option([], "--url")):
    typer.echo(f"urls: {urls}")


if __name__ == "__main__":
    pydantic_typer.run(main)
```

## License

`pydantic-typer` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
