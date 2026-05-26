import pytest

from app.ingestion.loaders import load_document


def test_load_txt(tmp_path):
    f = tmp_path / "doc.txt"
    f.write_text("hello world", encoding="utf-8")

    result = load_document(str(f))

    assert result == [{"page": None, "text": "hello world"}]


def test_load_markdown(tmp_path):
    f = tmp_path / "doc.md"
    f.write_text("# Título\n\nConteúdo.", encoding="utf-8")

    result = load_document(str(f))

    assert result == [{"page": None, "text": "# Título\n\nConteúdo."}]


def test_load_markdown_extension_long(tmp_path):
    f = tmp_path / "doc.markdown"
    f.write_text("texto", encoding="utf-8")

    result = load_document(str(f))

    assert result[0]["page"] is None
    assert result[0]["text"] == "texto"


def test_load_unsupported_extension(tmp_path):
    f = tmp_path / "doc.docx"
    f.write_bytes(b"fake")

    with pytest.raises(ValueError, match="não suportada"):
        load_document(str(f))


def test_load_uses_filename_for_extension(tmp_path):
    f = tmp_path / "upload_tmp"
    f.write_text("conteúdo", encoding="utf-8")

    result = load_document(str(f), filename="readme.md")

    assert result[0]["text"] == "conteúdo"


def test_load_unsupported_no_extension(tmp_path):
    f = tmp_path / "nodot"
    f.write_bytes(b"x")

    with pytest.raises(ValueError, match="não suportada"):
        load_document(str(f))
