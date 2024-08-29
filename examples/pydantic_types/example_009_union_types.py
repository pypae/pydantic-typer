import typer

import pydantic_typer


def main(value: bool | float | int | str = 1):
    typer.echo(f"{value} {type(value)}")


if __name__ == "__main__":
    pydantic_typer.run(main)
