#!/usr/bin/env python3
"""Small source-grounded retrieval prototype for synthetic reinsurance documents."""

from __future__ import annotations

import argparse
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
TOKEN_RE = re.compile(r"[a-z0-9]+")
DOMAIN_TERMS = {
    "underwrit", "underwriter", "risk", "claim", "notification", "treaty",
    "reinsurance", "coverag", "insured", "insurer", "reserv", "evidence",
    "exclusion", "referral", "authority", "personal", "medical", "model",
    "privacy", "retention", "audit",
}


@dataclass(frozen=True)
class Chunk:
    source: str
    index: int
    text: str

    @property
    def citation(self) -> str:
        return f"[{self.source}#chunk-{self.index}]"


def _stem(term: str) -> str:
    for suffix in ("ing", "ed", "es", "s"):
        if term.endswith(suffix) and len(term) > len(suffix) + 3:
            return term[: -len(suffix)]
    return term


def tokens(text: str) -> list[str]:
    return [_stem(term) for term in TOKEN_RE.findall(text.lower())]


def load_chunks() -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in sorted(DOCS.glob("*.md")):
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", path.read_text())]
        body = [p for p in paragraphs if p and not p.startswith("#")]
        for index, paragraph in enumerate(body, 1):
            chunks.append(Chunk(path.name, index, paragraph.replace("\n", " ")))
    return chunks


def idf_table(chunks: list[Chunk]) -> dict[str, float]:
    document_frequency: Counter[str] = Counter()
    for chunk in chunks:
        document_frequency.update(set(tokens(chunk.text)))
    size = len(chunks)
    return {
        term: math.log((1 + size) / (1 + frequency)) + 1
        for term, frequency in document_frequency.items()
    }


def vector(text: str, idf: dict[str, float]) -> dict[str, float]:
    counts = Counter(tokens(text))
    return {term: count * idf.get(term, 0.0) for term, count in counts.items()}


def cosine(left: dict[str, float], right: dict[str, float]) -> float:
    numerator = sum(value * right.get(term, 0.0) for term, value in left.items())
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if not left_norm or not right_norm:
        return 0.0
    return numerator / (left_norm * right_norm)


def retrieve(query: str, limit: int = 3) -> list[tuple[float, Chunk]]:
    if not set(tokens(query)).intersection(DOMAIN_TERMS):
        return []
    chunks = load_chunks()
    idf = idf_table(chunks)
    query_vector = vector(query, idf)
    scored = [(cosine(query_vector, vector(chunk.text, idf)), chunk) for chunk in chunks]
    return sorted(scored, key=lambda item: item[0], reverse=True)[:limit]


def extractive_answer(query: str, results: list[tuple[float, Chunk]]) -> str:
    if not results:
        return "The prototype did not find enough support to answer."
    query_terms = set(tokens(query))
    candidates: list[tuple[int, str, str]] = []
    for _, chunk in results:
        for sentence in re.split(r"(?<=[.!?])\s+", chunk.text):
            overlap = len(query_terms.intersection(tokens(sentence)))
            candidates.append((overlap, sentence, chunk.citation))
    best = sorted(candidates, key=lambda item: item[0], reverse=True)[:2]
    if not best or best[0][0] == 0:
        return "The prototype did not find enough support to answer."
    return " ".join(f"{sentence} {citation}" for _, sentence, citation in best)


def grounded_prompt(query: str, results: list[tuple[float, Chunk]]) -> str:
    context = "\n\n".join(f"{chunk.citation} {chunk.text}" for _, chunk in results)
    return (
        "Answer the question only from the supplied context. Cite every material claim. "
        "If the context is insufficient, say so. Do not make an underwriting or claims decision.\n\n"
        f"Question: {query}\n\nContext:\n{context}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--show-prompt", action="store_true")
    args = parser.parse_args()
    results = retrieve(args.query)
    print("Answer")
    print(extractive_answer(args.query, results))
    print("\nRetrieved sources")
    if results:
        for score, chunk in results:
            print(f"{score:.3f} {chunk.citation} {chunk.text}")
    else:
        print("No in-domain source was retrieved.")
    if args.show_prompt:
        print("\nGrounded language-model prompt")
        print(grounded_prompt(args.query, results))


if __name__ == "__main__":
    main()
