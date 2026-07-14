
import json
from openai import OpenAI
from dataset import EvalItem   # adjust import to your layout

client = OpenAI()

GEN_PROMPT = """You are creating evaluation questions for a system that answers \
questions about SEC filings. Given the filing excerpt below, write {n} factual \
questions whose answers are EXPLICITLY stated in the text.

For each, return a JSON object with:
- "question": a specific, unambiguous question
- "ground_truth": the exact answer, quoting figures verbatim from the text
- "expected_source_substring": a short exact string from the text that must \
appear in a retrieved chunk

Return ONLY a JSON array. Excerpt:
---
{excerpt}
---"""


def generate_candidates(excerpt: str, company: str, filing_type: str, n: int = 5):
    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.3,          
        messages=[{"role": "user",
                   "content": GEN_PROMPT.format(n=n, excerpt=excerpt[:6000])}],
    )
    raw = resp.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    drafts = json.loads(raw)

    items = []
    for i, d in enumerate(drafts):
        items.append(EvalItem(
            id=f"gen-{company}-{i}",
            question=d["question"],
            ground_truth=d["ground_truth"],
            category="exact_figure",
            company=company,
            filing_type=filing_type,
            expected_source_substring=d.get("expected_source_substring"),
            source="generated",      
        ))
    return items