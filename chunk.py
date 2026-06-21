

def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list[str]:
    
    words = text.split()          
    if not words:
        return []

    chunks = []
    step = chunk_size - overlap   
    if step <= 0:

        raise ValueError("overlap must be smaller than chunk_size")

    for start in range(0, len(words), step):
        chunk_words = words[start:start + chunk_size]
        chunks.append(" ".join(chunk_words))
        if start + chunk_size >= len(words):
            break                  
    return chunks


def inspect_chunks(chunks: list[str], n_samples: int = 2):
    
    if not chunks:
        print("No chunks produced.")
        return

    lengths = [len(c.split()) for c in chunks]
    print(f"Total chunks : {len(chunks)}")
    print(f"Avg words    : {sum(lengths) / len(lengths):.0f}")
    print(f"Min / Max    : {min(lengths)} / {max(lengths)} words")
    print("=" * 60)

    for i in range(min(n_samples, len(chunks))):
        preview = chunks[i][:400] + ("..." if len(chunks[i]) > 400 else "")
        print(f"\n--- CHUNK {i} ({len(chunks[i].split())} words) ---\n{preview}")