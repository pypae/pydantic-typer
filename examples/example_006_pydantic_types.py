import click
import typer
from pydantic import HttpUrl, conint

import pydantic_typer

EvenInt = conint(multiple_of=2)


def main(num: EvenInt, url: HttpUrl, ctx: click.Context):  # type: ignore
    print(num, type(num))
    print(url, type(url))


if __name__ == "__main__":
    pydantic_typer.run(main)
