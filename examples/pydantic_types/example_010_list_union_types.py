import typer

import pydantic_typer


def main(value: list[bool | int | float | str] = [True]):
    for val in value:
        typer.echo(f"{val} {type(val)}")


if __name__ == "__main__":
    pydantic_typer.run(main)
