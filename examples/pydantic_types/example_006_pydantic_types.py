import click
import typer
from pydantic import HttpUrl, conint

import pydantic_typer

EvenInt = conint(multiple_of=2)


def main(num: EvenInt, url: HttpUrl, ctx: click.Context):  # type: ignore
    typer.echo(f"{num} {type(num)}")
    typer.echo(f"{url} {type(url)}")


if __name__ == "__main__":
    pydantic_typer.run(main)
