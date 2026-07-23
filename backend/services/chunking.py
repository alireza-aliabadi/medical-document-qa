"""Semantic chunking for medical documents."""

import re
from dataclasses import dataclass


@dataclass
class TextChunk:
    content: str
    chunk_index: int
    page_number: int | None
    metadata: dict[str, str | int | None]


class ChunkingService:
    def __init__(self, chunk_size: int = 512, overlap: int = 64) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_pages(
        self,
        pages: list[tuple[int, str]],
        document_metadata: dict | None = None,
    ) -> list[TextChunk]:
        chunks: list[TextChunk] = []
        index = 0
        base_meta = document_metadata or {}

        for page_number, text in pages:
            sentences = self._split_sentences(text)
            buffer: list[str] = []
            buffer_len = 0

            for sentence in sentences:
                sentence_len = len(sentence)
                if buffer_len + sentence_len > self.chunk_size and buffer:
                    chunks.append(
                        TextChunk(
                            content=" ".join(buffer),
                            chunk_index=index,
                            page_number=page_number,
                            metadata={**base_meta, "page_number": page_number},
                        )
                    )
                    index += 1
                    overlap_text = " ".join(buffer)[-self.overlap :]
                    buffer = [overlap_text] if overlap_text else []
                    buffer_len = len(overlap_text)

                buffer.append(sentence)
                buffer_len += sentence_len

            if buffer:
                chunks.append(
                    TextChunk(
                        content=" ".join(buffer),
                        chunk_index=index,
                        page_number=page_number,
                        metadata={**base_meta, "page_number": page_number},
                    )
                )
                index += 1

        return chunks

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        parts = re.split(r"(?<=[.!?])\s+", text.strip())
        return [p.strip() for p in parts if p.strip()]
