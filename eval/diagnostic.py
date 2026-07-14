from vectorstore import VectorStore
store = VectorStore.load()
from collections import Counter
print(Counter(r["company"] for r in store.records))