import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import extractive_answer, retrieve  # noqa: E402
from evaluate import CASES  # noqa: E402


class RetrievalTest(unittest.TestCase):
    def test_expected_top_document(self):
        for question, expected in CASES:
            with self.subTest(question=question):
                _, result = retrieve(question, limit=1)[0]
                self.assertEqual(result.source, expected)

    def test_unsupported_question_does_not_invent_answer(self):
        results = retrieve("What is the office parking policy?")
        self.assertEqual(results, [])
        answer = extractive_answer("What is the office parking policy?", results)
        self.assertEqual(answer, "The prototype did not find enough support to answer.")


if __name__ == "__main__":
    unittest.main()
