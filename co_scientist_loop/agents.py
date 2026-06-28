from __future__ import annotations

import re

from .llm import LLMClient, numbered_items
from .memory import Hypothesis, Memory
from .prompts import (
    EVOLUTION_PROMPT,
    GENERATION_PROMPT,
    META_REVIEW_PROMPT,
    OUTSIDER_GENERATION_PROMPT,
    RANKING_PROMPT,
    REFLECTION_PROMPT,
)
from .ranking import update_elo
from .proximity import build_proximity, diverse_top_hypotheses


def _score(pattern: str, text: str) -> int | None:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return None
    value = int(match.group(1))
    return min(5, max(1, value))


class GenerationAgent:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def run(self, memory: Memory, count: int) -> list[Hypothesis]:
        prompt = GENERATION_PROMPT.format(
            goal=memory.goal,
            preferences=memory.preferences,
            count=count,
        )
        response = self.llm.complete(prompt)
        hypotheses = numbered_items(response)[:count]
        return [memory.add_hypothesis(item, source="generation") for item in hypotheses]

    def run_outsiders(self, memory: Memory, count: int) -> list[Hypothesis]:
        themes = summarize_cluster_themes(memory)
        prompt = OUTSIDER_GENERATION_PROMPT.format(
            goal=memory.goal,
            preferences=memory.preferences,
            current_themes=themes,
            count=count,
        )
        response = self.llm.complete(prompt)
        hypotheses = numbered_items(response)[:count]
        return [memory.add_hypothesis(item, source="outsider_generation") for item in hypotheses]


class ReflectionAgent:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def run(self, memory: Memory, hypothesis: Hypothesis) -> None:
        prompt = REFLECTION_PROMPT.format(
            goal=memory.goal,
            preferences=memory.preferences,
            hypothesis=hypothesis.text,
        )
        response = self.llm.complete(prompt)
        memory.add_review(
            hypothesis.id,
            response,
            novelty=_score(r"Novelty:\s*([1-5])", response),
            plausibility=_score(r"Plausibility:\s*([1-5])", response),
            testability=_score(r"Testability:\s*([1-5])", response),
        )


class RankingAgent:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def compare(self, memory: Memory, left: Hypothesis, right: Hypothesis) -> None:
        review_left = "\n\n".join(review.text for review in memory.reviews_for(left.id)) or "No review."
        review_right = "\n\n".join(review.text for review in memory.reviews_for(right.id)) or "No review."
        prompt = RANKING_PROMPT.format(
            goal=memory.goal,
            preferences=memory.preferences,
            hypothesis_a=left.text,
            review_a=review_left,
            hypothesis_b=right.text,
            review_b=review_right,
        )
        response = self.llm.complete(prompt)
        winner = right if re.search(r"better idea:\s*2", response, flags=re.IGNORECASE) else left
        loser = left if winner is right else right
        update_elo(winner, loser)
        memory.add_match(left.id, right.id, winner.id, response)


class EvolutionAgent:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def run(self, memory: Memory, count: int, max_per_cluster: int = 2) -> list[Hypothesis]:
        top = diverse_top_hypotheses(
            memory.hypotheses,
            memory.clusters,
            n=min(5, len(memory.hypotheses)),
            max_per_cluster=max_per_cluster,
        )
        top_text = "\n\n".join(f"{item.id} (Elo {item.elo:.1f}): {item.text}" for item in top)
        prompt = EVOLUTION_PROMPT.format(
            goal=memory.goal,
            preferences=memory.preferences,
            top_hypotheses=top_text,
            count=count,
        )
        response = self.llm.complete(prompt)
        parent_ids = [item.id for item in top]
        hypotheses = numbered_items(response)[:count]
        return [memory.add_hypothesis(item, source="evolution", parent_ids=parent_ids) for item in hypotheses]


class ProximityAgent:
    def run(self, memory: Memory, threshold: float = 0.5) -> None:
        clusters, pairs = build_proximity(memory.hypotheses, threshold=threshold)
        memory.clusters = clusters
        memory.proximity_pairs = pairs


class MetaReviewAgent:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def run(self, memory: Memory) -> str:
        materials = []
        for hypothesis in memory.top_hypotheses(n=10):
            reviews = "\n".join(review.text for review in memory.reviews_for(hypothesis.id))
            cluster = memory.cluster_for(hypothesis.id)
            materials.append(f"{hypothesis.id} | Elo {hypothesis.elo:.1f} | Cluster {cluster}\n{hypothesis.text}\nReviews:\n{reviews}")
        prompt = META_REVIEW_PROMPT.format(
            goal=memory.goal,
            preferences=memory.preferences,
            materials="\n\n---\n\n".join(materials),
        )
        report = self.llm.complete(prompt)
        memory.meta_reviews.append(report)
        return report


def summarize_cluster_themes(memory: Memory, max_clusters: int = 6) -> str:
    clusters: dict[int, list[Hypothesis]] = {}
    for hypothesis in sorted(memory.hypotheses, key=lambda item: item.elo, reverse=True):
        cluster_id = memory.cluster_for(hypothesis.id) or -1
        clusters.setdefault(cluster_id, []).append(hypothesis)

    lines: list[str] = []
    for cluster_id, hypotheses in sorted(
        clusters.items(),
        key=lambda item: item[1][0].elo,
        reverse=True,
    )[:max_clusters]:
        exemplar = hypotheses[0]
        lines.append(
            f"Cluster {cluster_id}: top Elo {exemplar.elo:.1f}; exemplar: "
            f"{exemplar.text[:500].replace(chr(10), ' ')}"
        )
    return "\n".join(lines) if lines else "No dominant themes yet."
