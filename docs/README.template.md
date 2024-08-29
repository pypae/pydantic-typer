<!---
Do not edit `README.md` manually, instead edit `docs/README.template.md` and run `python docs/scripts/make_docs.py`.
-->

# Pydantic Typer

[![PyPI - Version](https://img.shields.io/pypi/v/pydantic-typer.svg)](https://pypi.org/project/pydantic-typer)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pydantic-typer.svg)](https://pypi.org/project/pydantic-typer)
[![Test Coverage](https://coverage-badge.samuelcolvin.workers.dev/pypae/pydantic-typer.svg)](https://coverage-badge.samuelcolvin.workers.dev/redirect/pypae/pydantic-typer)

[Typer](https://github.com/tiangolo/typer) extension to enable pydantic support

> [!WARNING]  
> This package is still in early development and some things might not work as expected, or change between versions.

---

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Installation

```console
pip install pydantic-typer
```

> [!NOTE]  
> `pydantic-typer` comes with `pydantic` and `typer` as dependencies, so you don't need to install anything else.

## Usage

For general `typer` usage, please refer to the [typer documentation](https://typer.tiangolo.com/).

All the code blocks below can be copied and used directly (they are tested Python files).
To run any of the examples, copy the code to a file `main.py`, and run it:

```console
python main.py
```

### Basic Usage

<table>
<tr>
<td>

:technologist: Simply use `pydantic_typer.run` instead of `typer.run` to enable pydantic support

</td>
</tr>
<tr>
<td>

{pydantic_models/example_001_basic_an}

</td>
</tr>

<tr>
<td>
<details>
  <summary>
    :t-rex: Non-Annotated Version
  </summary>

{pydantic_models/example_001_basic}

</td>
</tr>

<tr>
<td>
<details>
  <summary>
    :computer: Usage
  </summary>

```console
$ # Run the basic example:
$ python main.py
Usage: main.py [OPTIONS] NUM
Try 'main.py --help' for help.
╭─ Error ────────────────────────────────────────────────────────────╮
│ Missing argument 'NUM'.                                            │
╰────────────────────────────────────────────────────────────────────╯

$ # We're missing a required argument, try using --help as suggested:
$ python main.py --help
Usage: main.py [OPTIONS] NUM

╭─ Arguments ────────────────────────────────────────────────────────╮
│ *    num      INTEGER  [default: None] [required]                  │
╰────────────────────────────────────────────────────────────────────╯
╭─ Options ──────────────────────────────────────────────────────────╮
│ *  --user.id          INTEGER  The id of the user. [default: None] │
│                                [required]                          │
│    --user.name        TEXT     The name of the user.               │
│                                [default: Jane Doe]                 │
│    --help                      Show this message and exit.         │
╰────────────────────────────────────────────────────────────────────

$ # Notice the help text for `user.id` and `user.name` are inferred from the `pydantic.Field`.
$ # `user.id` is reqired, because we don't provide a default value for the field.
$ # Now run the example with the required arguments:
$ python main.py 1 --user.id 1
1 <class 'int'>
id=1 name='Jane Doe' <class '__main__.User'>

$ # It worked! You can also experiment with an invalid `user.id`:
$ python main.py 1 --user.id some-string
Usage: example_001_basic.py [OPTIONS] NUM
Try 'example_001_basic.py --help' for help.
╭─ Error ─────────────────────────────────────────────────────────────╮
│ Invalid value for '--user.id': 'some-string' is not a valid integer.│
╰─────────────────────────────────────────────────────────────────────╯
```

</td>
</tr>

</table>

### Usage with nested models

<table>
<tr>
<td>

:technologist: `pydantic_typer.run` also works with nested pydantic models

</td>
</tr>
<tr>
<td>

{pydantic_models/example_002_nested_models}

</td>
</tr>

<tr>
<td>
<details>
  <summary>
    :computer: Usage
  </summary>

```console
$ # Run the nested models example with the required options:
$ python main.py --person.name "Patrick" --person.pet.name "Snoopy" --person.pet.species "Dog"
name='Patrick' age=None pet=Pet(name='Snoopy', species='Dog') <class '__main__.Person'>
```

</td>
</tr>
</table>

### Use `pydantic` models with `typer.Argument`

<table>
<tr>
<td>

:technologist: You can annotate the parameters with `typer.Argument` to make all model fields CLI arguments

</td>
</tr>
<tr>
<td>

{pydantic_models/example_003_annotated_argument}

</td>
</tr>
<tr>
<td>
<details>
  <summary>
    :computer: Usage
  </summary>

```console
$ # Run the example
$ python main.py
Usage: main.py [OPTIONS] _PYDANTIC_USER_ID
                                         _PYDANTIC_USER_NAME
Try 'main.py --help' for help.
╭─ Error ─────────────────────────────────────────────────────────────╮
│ Missing argument '_PYDANTIC_USER_ID'.                               │
╰─────────────────────────────────────────────────────────────────────╯

$ # Notice how _PYDANTIC_USER_ID and _PYDANTIC_USER_NAME are now cli arguments instead of options.
$ # Supply the arguments in the right order:
> python main.py 1 Patrick --num 1
1 <class 'int'>
id=1 name='Patrick' <class '__main__.User'>
```

</details>
</td>
</tr>
<tr>
<td>

<details>
<summary>:bulb: You can also override annotations directly on the pydantic model fields:</summary>

{pydantic_models/example_004_argument_override}

Here, `User` is a `typer.Argument`, but we manually override the fields again:

- We override the `metavar` of to `User.id` be `THE_ID`
- And `User.name` to be a `typer.Option`

</details>
</td>
</tr>
</table>

### Use pydantic models in multiple commands

<table>
<tr>
<td>

:technologist: For larger `typer` apps, you can use `pydantic_typer.Typer` instead of annotating each command function individually to enable pydantic models on all commands

</td>
</tr>
<tr>
<td>

{pydantic_models/example_005_multi_commands}

</td>
</tr>
</table>

### Use pydantic types

<table>
<tr>
<td>

:technologist: You can also annotate arguments with [pydantic types](https://docs.pydantic.dev/latest/concepts/types/) and they will be validated

</td>
</tr>
<tr>
<td>

{pydantic_types/example_006_pydantic_types}

</td>
</tr>
</table>

<table>
<tr>
<td>

:technologist: Pydantic types also work in lists and tuples

</td>
</tr>
<tr>
<td>

{pydantic_types/example_007_list_pydantic_types}

</td>
</tr>
</table>

### Use `Union` types

<table>
<tr>
<td>

:technologist: Thanks to `pydantic.TypeAdapter`, which we use internally, we also support `Union` types

</td>
</tr>
<tr>
<td>

{pydantic_types/example_009_union_types}

</td>
</tr>
<tr>
<td>
<details>
  <summary>
    :computer: Usage
  </summary>

```console
$ # Run the example using a boolean
$ python main.py --value True
True <class 'bool'>

$ # Run the example using an integer
$ python main.py --value 2
2 <class 'int'>

$ # Run the example using a float
$ python main.py --value 2.1
2.1 <class 'float'>

$ # Run the example using a string
$ python main.py --value "Hello World"
Hello World <class 'str'>

$ # Before, we intentionally used 2, when testing the integer
$ # Check what happens if you pass 1
$ python main.py --value 1
True <class 'bool'>

$ # We get back a boolean!
$ # This is because Unions are generally evaluated left to right.
$ # So in this case bool > int > float > str, if parsing is successful.
$ # There are some exceptions, where pydantic tries to be smart, see here for details:
$ # https://docs.pydantic.dev/latest/concepts/unions/#smart-mode
```

</details>
</td>
</tr>

</table>

### Limitations

> [!WARNING]  
> `pydantic-typer` does not yet support sequences of pydantic models: See [this issue](https://github.com/pypae/pydantic-typer/issues/6) for details

> [!WARNING]  
> `pydantic-typer` does not yet support self-referential pydantic models.

> [!WARNING]  
> `pydantic-typer` does not yet support lists with complex sub-types, in particular unions such as `list[str|int]`.

## License

`pydantic-typer` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
