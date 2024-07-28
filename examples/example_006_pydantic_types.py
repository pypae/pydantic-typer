import typer
from pydantic.types import conint

from pydantic_typer import enable_pydantic_type_validation

EvenInt = conint(multiple_of=2)


@enable_pydantic_type_validation
def main(num: EvenInt):  # type: ignore
    print(num, type(num))


if __name__ == "__main__":
    typer.run(main)
