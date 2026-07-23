"""Tests for chunking service."""

from backend.services.chunking import ChunkingService


def test_chunk_pages_splits_text():
    service = ChunkingService(chunk_size=100, overlap=10)
    pages = [(1, "First sentence. Second sentence. Third sentence with more words.")]
    chunks = service.chunk_pages(pages)
    assert len(chunks) >= 1
    assert all(c.page_number == 1 for c in chunks)


def test_split_sentences():
    text = "Hello world. How are you? Fine!"
    parts = ChunkingService._split_sentences(text)
    assert len(parts) == 3
