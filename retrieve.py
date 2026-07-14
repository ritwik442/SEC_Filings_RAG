

from dotenv import load_dotenv
from embed import embed_texts
from vectorstore import VectorStore
import re

load_dotenv()

def strip_company_name(question: str, company: str) -> str:
    
    if not company:
        return question
    aliases = {
        "spacex": ["spacex", "space exploration technologies", "spacex's"],
        "apple":  ["apple inc", "apple's", "apple"],
        "nvidia": ["nvidia's", "nvidia"],
        "tesla":  ["tesla's", "tesla"],
        "jpm":    ["jpmorgan chase", "jpmorgan", "jpm"],
    }
    cleaned = question
    for alias in aliases.get(company.lower(), [company]):
        cleaned = re.sub(rf"\b{re.escape(alias)}\b\s*", "", cleaned, flags=re.I)
    return re.sub(r"\s+", " ", cleaned).strip()


def retrieve(question, store, k=5, company=None):

    query_text = strip_company_name(question, company) if company else question
    q_emb = embed_texts([query_text], verbose=False)[0]
    return store.search(q_emb, k=k, company=company)