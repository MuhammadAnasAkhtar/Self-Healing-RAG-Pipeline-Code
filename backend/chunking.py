from typing import List
import re

def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50, strategy: str = "fixed") -> List[str]:
    """Chunk text into smaller pieces based on strategy."""
    if strategy == "fixed":
        return fixed_size_chunking(text, chunk_size, overlap)
    elif strategy == "sentence":
        return sentence_chunking(text, chunk_size, overlap)
    else:
        raise ValueError(f"Unknown chunking strategy: {strategy}")

def fixed_size_chunking(text: str, chunk_size: int, overlap: int) -> List[str]:
    """Simple fixed-size overlapping chunks."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        start += chunk_size - overlap
        if start >= len(words):
            break
    return chunks

def sentence_chunking(text: str, chunk_size: int, overlap: int) -> List[str]:
    """Chunk by sentences, grouping to approximate chunk_size words."""
    # Split into sentences (simple regex)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = []
    current_length = 0
    for sent in sentences:
        words = sent.split()
        sent_len = len(words)
        if current_length + sent_len > chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))
            # Keep overlap sentences from the end of last chunk
            overlap_sents = []
            overlap_len = 0
            for s in reversed(current_chunk):
                s_words = s.split()
                if overlap_len + len(s_words) <= overlap:
                    overlap_sents.insert(0, s)
                    overlap_len += len(s_words)
                else:
                    break
            current_chunk = overlap_sents
            current_length = overlap_len
        current_chunk.append(sent)
        current_length += sent_len
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks