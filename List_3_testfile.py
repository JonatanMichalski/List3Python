# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 19:29:19 2026

@author: jonas
"""


"""Unit tests for List 3 tasks."""

import unittest
from shingles_lib import clean_and_tokenize, jaccard_similarity, shingles
from fasta import ProteinSequence, fasta_id_to_dict, fasta_to_prot_seq


class TestShinglesLib(unittest.TestCase):
    """Unit tests for shingles_lib module functions."""

    def test_clean_and_tokenize(self) -> None:
        text = "Hello, world! This is a test."
        tokens_with_punct = clean_and_tokenize(text, remove_punctuation=False)
        self.assertEqual(tokens_with_punct, ["Hello,", "world!", "This", "is", "a", "test."])

        tokens_no_punct = clean_and_tokenize(text, remove_punctuation=True)
        self.assertEqual(tokens_no_punct, ["Hello", "world", "This", "is", "a", "test"])

    def test_shingles_valid_input(self) -> None:
        tokens = ["a", "b", "c", "a", "b"]
        # 2-shingles: ('a', 'b'): 2, ('b', 'c'): 1, ('c', 'a'): 1
        res = shingles(tokens, k=2)
        self.assertEqual(res[("a", "b")], 2)
        self.assertEqual(res[("b", "c")], 1)
        self.assertEqual(res[("c", "a")], 1)
        self.assertEqual(sum(res.values()), 4)

    def test_shingles_exceptions(self) -> None:
        tokens = ["word1", "word2"]

        # Invalid k type
        with self.assertRaises(TypeError):
            shingles(tokens, k=2.5)  # type: ignore

        # Invalid k value
        with self.assertRaises(ValueError):
            shingles(tokens, k=0)

        # Sequence shorter than k
        with self.assertRaises(ValueError):
            shingles(tokens, k=3)

    def test_jaccard_similarity(self) -> None:
        tokens1 = ["the", "quick", "brown", "fox"]
        tokens2 = ["the", "quick", "red", "fox"]

        bag1 = shingles(tokens1, k=2)
        bag2 = shingles(tokens2, k=2)

        # bag1: ('the', 'quick'), ('quick', 'brown'), ('brown', 'fox') -> 3
        # bag2: ('the', 'quick'), ('quick', 'red'), ('red', 'fox') -> 3
        # Intersection: ('the', 'quick') -> count 1
        # Union size: 5
        # Similarity: 1 / 5 = 0.2
        sim = jaccard_similarity(bag1, bag2)
        self.assertAlmostEqual(sim, 0.2)

    def test_jaccard_similarity_identical(self) -> None:
        tokens = ["alpha", "beta", "gamma"]
        bag = shingles(tokens, k=2)
        self.assertEqual(jaccard_similarity(bag, bag), 1.0)

    def test_jaccard_similarity_empty_error(self) -> None:
        from collections import Counter
        with self.assertRaises(ValueError):
            jaccard_similarity(Counter(), Counter())


class TestFastaModule(unittest.TestCase):
    """Unit tests for fasta module classes and functions."""

    def test_protein_sequence_instantiation(self) -> None:
        protein = ProteinSequence(
            accession="P02768",
            full_name="Serum albumin",
            organism="Homo sapiens",
            sequence="MKWVTFISLLFLFSSAYSRGVFRR",
        )
        self.assertEqual(protein.accession, "P02768")
        self.assertEqual(protein.organism, "Homo sapiens")

        d = protein.to_dict()
        self.assertEqual(d["accession"], "P02768")
        self.assertIn("sequence", d)

    def test_protein_sequence_invalid(self) -> None:
        # Empty accession or sequence should raise ValueError
        with self.assertRaises(ValueError):
            ProteinSequence("", "Full Name", "Organism", "SEQ")

        with self.assertRaises(ValueError):
            ProteinSequence("P02768", "Full Name", "Organism", "")

    def test_fasta_id_to_dict_uniprot_header(self) -> None:
        header = ">sp|P02768|ALBU_HUMAN Serum albumin OS=Homo sapiens OX=9606 GN=ALB PE=1 SV=2"
        res = fasta_id_to_dict(header)

        self.assertEqual(res["accession"], "P02768")
        self.assertEqual(res["full_name"], "Serum albumin")
        self.assertEqual(res["organism"], "Homo sapiens")

    def test_fasta_to_prot_seq(self) -> None:
        sample_fasta = (
            ">sp|P02768|ALBU_HUMAN Serum albumin OS=Homo sapiens\n"
            "MKWVTFISLLFLFSSAYSRGVFRR\n"
            "DAHKSEVAHRFKDLGEENFKALVL\n"
            ">sp|P02769|ALBU_BOVIN Serum albumin OS=Bos taurus\n"
            "MKWVTFISLLLLFSSAYSRGVFRR\n"
        )
        proteins = fasta_to_prot_seq(sample_fasta)

        self.assertEqual(len(proteins), 2)
        self.assertEqual(proteins[0].accession, "P02768")
        self.assertEqual(proteins[0].organism, "Homo sapiens")
        self.assertTrue(proteins[0].sequence.startswith("MKWVTFISLLFLFSSAYSRGVFRRDAHKSEVAHRFKDLGEENFKALVL"))

        self.assertEqual(proteins[1].accession, "P02769")
        self.assertEqual(proteins[1].organism, "Bos taurus")


if __name__ == "__main__":
    unittest.main()