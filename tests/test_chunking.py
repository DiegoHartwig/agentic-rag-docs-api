import pytest

from app.ingestion.chunking import chunk_pages


def test_simple_text_produces_at_least_one_chunk():
    pages = [{"page": 1, "text": "Este é um texto simples para teste."}]
    result = chunk_pages(pages)
    assert len(result) >= 1


def test_empty_page_is_ignored():
    pages = [
        {"page": 1, "text": "   "},
        {"page": 2, "text": ""},
        {"page": 3, "text": None},
    ]
    result = chunk_pages(pages)
    assert result == []


def test_chunk_index_is_sequential():
    long_text = "palavra " * 500
    pages = [{"page": 1, "text": long_text}]
    result = chunk_pages(pages, chunk_size=100, chunk_overlap=10)
    indices = [c["chunk_index"] for c in result]
    assert indices == list(range(len(result)))


def test_chunk_index_is_sequential_across_pages():
    pages = [
        {"page": 1, "text": "palavra " * 200},
        {"page": 2, "text": "outra " * 200},
    ]
    result = chunk_pages(pages, chunk_size=100, chunk_overlap=10)
    indices = [c["chunk_index"] for c in result]
    assert indices == list(range(len(result)))


def test_page_number_is_preserved():
    pages = [{"page": 5, "text": "conteúdo da página cinco"}]
    result = chunk_pages(pages)
    assert all(c["page"] == 5 for c in result)


def test_page_none_is_preserved():
    pages = [{"page": None, "text": "conteúdo sem número de página"}]
    result = chunk_pages(pages)
    assert all(c["page"] is None for c in result)


def test_invalid_chunk_size_raises():
    with pytest.raises(ValueError, match="chunk_size"):
        chunk_pages([{"page": 1, "text": "x"}], chunk_size=0)


def test_invalid_chunk_overlap_negative_raises():
    with pytest.raises(ValueError, match="chunk_overlap"):
        chunk_pages([{"page": 1, "text": "x"}], chunk_size=100, chunk_overlap=-1)


def test_invalid_chunk_overlap_too_large_raises():
    with pytest.raises(ValueError, match="chunk_overlap"):
        chunk_pages([{"page": 1, "text": "x"}], chunk_size=100, chunk_overlap=100)
