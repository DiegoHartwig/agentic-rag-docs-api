import fitz

_SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md", ".markdown"}


def extract_text_from_pdf(file_path: str) -> list[dict]:
    """Extrai texto de PDFs usando PyMuPDF.

    PDFs escaneados (imagens) podem retornar pouco ou nenhum texto.
    OCR não é suportado.
    """
    doc = fitz.open(file_path)
    try:
        pages = []
        for number, page in enumerate(doc, start=1):
            text = page.get_text("text") or ""
            pages.append({"page": number, "text": text})
        return pages
    finally:
        doc.close()


def extract_text_from_txt(file_path: str) -> list[dict]:
    with open(file_path, encoding="utf-8") as f:
        return [{"page": None, "text": f.read()}]


def extract_text_from_markdown(file_path: str) -> list[dict]:
    with open(file_path, encoding="utf-8") as f:
        return [{"page": None, "text": f.read()}]


def load_document(file_path: str, filename: str | None = None) -> list[dict]:
    """Carrega um documento e retorna lista de páginas com texto.

    Formatos suportados: PDF, TXT, Markdown (.md, .markdown).
    """
    source = filename or file_path
    ext = "." + source.rsplit(".", 1)[-1].lower() if "." in source else ""

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    if ext in (".txt",):
        return extract_text_from_txt(file_path)
    if ext in (".md", ".markdown"):
        return extract_text_from_markdown(file_path)

    raise ValueError(
        f"Extensão '{ext}' não suportada. "
        f"Formatos aceitos: {', '.join(sorted(_SUPPORTED_EXTENSIONS))}."
    )
