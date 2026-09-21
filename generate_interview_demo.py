#!/usr/bin/env python3
"""Generate a self-contained HTML demonstration from actual retrieval results."""

from __future__ import annotations

from html import escape
from pathlib import Path

from app import grounded_prompt, retrieve


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "interview_demo.html"

QUESTIONS = [
    "When should an underwriter escalate a referral?",
    "How are reserves reviewed?",
    "How should treaty ambiguities be handled?",
    "Who can access personal or medical information?",
]


def result_block(question: str) -> str:
    results = retrieve(question, limit=3)
    top_score, top_chunk = results[0]
    ranking = "".join(
        f"""
        <li>
          <div class="rank-head"><code>{escape(chunk.citation)}</code><span>{score:.3f}</span></div>
          <div class="bar"><span style="width:{max(4, score / max(top_score, 0.001) * 100):.1f}%"></span></div>
        </li>
        """
        for score, chunk in results
    )
    prompt = grounded_prompt(question, results)
    return f"""
    <section class="example">
      <p class="eyebrow">Question</p>
      <h2>{escape(question)}</h2>
      <div class="answer">
        <p class="eyebrow">Top retrieved passage</p>
        <p>{escape(top_chunk.text)}</p>
        <code>{escape(top_chunk.citation)}</code>
      </div>
      <div class="ranking">
        <p class="eyebrow">Top three ranked chunks</p>
        <ol>{ranking}</ol>
      </div>
      <details>
        <summary>Show the grounded prompt built for a future LLM step</summary>
        <pre>{escape(prompt)}</pre>
      </details>
    </section>
    """


def main() -> None:
    examples = "".join(result_block(question) for question in QUESTIONS)
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Reinsurance document retrieval prototype</title>
<style>
  :root {{ color-scheme: light; --navy:#17324d; --blue:#2e638b; --ink:#20252b; --muted:#65717c; --line:#d7e0e7; --soft:#f3f7fa; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font-family:Arial,Helvetica,sans-serif; color:var(--ink); background:#fff; line-height:1.55; }}
  main {{ max-width:960px; margin:0 auto; padding:48px 24px 64px; }}
  h1 {{ color:var(--navy); font-size:34px; margin:0 0 8px; }}
  h2 {{ color:var(--navy); font-size:20px; margin:0 0 18px; }}
  .subtitle {{ color:var(--muted); margin:0 0 24px; }}
  .status {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; margin:28px 0 36px; }}
  .status div {{ background:var(--soft); padding:16px; border-radius:8px; }}
  .status strong {{ display:block; color:var(--navy); font-size:18px; }}
  .status span {{ color:var(--muted); font-size:14px; }}
  .example {{ padding:30px 0; border-top:1px solid var(--line); }}
  .eyebrow {{ color:var(--blue); text-transform:uppercase; letter-spacing:.08em; font-size:12px; font-weight:700; margin:0 0 6px; }}
  .answer {{ background:var(--soft); padding:18px; border-radius:8px; margin-bottom:18px; }}
  .answer p:not(.eyebrow) {{ margin:0 0 10px; }}
  code {{ color:var(--navy); font-size:13px; }}
  ol {{ margin:0; padding:0; list-style:none; }}
  li {{ margin:10px 0 14px; }}
  .rank-head {{ display:flex; justify-content:space-between; gap:16px; }}
  .bar {{ height:7px; background:#e9eef2; border-radius:5px; margin-top:6px; overflow:hidden; }}
  .bar span {{ display:block; height:100%; background:var(--blue); }}
  details {{ margin-top:18px; }}
  summary {{ color:var(--blue); cursor:pointer; }}
  pre {{ white-space:pre-wrap; background:#111a22; color:#edf5fb; padding:16px; border-radius:8px; overflow-wrap:anywhere; font-size:12px; }}
  .caveat {{ border-left:4px solid var(--blue); padding:4px 0 4px 16px; margin:32px 0 0; color:var(--muted); }}
  @media (max-width:650px) {{ .status {{ grid-template-columns:1fr; }} h1 {{ font-size:28px; }} }}
</style>
</head>
<body>
<main>
  <h1>Reinsurance document retrieval prototype</h1>
  <p class="subtitle">A small Python demonstration of the retrieval stage that could feed a future approved language model.</p>
  <div class="status">
    <div><strong>4</strong><span>synthetic documents</span></div>
    <div><strong>12/12</strong><span>top-document results on the hand-written smoke test</span></div>
    <div><strong>No LLM call</strong><span>retrieval and prompt construction only</span></div>
  </div>
  {examples}
  <p class="caveat">This is a learning prototype, not an underwriting or claims tool. The smoke test is small and uses synthetic data. It does not prove answer correctness, generalisation, privacy, or production readiness.</p>
</main>
</body>
</html>
"""
    OUTPUT.write_text(html)
    print(OUTPUT)


if __name__ == "__main__":
    main()

