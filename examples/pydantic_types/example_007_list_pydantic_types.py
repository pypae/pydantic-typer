from typing import List

import typer
from pydantic import AnyHttpUrl

import pydantic_typer


def main(urls: List[AnyHttpUrl] = typer.Option([], "--url")):
    typer.echo(f"urls: {urls}")


if __name__ == "__main__":
    pydantic_typer.run(main)
