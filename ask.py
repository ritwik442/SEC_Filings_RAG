
import sys
from store import VectorStore
from rag import answer_question

store = VectorStore.load()
question = " ".join(sys.argv[1:]) or "What was the IPO offer price per share?"

answer, hits = answer_question(question, store)
print(f"\nQ: {question}\n")
print(f"A: {answer}\n")
print("Sources:")
for rec, score in hits:
    print(f"  [{score:.3f}] {rec['company']} {rec['filing_type']} #{rec['chunk_index']}")