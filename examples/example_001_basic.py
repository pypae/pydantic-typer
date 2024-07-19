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
