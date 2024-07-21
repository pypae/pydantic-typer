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
