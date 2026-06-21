

from dotenv import load_dotenv
from embed import embed_texts
from store import VectorStore

load_dotenv()


def retrieve(question: str, store: VectorStore, k: int = 5, company: str = None):

    
    q_emb = embed_texts([question], verbose=False)[0]

    return store.search(q_emb, k=k, company=company)