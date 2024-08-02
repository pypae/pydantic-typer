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
