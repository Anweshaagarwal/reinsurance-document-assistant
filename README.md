# Reinsurance document retrieval prototype

This is a small hobby prototype for source-grounded search over a synthetic reinsurance knowledge base. It attempts to retrieve relevant document sections, produces an extractive answer, builds a prompt for a future approved language-model step, and preserves source references.

The documents are synthetic and exist only to demonstrate the workflow. The prototype is not an underwriting or claims tool.

## What it demonstrates

- Paragraph chunking and tokenisation in Python
- TF-IDF retrieval without external packages
- Source citations for every retrieved passage
- Grounded prompt construction for a future language-model step
- A small evaluation set for top-document retrieval
- An explicit domain gate that rejects unrelated questions before retrieval
- Responsible-use requirements covering privacy, unsupported answers, and human review

The current version retrieves the expected source document for all 12 questions in the hand-written test set. This result applies only to the four-document synthetic corpus and is not a measure of production performance.

The regression suite also checks that an unrelated office-policy question returns no answer. The domain gate is a small prototype control, not a substitute for production intent classification.

## Run it

```bash
python3 app.py "What information should an underwriter check before accepting a risk?"
python3 evaluate.py
```

Generate a browser-ready interview demonstration from the project's actual retrieval results:

```bash
python3 generate_interview_demo.py
open interview_demo.html
```

## Current limits

- The knowledge base is small and synthetic.
- Retrieval uses lexical similarity, so it can miss paraphrases.
- The answer is extractive. The code builds a grounded language-model prompt but does not send data to an external service.
- The evaluation measures top-document retrieval, not answer faithfulness or business correctness.

## Responsible-use notes

Production use would require approved enterprise data, access controls, encryption, retention rules, personal-data redaction, model and retrieval evaluation, audit logs, and mandatory expert review for underwriting or claims decisions.
