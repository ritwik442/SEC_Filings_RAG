
from dotenv import load_dotenv
from openai import OpenAI

from retrieve import retrieve
from store import VectorStore

load_dotenv()
client = OpenAI()

CHAT_MODEL = "gpt-4.1-mini"  

SYSTEM_PROMPT = """You are a financial analyst assistant that answers questions about SEC filings.

Rules:
- Answer ONLY using the provided context. Do not use any outside knowledge.
- If the answer is not in the context, say "I couldn't find that in the filing." Never guess.
- When citing figures, quote the exact numbers from the context.
- Be concise and factual. No speculation."""


def build_context(hits):
    
    blocks = []
    for rec, score in hits:
        tag = f"[{rec['company']} {rec['filing_type']} chunk {rec['chunk_index']}]"
        blocks.append(f"{tag}\n{rec['text']}")
    return "\n\n---\n\n".join(blocks)


def answer_question(question: str, store: VectorStore, k: int = 6, company: str = None):
    hits = retrieve(question, store, k=k, company=company)
    context = build_context(hits)

    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        temperature=0,  
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
    )
    return resp.choices[0].message.content, hits