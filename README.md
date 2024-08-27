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

:technologist: Simply use `pydantic_typer.run` instead of `typer.run` to enable pydantic support

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
    typer.echo(f"{num} {type(num)}")
    typer.echo(f"{user} {type(user)}")


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
    typer.echo(f"{num} {type(num)}")
    typer.echo(f"{user} {type(user)}")


if __name__ == "__main__":
    pydantic_typer.run(main)
```

</td>
</tr>

<tr>
<td>
<details>
  <summary>
    :computer: Usage
  </summary>

```console
$ # Run the basic example:
$ python main.py
Usage: main.py [OPTIONS] NUM
Try 'main.py --help' for help.
╭─ Error ────────────────────────────────────────────────────────────╮
│ Missing argument 'NUM'.                                            │
╰────────────────────────────────────────────────────────────────────╯

$ # We're missing a required argument, try using --help as suggested:
$ python main.py --help
Usage: main.py [OPTIONS] NUM

╭─ Arguments ────────────────────────────────────────────────────────╮
│ *    num      INTEGER  [default: None] [required]                  │
╰────────────────────────────────────────────────────────────────────╯
╭─ Options ──────────────────────────────────────────────────────────╮
│ *  --user.id          INTEGER  The id of the user. [default: None] │
│                                [required]                          │
│    --user.name        TEXT     The name of the user.               │
│                                [default: Jane Doe]                 │
│    --help                      Show this message and exit.         │
╰────────────────────────────────────────────────────────────────────

$ # Notice the help text for `user.id` and `user.name` are inferred from the `pydantic.Field`.
$ # `user.id` is reqired, because we don't provide a default value for the field.
$ # Now run the example with the required arguments:
$ python main.py 1 --user.id 1
1 <class 'int'>
id=1 name='Jane Doe' <class '__main__.User'>

$ # It worked! You can also experiment with an invalid `user.id`:
$ python main.py 1 --user.id some-string
Usage: example_001_basic.py [OPTIONS] NUM
Try 'example_001_basic.py --help' for help.
╭─ Error ─────────────────────────────────────────────────────────────╮
│ Invalid value for '--user.id': 'some-string' is not a valid integer.│
╰─────────────────────────────────────────────────────────────────────╯
```

</td>
</tr>

</table>

### Usage with nested models

<table>
<tr>
<td>

:technologist: `pydantic_typer.run` also works with nested pydantic models

</td>
</tr>
<tr>
<td>

```python
from __future__ import annotations

from typing import Optional

import pydantic
import typer

import pydantic_typer


class Pet(pydantic.BaseModel):
    name: str
    species: str


class Person(pydantic.BaseModel):
    name: str
    age: Optional[float] = None  # noqa: UP007 For Python versions >=3.10, prefer float | None
    pet: Pet


def main(person: Person):
    typer.echo(f"{person} {type(person)}")


if __name__ == "__main__":
    pydantic_typer.run(main)
```

</td>
</tr>

<tr>
<td>
<details>
  <summary>
    :computer: Usage
  </summary>

```console
$ # Run the nested models example with the required options:
$ python main.py --person.name "Patrick" --person.pet.name "Snoopy" --person.pet.species "Dog"
name='Patrick' age=None pet=Pet(name='Snoopy', species='Dog') <class '__main__.Person'>
```

</td>
</tr>
</table>

### Use `pydantic` models with `typer.Argument`

<table>
<tr>
<td>

:technologist: You can annotate the parameters with `typer.Argument` to make all model fields CLI arguments

</td>
</tr>
<tr>
<td>

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
    typer.echo(f"{num} {type(num)}")
    typer.echo(f"{user} {type(user)}")


if __name__ == "__main__":
    pydantic_typer.run(main)
```

</td>
</tr>
<tr>
<td>
<details>
  <summary>
    :computer: Usage
  </summary>

```console
$ # Run the example
$ python main.py
Usage: main.py [OPTIONS] _PYDANTIC_USER_ID
                                         _PYDANTIC_USER_NAME
Try 'main.py --help' for help.
╭─ Error ─────────────────────────────────────────────────────────────╮
│ Missing argument '_PYDANTIC_USER_ID'.                               │
╰─────────────────────────────────────────────────────────────────────╯

$ # Notice how _PYDANTIC_USER_ID and _PYDANTIC_USER_NAME are now cli arguments instead of options.
$ # Supply the arguments in the right order:
> python main.py 1 Patrick --num 1
1 <class 'int'>
id=1 name='Patrick' <class '__main__.User'>
```

</td>
</tr>
<tr>
<td>

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
    typer.echo(f"{num} {type(num)}")
    typer.echo(f"{user} {type(user)}")


if __name__ == "__main__":
    pydantic_typer.run(main)
```

Here, `User` is a `typer.Argument`, but we manually override the fields again:

- We override the `metavar` of to `User.id` be `THE_ID`
- And `User.name` to be a `typer.Option`

</details>
</td>
</tr>
</table>

### Use pydantic models in multiple commands

<table>
<tr>
<td>

:technologist: For larger `typer` apps, you can use `pydantic_typer.Typer` instead of annotating each command function individually to enable pydantic models on all commands

</td>
</tr>
<tr>
<td>

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
    typer.echo(f"Hi {user}")


@app.command()
def bye(user: User):
    typer.echo(f"Bye {user}")


if __name__ == "__main__":
    app()
```

</td>
</tr>
</table>

### Use pydantic types

<table>
<tr>
<td>

:technologist: You can also annotate arguments with [pydantic types](https://docs.pydantic.dev/latest/concepts/types/) and they will be validated

</td>
</tr>
<tr>
<td>

```python
import click
import typer
from pydantic import HttpUrl, conint

import pydantic_typer

EvenInt = conint(multiple_of=2)


def main(num: EvenInt, url: HttpUrl, ctx: click.Context):  # type: ignore
    typer.echo(f"{num} {type(num)}")
    typer.echo(f"{url} {type(url)}")


if __name__ == "__main__":
    pydantic_typer.run(main)
```

</td>
</tr>
</table>

<table>
<tr>
<td>

:technologist: Pydantic types also work in lists and tuples

</td>
</tr>
<tr>
<td>

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

</td>
</tr>
</table>

### Limitations

> [!WARNING]  
> `pydantic-typer` does not yet support sequences of pydantic models: See [this issue](https://github.com/pypae/pydantic-typer/issues/6) for details

> [!WARNING]  
> `pydantic-typer` does not yet support self-referential pydantic models.

## License

`pydantic-typer` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
