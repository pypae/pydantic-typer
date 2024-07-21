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
