from vectorstore import VectorStore
from retrieve import retrieve

store = VectorStore.load()
print(f"Loaded {len(store)} chunks\n")

questions = [
    "What was the IPO offer price per share?",
    "What are the main risk factors the company disclosed?",
    "How much revenue did the company generate?",
]

for q in questions:
    print(f"Q: {q}")
    for rec, score in retrieve(q, store, k=3):
        tag = f"{rec['company']} {rec['filing_type']} #{rec['chunk_index']}"
        print(f"  [{score:.3f}] ({tag}) {rec['text'][:110]}...")
    print()