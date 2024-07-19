# noqa: INP001
from pathlib import Path


def main():
    readme_template = Path("docs/README.template.md")
    readme_output = Path("README.md")
    examples_dir = Path("examples")

    example_paths = {path.stem: path.name for path in examples_dir.glob("example_*.py")}

    with readme_template.open() as file:
        readme_content = file.read()

    examples = {}
    for placeholder, example_file in example_paths.items():
        with (examples_dir / example_file).open() as f:
            example_content = f.read()
            examples[placeholder] = f"```python\n{example_content}```"

    readme_content = readme_content.format(**examples)

    with readme_output.open("w") as file:
        file.write(readme_content)


if __name__ == "__main__":
    main()
