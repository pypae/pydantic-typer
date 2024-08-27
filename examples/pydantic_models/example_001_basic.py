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
