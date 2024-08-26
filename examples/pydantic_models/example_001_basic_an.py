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
