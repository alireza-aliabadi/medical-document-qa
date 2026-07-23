#!/usr/bin/env python3
"""QLoRA fine-tuning script for medical QA."""

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Train QLoRA model")
    parser.add_argument(
        "--dataset", type=Path, default=Path("training/datasets/processed/instruction.jsonl")
    )
    parser.add_argument("--model", default="Qwen/Qwen3-1.7B")
    parser.add_argument("--output", type=Path, default=Path("training/artifacts/qlora-checkpoint"))
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.dataset.exists():
        raise SystemExit(f"Dataset not found: {args.dataset}. Run build_dataset.py first.")

    examples = [json.loads(line) for line in args.dataset.read_text().splitlines() if line.strip()]
    print(f"Loaded {len(examples)} training examples")
    print(f"Model: {args.model}, epochs: {args.epochs}, output: {args.output}")

    if args.dry_run:
        print("Dry run — skipping GPU training. Install poetry group ml for full training.")
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "config.json").write_text(
            json.dumps({"model": args.model, "method": "qlora"})
        )
        return

    try:
        import torch
        from peft import LoraConfig, get_peft_model
        from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
        from trl import SFTTrainer
    except ImportError as exc:
        raise SystemExit("ML dependencies missing. Install with: poetry install --with ml") from exc

    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    lora_config = LoraConfig(
        r=16, lora_alpha=32, target_modules=["q_proj", "v_proj"], lora_dropout=0.05
    )
    model = get_peft_model(model, lora_config)

    def format_example(row: dict) -> str:
        return f"### Instruction:\n{row['instruction']}\n\n### Response:\n{row['output']}"

    texts = [format_example(row) for row in examples]
    training_args = TrainingArguments(
        output_dir=str(args.output),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=1,
        gradient_checkpointing=True,
        logging_steps=10,
        save_steps=100,
    )
    trainer = SFTTrainer(model=model, args=training_args, train_dataset=texts, tokenizer=tokenizer)
    trainer.train()
    model.save_pretrained(args.output)
    tokenizer.save_pretrained(args.output)
    print(f"Saved checkpoint to {args.output}")


if __name__ == "__main__":
    main()
