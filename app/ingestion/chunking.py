_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]


def _split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """Divisão recursiva por separadores, com overlap entre chunks."""
    for sep in _SEPARATORS:
        parts = text.split(sep) if sep else list(text)
        if len(parts) > 1:
            break
    else:
        parts = [text]

    chunks: list[str] = []
    current = ""

    for part in parts:
        piece = (current + sep + part).lstrip(sep) if current else part
        if len(piece) <= chunk_size:
            current = piece
        else:
            if current:
                chunks.append(current)
                overlap_start = max(0, len(current) - chunk_overlap)
                current = current[overlap_start:]
                current = (current + sep + part).lstrip(sep) if current else part
            else:
                # part alone exceeds chunk_size — recurse with next separator
                sub = _split_with_fallback(part, chunk_size, chunk_overlap, _SEPARATORS[1:])
                chunks.extend(sub[:-1])
                current = sub[-1] if sub else ""

    if current:
        chunks.append(current)

    return chunks or [text]


def _split_with_fallback(
    text: str, chunk_size: int, chunk_overlap: int, separators: list[str]
) -> list[str]:
    if not separators or len(text) <= chunk_size:
        return [text]

    sep, *rest = separators
    parts = text.split(sep) if sep else list(text)

    if len(parts) == 1:
        return _split_with_fallback(text, chunk_size, chunk_overlap, rest)

    chunks: list[str] = []
    current = ""

    for part in parts:
        piece = (current + sep + part).lstrip(sep) if current else part
        if len(piece) <= chunk_size:
            current = piece
        else:
            if current:
                chunks.append(current)
                overlap_start = max(0, len(current) - chunk_overlap)
                current = current[overlap_start:]
                current = (current + sep + part).lstrip(sep) if current else part
            else:
                sub = _split_with_fallback(part, chunk_size, chunk_overlap, rest)
                chunks.extend(sub[:-1])
                current = sub[-1] if sub else ""

    if current:
        chunks.append(current)

    return chunks or [text]


def chunk_pages(
    pages: list[dict],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[dict]:
    if chunk_size <= 0:
        raise ValueError("chunk_size deve ser maior que 0.")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap deve ser maior ou igual a 0.")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap deve ser menor que chunk_size.")

    chunks = []
    chunk_index = 0

    for page in pages:
        text = page.get("text") or ""
        if not text.strip():
            continue

        for fragment in _split_text(text, chunk_size, chunk_overlap):
            chunks.append(
                {
                    "page": page.get("page"),
                    "chunk_index": chunk_index,
                    "text": fragment,
                }
            )
            chunk_index += 1

    return chunks
