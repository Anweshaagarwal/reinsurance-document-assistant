#!/usr/bin/env python3
"""Evaluate top-document retrieval on a small hand-written question set."""

from app import retrieve


CASES = [
    ("What details are needed before underwriting a property risk?", "underwriting_guidelines.md"),
    ("When should an underwriter escalate a referral?", "underwriting_guidelines.md"),
    ("How should exclusions be recorded?", "underwriting_guidelines.md"),
    ("What happens when a claim notification arrives?", "claims_triage.md"),
    ("Which claims require specialist review?", "claims_triage.md"),
    ("How are reserves reviewed?", "claims_triage.md"),
    ("What should be checked in a treaty wording?", "treaty_review.md"),
    ("How should treaty ambiguities be handled?", "treaty_review.md"),
    ("Who can access personal or medical information?", "data_governance.md"),
    ("What should the system do when evidence is insufficient?", "data_governance.md"),
    ("Can an AI system make an underwriting decision by itself?", "data_governance.md"),
    ("Why should model activity be logged?", "data_governance.md"),
]


def main() -> None:
    correct = 0
    for question, expected in CASES:
        _, top_chunk = retrieve(question, limit=1)[0]
        passed = top_chunk.source == expected
        correct += int(passed)
        status = "PASS" if passed else "FAIL"
        print(f"{status} | expected={expected} | got={top_chunk.source} | {question}")
    print(f"\nTop-document retrieval accuracy: {correct}/{len(CASES)} ({correct / len(CASES):.0%})")


if __name__ == "__main__":
    main()

