# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 22:39:27 2026

@author: jonas
"""

"""FASTA sequence parser and UniProt API integrator.

Supports parsing FASTA files, querying UniProt REST API, and exporting protein
metadata/sequences to Pickle, JSON, and XML formats.
"""

import argparse
import json
import pickle
import re

from typing import Dict, List, Optional
import xml.etree.ElementTree as ET
import requests


class ProteinSequence:
    """Represents a protein sequence entry from UniProt.

    Attributes:
        accession: UniProt primary accession identifier.
        full_name: Full descriptive name of the protein.
        organism: Scientific name of the source organism.
        sequence: Amino acid sequence string.
    """

    def __init__(
        self, accession: str, full_name: str, organism: str, sequence: str
    ) -> None:
        if not accession or not sequence:
            raise ValueError("Accession and sequence cannot be empty.")
        self.accession = accession
        self.full_name = full_name
        self.organism = organism
        self.sequence = sequence

    def to_dict(self) -> Dict[str, str]:
        """Converts object attributes to a dictionary representation."""
        return {
            "accession": self.accession,
            "full_name": self.full_name,
            "organism": self.organism,
            "sequence": self.sequence,
        }

    def __repr__(self) -> str:
        return f"ProteinSequence(accession='{self.accession}', organism='{self.organism}')"


def fasta_id_to_dict(identifier: str) -> Dict[str, str]:
    """Parses a UniProt FASTA header line to extract metadata.

    Example identifier:
        >sp|P02768|ALBU_HUMAN Serum albumin OS=Homo sapiens OX=9606 GN=ALB PE=1 SV=2

    Args:
        identifier: Header line string from a FASTA entry.

    Returns:
        Dictionary containing 'accession', 'full_name', and 'organism'.

    Raises:
        ValueError: If accession format cannot be parsed.
    """
    header = identifier.lstrip(">").strip()

    # Match UniProt format |accession| entry_name full_name OS=organism
    acc_match = re.search(r"\|([A-Z0-9]{6,10})\|", header)
    accession = acc_match.group(1) if acc_match else header.split()[0]

    org_match = re.search(r"OS=(.*?)(?=\s[A-Z]{2}=|$)", header)
    organism = org_match.group(1).strip() if org_match else "Unknown"

    # Extract full name between sequence ID and OS=
    name_match = re.search(r"\|[A-Z0-9_]+\s+(.*?)\s+OS=", header)
    if name_match:
        full_name = name_match.group(1).strip()
    else:
        full_name = header

    return {"accession": accession, "full_name": full_name, "organism": organism}


def fasta_to_prot_seq(fasta_content: str) -> List[ProteinSequence]:
    """Parses FASTA format string content into a list of ProteinSequence objects.

    Args:
        fasta_content: Raw text content in FASTA format.

    Returns:
        List of ProteinSequence instances.
    """
    entries: List[ProteinSequence] = []
    lines = fasta_content.strip().splitlines()

    current_header: Optional[str] = None
    current_seq_lines: List[str] = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if current_header and current_seq_lines:
                meta = fasta_id_to_dict(current_header)
                seq = "".join(current_seq_lines)
                entries.append(ProteinSequence(sequence=seq, **meta))
                current_seq_lines = []
            current_header = line
        else:
            current_seq_lines.append(line)

    if current_header and current_seq_lines:
        meta = fasta_id_to_dict(current_header)
        seq = "".join(current_seq_lines)
        entries.append(ProteinSequence(sequence=seq, **meta))

    return entries


def fetch_uniprot_fasta(protein_name: str, max_seq: int) -> str:
    """Fetches protein sequences in FASTA format using UniProt REST API.

    Args:
        protein_name: Name of the protein query (e.g., 'albumin').
        max_seq: Maximum number of records to retrieve.

    Returns:
        Raw FASTA string retrieved from UniProt.

    Raises:
        requests.HTTPError: If the HTTP request fails.
    """
    url = "https://rest.uniprot.org/uniprotkb/search"
    params = {
        "query": protein_name,
        "format": "fasta",
        "size": max_seq,
    }
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    return response.text


def export_data(
    proteins: List[ProteinSequence],
    json_path: Optional[str] = None,
    pickle_path: Optional[str] = None,
    xml_path: Optional[str] = None,
) -> None:
    """Exports protein sequences to JSON, Pickle, or XML files.

    Args:
        proteins: List of ProteinSequence objects.
        json_path: Destination path for JSON export.
        pickle_path: Destination path for Pickle export.
        xml_path: Destination path for XML export.
    """
    data = [p.to_dict() for p in proteins]

    if json_path:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Exported JSON to {json_path}")

    if pickle_path:
        with open(pickle_path, "wb") as f:
            pickle.dump(proteins, f)
        print(f"Exported Pickle to {pickle_path}")

    if xml_path:
        root = ET.Element("Proteins")
        for p in proteins:
            entry = ET.SubElement(root, "ProteinSequence")
            ET.SubElement(entry, "accession").text = p.accession
            ET.SubElement(entry, "full_name").text = p.full_name
            ET.SubElement(entry, "organism").text = p.organism
            ET.SubElement(entry, "sequence").text = p.sequence
        tree = ET.ElementTree(root)
        tree.write(xml_path, encoding="utf-8", xml_declaration=True)
        print(f"Exported XML to {xml_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse and export FASTA sequence data.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--fasta", type=str, help="Input FASTA file path.")
    group.add_argument("--protein", type=str, help="Protein name to search via UniProt API.")

    parser.add_argument("--max_seq", type=int, default=5, help="Max sequences to download from API.")
    parser.add_argument("--json", type=str, help="Output JSON file path.")
    parser.add_argument("--pickle", type=str, help="Output Pickle file path.")
    parser.add_argument("--xml", type=str, help="Output XML file path.")

    args = parser.parse_args()

    if args.fasta:
        with open(args.fasta, "r", encoding="utf-8") as f:
            fasta_raw = f.read()
    else:
        print(f"Fetching up to {args.max_seq} sequences for '{args.protein}' from UniProt...")
        fasta_raw = fetch_uniprot_fasta(args.protein, args.max_seq)

    protein_objects = fasta_to_prot_seq(fasta_raw)
    print(f"Successfully processed {len(protein_objects)} sequences.")

    export_data(
        protein_objects,
        json_path=args.json,
        pickle_path=args.pickle,
        xml_path=args.xml,
    )


if __name__ == "__main__":
    main()