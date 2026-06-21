from chunk import chunk_text, inspect_chunks

with open("data/spacex_424B4.txt", encoding="utf-8") as f:
    text = f.read()

print(f"Document length: {len(text):,} characters\n")
chunks = chunk_text(text, chunk_size=300, overlap=50)
inspect_chunks(chunks)