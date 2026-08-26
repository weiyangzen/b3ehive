#!/usr/bin/env python3
"""One-shot Cursor SDK worker for generated b3ehive crons."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--prompt-file", required=True)
    args = parser.parse_args()

    api_key = os.environ.get("CURSOR_API_KEY", "").strip()
    if not api_key:
        print("CURSOR_API_KEY is required for the Cursor agent runner", file=sys.stderr)
        return 2

    prompt_path = Path(args.prompt_file)
    workspace = Path(args.workspace)
    if not prompt_path.is_file():
        print(f"prompt file not found: {prompt_path}", file=sys.stderr)
        return 2
    if not workspace.is_dir():
        print(f"workspace not found: {workspace}", file=sys.stderr)
        return 2

    try:
        from cursor_sdk import Agent, AgentOptions, LocalAgentOptions
    except ImportError:
        print(
            "cursor-sdk is required: pip install cursor-sdk",
            file=sys.stderr,
        )
        return 2

    prompt = prompt_path.read_text(encoding="utf-8")
    options_kwargs = {
        "api_key": api_key,
        "local": LocalAgentOptions(cwd=str(workspace)),
    }
    model = os.environ.get("CURSOR_MODEL", "").strip()
    if model:
        options_kwargs["model"] = model

    result = Agent.prompt(prompt, AgentOptions(**options_kwargs))
    text = getattr(result, "result", None)
    if text is None:
        text = str(result)
    sys.stdout.write(text if text.endswith("\n") else f"{text}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
