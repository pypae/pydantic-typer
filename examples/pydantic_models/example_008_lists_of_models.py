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
    pets: list[Pet]


def main(persons: list[Person]):
    typer.echo(f"{persons} {type(persons)}")


if __name__ == "__main__":
    pydantic_typer.run(main)
