

import json
from pathlib import Path
import numpy as np


class VectorStore:
    def __init__(self, records=None, embeddings=None):

        self.records = records or []     # list of dicts: text + metadata
        self.embeddings = embeddings     # np.ndarray (n, dim) or None

    def add(self, records: list[dict], embeddings: np.ndarray):
        if len(records) != len(embeddings):
            raise ValueError("records and embeddings must align 1:1")
        self.records.extend(records)
        if self.embeddings is None:
            self.embeddings = embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, embeddings])





    def save(self, path: str = "store"):
        Path(path).mkdir(exist_ok=True)
        np.save(Path(path) / "embeddings.npy", self.embeddings)
        (Path(path) / "records.json").write_text(json.dumps(self.records))
        print(f"Saved {len(self.records)} vectors -> {path}/")

    @classmethod
    def load(cls, path: str = "store"):
        embeddings = np.load(Path(path) / "embeddings.npy")
        records = json.loads((Path(path) / "records.json").read_text())
        return cls(records=records, embeddings=embeddings)
    

    def search(self, query_embedding, k=5, company=None):

        mat = self.embeddings / np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        q = query_embedding / np.linalg.norm(query_embedding)
        sims = mat @ q  



        if company is not None:
            mask = np.array([r["company"] == company for r in self.records])
            sims = np.where(mask, sims, -np.inf)

        k = min(k, len(self.records))
        top_idx = np.argsort(sims)[::-1][:k]      
        return [(self.records[i], float(sims[i]))
                for i in top_idx if np.isfinite(sims[i])]

    def __len__(self):
        return len(self.records)