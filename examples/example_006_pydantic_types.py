import typer
from pydantic import HttpUrl, conint

from pydantic_typer import enable_pydantic_type_validation

EvenInt = conint(multiple_of=2)


@enable_pydantic_type_validation
def main(num: EvenInt, url: HttpUrl):  # type: ignore
    print(num, type(num))
    print(url, type(url))


if __name__ == "__main__":
    typer.run(main)
