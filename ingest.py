# ingest.py
from pathlib import Path
from dotenv import load_dotenv

from chunk import chunk_text
from embed import embed_texts
from vectorstore import VectorStore

load_dotenv()
DATA_DIR = Path("data")

def ingest_filing(company: str, filing_type: str, store: VectorStore):
    """Read one saved filing, chunk + embed, add to store with metadata."""
    path = DATA_DIR / f"{company}_{filing_type}.txt"
    text = path.read_text(encoding="utf-8")

    chunks = chunk_text(text, chunk_size=300, overlap=50)
    print(f"{company} {filing_type}: {len(chunks)} chunks")

    embeddings = embed_texts(chunks)
    records = [
        {"text": chunk, "company": company,
         "filing_type": filing_type, "chunk_index": i}
        for i, chunk in enumerate(chunks)
    ]
    store.add(records, embeddings)


if __name__ == "__main__":
    store = VectorStore()
    for path in sorted(DATA_DIR.glob("*_*.txt")):
        if path.name == "company_tickers.json":
            continue
        stem = path.stem                        
        company, _, filing_type = stem.partition("_")
        ingest_filing(company, filing_type, store)
    store.save()