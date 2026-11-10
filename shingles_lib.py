# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 22:32:12 2026

@author: jonas
"""

"""Exercise 1a

Module for text tokenization, k-shingle generation, and multiset similarity.

This module provides utility functions to extract k-shingles from token sequences
and to calculate the Jaccard similarity index between multisets.
"""

from collections import Counter
import re
from typing import List, Sequence, Tuple, Union


def clean_and_tokenize(text: str, remove_punctuation: bool = False) -> List[str]:
    """Tokenizes text into words separated by whitespace.

    Args:
        text: Input text string.
        remove_punctuation: If True, strips punctuation characters from tokens.

    Returns:
        A list of string tokens.
    """
    if remove_punctuation:
        text = re.sub(r"[^\w\s]", "", text)
    return text.split()


def shingles(t: Sequence[str], k: int) -> Counter:
    """Generates a multiset of k-shingles from a list of tokens.

    Args:
        t: Sequence of string tokens.
        k: Natural number specifying the shingle size (k-gram length).

    Returns:
        A Counter mapping each k-shingle (represented as a tuple of tokens)
        to its frequency count.

    Raises:
        TypeError: If k is not an integer or t is not a sequence.
        ValueError: If k <= 0 or if the sequence t has fewer than k tokens.
    """
    if not isinstance(k, int):
        raise TypeError(f"Shingle size 'k' must be an integer, got {type(k).__name__}.")
    if k <= 0:
        raise ValueError(f"Shingle size 'k' must be a positive integer, got {k}.")
    if len(t) < k:
        raise ValueError(f"Token list length ({len(t)}) is smaller than shingle size k ({k}).")

    shingle_list: List[Tuple[str, ...]] = [
        tuple(t[i : i + k]) for i in range(len(t) - k + 1)
    ]
    return Counter(shingle_list)


def jaccard_similarity(bag1: Counter, bag2: Counter) -> float:
    """Calculates the Jaccard similarity index for two multisets (bags).

    Definition used:
        J(A, B) = |A ∩ B| / |A ∪ B|
        where |A ∩ B| = sum(min(count_A(x), count_B(x)))
        and |A ∪ B| = sum(max(count_A(x), count_B(x)))

    Args:
        bag1: Counter representing the first multiset.
        bag2: Counter representing the second multiset.

    Returns:
        Jaccard similarity coefficient as a float in the range [0.0, 1.0].

    Raises:
        ValueError: If both multisets are empty.
    """
    if not bag1 and not bag2:
        raise ValueError("Cannot compute similarity for two empty multisets.")

    all_keys = set(bag1.keys()).union(set(bag2.keys()))
    intersection_count = sum(min(bag1[k], bag2[k]) for k in all_keys)
    union_count = sum(max(bag1[k], bag2[k]) for k in all_keys)

    if union_count == 0:
        return 0.0

    return intersection_count / union_count