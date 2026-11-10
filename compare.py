# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 22:38:33 2026

@author: jonas
"""

"""CLI tool to compare two text files using Jaccard similarity of k-shingles."""

import argparse
from pathlib import Path
import sys
from shingles_lib import clean_and_tokenize, jaccard_similarity, shingles


def parse_args() -> argparse.Namespace:
    """Parses command line options for file comparison.

    Returns:
        Parsed arguments with parameters: query, target, k, remove_punctuation.
    """
    parser = argparse.ArgumentParser(
        description="Calculate Jaccard similarity between two text files based on k-shingles."
    )
    parser.add_argument(
        "--query", type=Path, required=True, help="Path to the query text file."
    )
    parser.add_argument(
        "--target", type=Path, required=True, help="Path to the target text file."
    )
    parser.add_argument(
        "-k", type=int, default=2, help="Size of the k-shingle (default: 2)."
    )
    parser.add_argument(
        "--remove_punctuation",
        action="store_true",
        help="Enable removal of punctuation marks before tokenization.",
    )
    return parser.parse_args()


def load_and_tokenize(path: Path, remove_punct: bool) -> list:
    """Loads a text file and tokenizes its contents.

    Args:
        path: Path to the text file.
        remove_punct: Whether to strip punctuation.

    Returns:
        List of tokens.
    """
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    content = path.read_text(encoding="utf-8")
    return clean_and_tokenize(content, remove_punctuation=remove_punct)


def main() -> None:
    args = parse_args()

    try:
        tokens_query = load_and_tokenize(args.query, args.remove_punctuation)
        tokens_target = load_and_tokenize(args.target, args.remove_punctuation)

        shingles_query = shingles(tokens_query, args.k)
        shingles_target = shingles(tokens_target, args.k)

        similarity = jaccard_similarity(shingles_query, shingles_target)
        print(f"Jaccard Similarity (k={args.k}): {similarity:.4f}")

    except (FileNotFoundError, ValueError, TypeError) as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()