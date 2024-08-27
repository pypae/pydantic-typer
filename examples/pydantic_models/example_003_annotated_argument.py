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
