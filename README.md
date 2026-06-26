# SEC Filings RAG

Ask grounded questions about real SEC filings. Every answer cites the passage it came from.

**Live demo:** https://your-url.vercel.app

<img width="761" height="672" alt="image" src="https://github.com/user-attachments/assets/70a51b7d-615a-4f47-b0b7-66e342c88116" />


## How it works

Offline, once per filing: fetch from EDGAR → linearize tables → chunk → embed → save.

At request time: embed the question → cosine search the index → pass top chunks to the LLM with a "refuse rather than hallucinate" prompt → return answer + sources.

## Stack

Python, FastAPI, numpy, BeautifulSoup, React, Vite, Tailwind. OpenAI for embeddings and generation. Railway for the backend, Vercel for the frontend.

## Decisions worth noting

- **Tables get linearized before chunking.** Naive HTML extraction scatters numbers away from their labels; rewriting rows as `label: header=value` keeps them attached.
- **`temperature=0` and an explicit refusal prompt.** Grounded QA needs faithfulness, not creativity. The model says "I couldn't find that" instead of guessing.
- **Per-chunk metadata** (`company`, `filing_type`, `chunk_index`) is what makes source citation and per-company filtering work.
- **The vector store ships with the deploy.** ~5MB committed to git. At larger scale this moves to S3.



## Next

Hybrid caching for arbitrary tickers. Section-aware chunking. pgvector instead of numpy. Streaming responses.
