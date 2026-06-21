import numpy as np
from openai import OpenAI

EMBED_MODEL = "text-embedding-3-small"
client = OpenAI()


def embed_texts(texts, batch_size=100, verbose=True):
    all_vectors = []                                              
    for start in range(0, len(texts), batch_size):
        batch = texts[start:start + batch_size]
        resp = client.embeddings.create(model=EMBED_MODEL, input=batch)
        ordered = sorted(resp.data, key=lambda d: d.index)
        all_vectors.extend(d.embedding for d in ordered)
        if verbose:
            print(f"  embedded {min(start + batch_size, len(texts))}/{len(texts)}")
    return np.array(all_vectors, dtype=np.float32)