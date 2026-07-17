#!/usr/bin/env python3

import argparse
import re
from pathlib import Path

from datamodel_code_generator import (
    GenerateConfig,
    InputFileType,
    generate,
)


INPUT_BASE_DIR = Path("/beacon/custom_schemas/json")
OUTPUT_BASE_DIR = Path(
    "/beacon/custom_schemas/output_schemas"
)


def valid_output_file(value: str) -> str:
    """
    Validate that the output filename is a valid Python filename.
    Allowed characters: letters, numbers, underscores.
    Must end with .py.
    """
    path = Path(value)

    if path.suffix != ".py":
        raise argparse.ArgumentTypeError(
            "Output file must have a .py extension"
        )

    if not re.fullmatch(r"[A-Za-z0-9_]+\.py", path.name):
        raise argparse.ArgumentTypeError(
            "Output filename can only contain letters, numbers, and underscores"
        )

    return value


def main():
    parser = argparse.ArgumentParser(
        description="Generate Pydantic models from a JSON Schema"
    )

    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="JSON Schema filename",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=valid_output_file,
        default="models.py",
        help="Generated Python filename",
    )

    parser.add_argument(
        "-e",
        "--entry_type",
        help="Name of the entry type used for naming the generated class",
    )

    args = parser.parse_args()

    input_path = INPUT_BASE_DIR / args.input
    output_path = OUTPUT_BASE_DIR / args.output

    if not input_path.exists():
        raise FileNotFoundError(
            f"Schema file not found: {input_path}"
        )

    print(f"Input schema: {input_path}")
    print(f"Output file:  {output_path}")

    config = GenerateConfig(
        input_file_type=InputFileType.JsonSchema,
        output=output_path,
        class_name=args.entry_type
    )

    generate(
        input_=input_path,
        config=config,
    )


if __name__ == "__main__":
    main()