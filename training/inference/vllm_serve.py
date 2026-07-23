#!/usr/bin/env python3
"""vLLM inference server launcher."""

import argparse
import subprocess
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve model with vLLM")
    parser.add_argument("--model", default="Qwen/Qwen3-1.7B")
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    cmd = [
        sys.executable,
        "-m",
        "vllm.entrypoints.openai.api_server",
        "--model",
        args.model,
        "--port",
        str(args.port),
    ]
    print("Command:", " ".join(cmd))
    if args.dry_run:
        print("Dry run — vLLM not started")
        return
    subprocess.run(cmd, check=False)


if __name__ == "__main__":
    main()
