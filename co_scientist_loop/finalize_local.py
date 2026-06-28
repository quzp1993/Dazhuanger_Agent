from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--memory", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--top-n", type=int, default=12)
    parser.add_argument("--note", default="")
    args = parser.parse_args()

    data = json.loads(Path(args.memory).read_text(encoding="utf-8"))
    clusters = data.get("clusters", {})
    cluster_counts = Counter(clusters.values())
    top = sorted(data["hypotheses"], key=lambda item: item["elo"], reverse=True)[: args.top_n]

    lines = [
        "# Partial Final Report (Local Summary)",
        "",
        args.note or "This summary was generated locally from memory.json.",
        "",
        "## Run Statistics",
        "",
        f"- Hypotheses: {len(data['hypotheses'])}",
        f"- Reviews: {len(data['reviews'])}",
        f"- Ranking matches: {len(data['matches'])}",
        f"- Meta-reviews: {len(data.get('meta_reviews', []))}",
        f"- Proximity clusters: {len(cluster_counts)}",
        f"- Proximity pairs: {len(data.get('proximity_pairs', []))}",
        "",
        "## Cluster Sizes",
        "",
    ]
    for cluster_id, count in sorted(cluster_counts.items(), key=lambda item: str(item[0])):
        lines.append(f"- Cluster {cluster_id}: {count} hypotheses")

    lines += ["", "## Top Ranked Hypotheses", ""]
    for index, hypothesis in enumerate(top, start=1):
        text = " ".join(hypothesis["text"].split())
        lines.append(
            f"{index}. **{hypothesis['id']}** | Elo {hypothesis['elo']:.1f} | "
            f"Cluster {clusters.get(hypothesis['id'])}"
        )
        lines.append(f"   {text[:700]}")
        lines.append("")

    lines += [
        "## Interpretation Notes",
        "",
        "- Treat this as a partial run if the original loop stopped before final meta-review.",
        "- Elo is a prioritization signal, not scientific proof.",
        "- If most high-Elo hypotheses collapse into one cluster, increase diversity pressure before another long run.",
        "- Useful next improvements: retry failed API calls, checkpoint/resume, and per-cluster quotas for Evolution.",
    ]

    Path(args.out).write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
