from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from .agents import (
    EvolutionAgent,
    GenerationAgent,
    MetaReviewAgent,
    ProximityAgent,
    RankingAgent,
    ReflectionAgent,
)
from .llm import make_client
from .memory import Memory
from .ranking import select_pairs_with_clusters


DEFAULT_PREFERENCES = """Hypotheses should be plausible, novel, testable with realistic experiments,
specific about mechanism and entities, and safe/ethical."""


def run_loop(
    goal: str,
    rounds: int,
    initial_count: int,
    evolved_count: int,
    matches_per_round: int,
    provider: str,
    out_dir: Path,
    preferences: str = DEFAULT_PREFERENCES,
    proximity_threshold: float = 0.5,
    max_evolution_seeds_per_cluster: int = 2,
    outsider_count: int = 1,
    outsider_every: int = 3,
) -> Memory:
    llm = make_client(provider)
    memory = Memory(goal=goal, preferences=preferences)

    generation = GenerationAgent(llm)
    reflection = ReflectionAgent(llm)
    ranking = RankingAgent(llm)
    evolution = EvolutionAgent(llm)
    proximity = ProximityAgent()
    meta_review = MetaReviewAgent(llm)

    out_dir.mkdir(parents=True, exist_ok=True)

    print("[1/5] Generating initial hypotheses")
    new_hypotheses = generation.run(memory, count=initial_count)
    for hypothesis in new_hypotheses:
        reflection.run(memory, hypothesis)
        memory.save(out_dir / "memory.json")
    proximity.run(memory, threshold=proximity_threshold)
    memory.save(out_dir / "memory.json")

    for round_index in range(1, rounds + 1):
        print(f"[round {round_index}] Updating proximity clusters")
        proximity.run(memory, threshold=proximity_threshold)
        memory.save(out_dir / "memory.json")
        print(f"[round {round_index}] Ranking hypotheses")
        pairs = select_pairs_with_clusters(
            memory.hypotheses,
            memory.matches,
            memory.clusters,
            max_pairs=matches_per_round,
        )
        for left, right in pairs:
            ranking.compare(memory, left, right)
            memory.save(out_dir / "memory.json")

        print(f"[round {round_index}] Evolving top hypotheses")
        evolved = evolution.run(
            memory,
            count=evolved_count,
            max_per_cluster=max_evolution_seeds_per_cluster,
        )
        for hypothesis in evolved:
            reflection.run(memory, hypothesis)
            memory.save(out_dir / "memory.json")

        if outsider_count > 0 and outsider_every > 0 and round_index % outsider_every == 0:
            print(f"[round {round_index}] Generating outsider hypotheses")
            proximity.run(memory, threshold=proximity_threshold)
            outsiders = generation.run_outsiders(memory, count=outsider_count)
            for hypothesis in outsiders:
                reflection.run(memory, hypothesis)
                memory.save(out_dir / "memory.json")

        proximity.run(memory, threshold=proximity_threshold)

        memory.save(out_dir / "memory.json")

    print("[5/5] Writing final meta-review")
    proximity.run(memory, threshold=proximity_threshold)
    report = meta_review.run(memory)
    (out_dir / "final_report.md").write_text(report, encoding="utf-8")
    memory.save(out_dir / "memory.json")
    return memory


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a lightweight Co-Scientist loop.")
    parser.add_argument("--goal", required=True, help="Research goal in natural language.")
    parser.add_argument("--rounds", type=int, default=2, help="Number of evolution/ranking rounds.")
    parser.add_argument("--initial-count", type=int, default=5, help="Initial hypotheses to generate.")
    parser.add_argument("--evolved-count", type=int, default=3, help="Improved hypotheses per round.")
    parser.add_argument("--matches-per-round", type=int, default=8, help="Pairwise ranking matches per round.")
    parser.add_argument("--provider", choices=["mock", "openai", "anthropic"], default="mock", help="LLM provider.")
    parser.add_argument("--out", default=None, help="Output directory. Defaults to runs/<timestamp>.")
    parser.add_argument("--preferences", default=DEFAULT_PREFERENCES, help="Evaluation criteria.")
    parser.add_argument("--proximity-threshold", type=float, default=0.5, help="Similarity threshold for Proximity clusters.")
    parser.add_argument("--max-evolution-seeds-per-cluster", type=int, default=2, help="Maximum Evolution seed hypotheses from one cluster.")
    parser.add_argument("--outsider-count", type=int, default=1, help="Outsider hypotheses to generate every outsider interval.")
    parser.add_argument("--outsider-every", type=int, default=3, help="Generate outsider hypotheses every N rounds; 0 disables it.")
    args = parser.parse_args()

    out_dir = Path(args.out) if args.out else Path("runs") / datetime.now().strftime("%Y%m%d_%H%M%S")
    memory = run_loop(
        goal=args.goal,
        rounds=args.rounds,
        initial_count=args.initial_count,
        evolved_count=args.evolved_count,
        matches_per_round=args.matches_per_round,
        provider=args.provider,
        out_dir=out_dir,
        preferences=args.preferences,
        proximity_threshold=args.proximity_threshold,
        max_evolution_seeds_per_cluster=args.max_evolution_seeds_per_cluster,
        outsider_count=args.outsider_count,
        outsider_every=args.outsider_every,
    )
    print(f"Done. Top hypotheses:")
    for item in memory.top_hypotheses(5):
        print(f"- {item.id} | Elo {item.elo:.1f} | {item.text[:100].replace(chr(10), ' ')}")
    print(f"Outputs: {out_dir}")
