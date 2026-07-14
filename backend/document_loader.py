import os
from typing import List
from pypdf import PdfReader

def load_text(file_path: str) -> str:
    """Load text from a file (txt or pdf)."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    elif ext == '.pdf':
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    else:
        raise ValueError(f"Unsupported file format: {ext}")