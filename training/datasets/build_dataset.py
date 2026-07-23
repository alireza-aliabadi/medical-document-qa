#!/usr/bin/env python3
"""Build instruction dataset from indexed document chunks."""

import argparse
import json
import random
from pathlib import Path

QUESTION_TEMPLATES = [
    "What does the document say about {topic}?",
    "Summarize the findings related to {topic}.",
    "What treatment is mentioned for {topic}?",
    "What are the symptoms of {topic}?",
]

TOPICS = ["diabetes", "hypertension", "pneumonia", "asthma", "cancer", "stroke"]


def generate_qa_pairs(chunks: list[dict], num_pairs: int = 100) -> list[dict]:
    pairs: list[dict] = []
    for _ in range(num_pairs):
        chunk = random.choice(chunks)
        topic = random.choice(TOPICS)
        question = random.choice(QUESTION_TEMPLATES).format(topic=topic)
        answer = chunk.get("content", "")[:512]
        pairs.append(
            {
                "instruction": question,
                "input": "",
                "output": answer,
                "metadata": {
                    "chunk_id": chunk.get("chunk_id"),
                    "document_id": chunk.get("document_id"),
                    "page_number": chunk.get("page_number"),
                },
            }
        )
    return pairs


def deduplicate(pairs: list[dict]) -> list[dict]:
    seen: set[str] = set()
    unique: list[dict] = []
    for pair in pairs:
        key = pair["instruction"] + pair["output"][:128]
        if key not in seen:
            seen.add(key)
            unique.append(pair)
    return unique


def main() -> None:
    parser = argparse.ArgumentParser(description="Build medical QA dataset")
    parser.add_argument("--input", type=Path, default=Path("training/datasets/raw/chunks.json"))
    parser.add_argument(
        "--output", type=Path, default=Path("training/datasets/processed/instruction.jsonl")
    )
    parser.add_argument("--num-pairs", type=int, default=100)
    args = parser.parse_args()

    if args.input.exists():
        chunks = json.loads(args.input.read_text())
    else:
        chunks = [
            {
                "chunk_id": "sample-1",
                "document_id": "doc-1",
                "page_number": 1,
                "content": "Metformin is first-line therapy for type 2 diabetes.",
            }
        ]

    pairs = deduplicate(generate_qa_pairs(chunks, num_pairs=args.num_pairs))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as f:
        for pair in pairs:
            f.write(json.dumps(pair) + "\n")
    print(f"Wrote {len(pairs)} examples to {args.output}")


if __name__ == "__main__":
    main()
