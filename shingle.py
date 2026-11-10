# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 22:37:53 2026

@author: jonas
"""
"""CLI tool to find the n most common k-shingles from standard input."""

import argparse
import sys
from shingles_lib import clean_and_tokenize, shingles


def parse_args() -> argparse.Namespace:
    """Parses command-line arguments.

    Returns:
        Parsed arguments namespace containing 'k' and 'n'.
    """
    parser = argparse.ArgumentParser(
        description="Print the n most common k-shingles from multiline text input."
    )
    parser.add_argument(
        "-k", type=int, required=True, help="Size of the shingle (positive integer)."
    )
    parser.add_argument(
        "-n", type=int, required=True, help="Number of most frequent shingles to output."
    )
    return parser.parse_args()


def read_stdin() -> str:
    """Reads multiline text from standard input until EOF is reached.

    Returns:
        Full input text concatenated into a single string.
    """
    lines = []
    while True:
        try:
            line = input()
            lines.append(line)
        except EOFError:
            break
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    raw_text = read_stdin()
    tokens = clean_and_tokenize(raw_text)

    if not tokens:
        print("Error: Input text contains no tokens.", file=sys.stderr)
        sys.exit(1)

    try:
        shingle_counts = shingles(tokens, args.k)
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)

    most_common = shingle_counts.most_common(args.n)
    for shingle, count in most_common:
        shingle_str = " ".join(shingle)
        print(f"{count}\t'{shingle_str}'")


if __name__ == "__main__":
    main()