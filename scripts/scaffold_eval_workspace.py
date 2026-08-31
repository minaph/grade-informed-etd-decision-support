from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a repeated with-skill/without-skill eval workspace.")
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--iteration", default="iteration-1")
    parser.add_argument("--repetitions", type=int, default=None)
    args = parser.parse_args()

    data = json.loads((ROOT / "evals/evals.json").read_text(encoding="utf-8"))
    minimum = int(data.get("evaluation_protocol", {}).get("minimum_repetitions_per_prompt", 3))
    repetitions = args.repetitions or minimum
    if repetitions < minimum:
        raise SystemExit(f"repetitions must be at least {minimum}")

    base = args.workspace / args.iteration
    for item in data.get("evals", []):
        for repetition in range(1, repetitions + 1):
            for mode in ("with_skill", "without_skill"):
                run = base / str(item["id"]) / f"repeat-{repetition}" / mode
                (run / "outputs").mkdir(parents=True, exist_ok=True)
                (run / "RUN_INSTRUCTIONS.txt").write_text(
                    f"Skill: {ROOT if mode == 'with_skill' else 'none'}\n"
                    f"Prompt: {item['prompt']}\n"
                    f"Files: {item.get('files', [])}\n"
                    f"Assertions: {item.get('assertions', [])}\n"
                    f"Capture: output, tool trace, latency, token usage, triggered status\n"
                    f"Save results under: {run / 'outputs'}\n",
                    encoding="utf-8",
                )
    print(base)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
