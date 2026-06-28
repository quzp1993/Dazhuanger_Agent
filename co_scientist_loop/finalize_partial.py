from __future__ import annotations

import argparse
import json
from pathlib import Path

from .llm import make_client
from .memory import Hypothesis
from .proximity import build_proximity


def build_prompt(memory_path: Path, top_n: int) -> str:
    data = json.loads(memory_path.read_text(encoding="utf-8"))
    if not data.get("clusters"):
        hypotheses = [Hypothesis(**item) for item in data["hypotheses"]]
        clusters, _ = build_proximity(hypotheses)
        data["clusters"] = clusters
    top = sorted(data["hypotheses"], key=lambda item: item["elo"], reverse=True)[:top_n]
    materials = []
    for index, hypothesis in enumerate(top, start=1):
        text = hypothesis["text"].replace("\n", " ")
        materials.append(
            f"{index}. {hypothesis['id']} | Elo {hypothesis['elo']:.1f} | Cluster {data['clusters'].get(hypothesis['id'])}\n{text[:900]}"
        )
    return (
        "Write a concise final research overview from these ranked hypotheses. "
        "Include ranked hypothesis themes, strongest rationale, key weaknesses, "
        "and recommended next experiments. The research goal is private; do not "
        "restate it.\n\n"
        + "\n\n".join(materials)
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--memory", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--provider", choices=["openai", "anthropic"], default="anthropic")
    parser.add_argument("--top-n", type=int, default=10)
    args = parser.parse_args()

    prompt = build_prompt(Path(args.memory), args.top_n)
    report = make_client(args.provider).complete(prompt)
    Path(args.out).write_text(report, encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
