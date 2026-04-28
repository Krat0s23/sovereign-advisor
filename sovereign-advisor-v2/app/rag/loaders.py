from pathlib import Path
import frontmatter
from docx import Document
from pypdf import PdfReader

SUPPORTED_EXTENSIONS = {".txt", ".md", ".markdown", ".pdf", ".docx"}

def load_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")

def load_markdown_file(path: Path) -> str:
    post = frontmatter.load(path)
    metadata = "\n".join([f"{k}: {v}" for k, v in post.metadata.items()])
    body = post.content or ""
    return f"{metadata}\n\n{body}".strip()

def load_pdf_file(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            pages.append(text)
    return "\n\n".join(pages)

def load_docx_file(path: Path) -> str:
    document = Document(str(path))
    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)

def load_document(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return load_text_file(path)
    if suffix in {".md", ".markdown"}:
        return load_markdown_file(path)
    if suffix == ".pdf":
        return load_pdf_file(path)
    if suffix == ".docx":
        return load_docx_file(path)
    raise ValueError(f"Unsupported file type: {suffix}")
