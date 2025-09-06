import spacy
import tiktoken
from typing import List

# load spaCy English model
nlp = spacy.load("en_core_web_sm")

# tokenizer for counting tokens (OpenAI tiktoken)
enc = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    try:
        return len(enc.encode(text))
    except Exception:
        return len(text.split())

def split_text(text: str, max_tokens: int = 500, overlap: int = 50) -> List[str]:
    """
    Hybrid splitter: paragraph -> sentence -> char
    """
    chunks = []

    # step 1: split by paragraph
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    for para in paragraphs:
        if count_tokens(para) <= max_tokens:
            chunks.append(para)
            continue

        # step 2: split by sentence using spaCy
        doc = nlp(para)
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

        current_chunk = ""
        for sent in sentences:
            if count_tokens(current_chunk + " " + sent) <= max_tokens:
                current_chunk += " " + sent if current_chunk else sent
            else:
                chunks.append(current_chunk)
                current_chunk = sent

        if current_chunk:
            chunks.append(current_chunk)

    # step 3: fallback char-based split if still too long
    final_chunks = []
    for ch in chunks:
        if count_tokens(ch) > max_tokens:
            tokens = enc.encode(ch)
            start = 0
            while start < len(tokens):
                end = start + max_tokens
                piece = enc.decode(tokens[start:end])
                final_chunks.append(piece)
                start = end - overlap
        else:
            final_chunks.append(ch)

    return final_chunks


if __name__ == "__main__":
    sample = """
    This is a long paragraph. It contains multiple sentences. The splitter should handle this.

    Another paragraph starts here. If it's too long, it will be cut.
    """

    chunks = split_text(sample, max_tokens=20)
    for i, ch in enumerate(chunks, 1):
        print(f"--- Chunk {i} ---\n{ch}\n")
