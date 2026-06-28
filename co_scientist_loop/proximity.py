from __future__ import annotations

import math
import re
from collections import Counter, defaultdict

from .memory import Hypothesis, ProximityPair


STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "into", "between",
    "hypothesis", "mechanism", "title", "causal", "specific", "test", "using",
    "will", "may", "can", "could", "would", "are", "has", "have", "been",
}


def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", text.lower())
    return [token for token in tokens if token not in STOPWORDS]


def term_vector(text: str) -> Counter[str]:
    return Counter(tokenize(text))


def cosine_similarity(left: Counter[str], right: Counter[str]) -> float:
    if not left or not right:
        return 0.0
    shared = set(left) & set(right)
    dot = sum(left[token] * right[token] for token in shared)
    norm_left = math.sqrt(sum(value * value for value in left.values()))
    norm_right = math.sqrt(sum(value * value for value in right.values()))
    if norm_left == 0 or norm_right == 0:
        return 0.0
    return dot / (norm_left * norm_right)


def build_proximity(
    hypotheses: list[Hypothesis],
    threshold: float = 0.5,
) -> tuple[dict[str, int], list[ProximityPair]]:
    vectors = {hypothesis.id: term_vector(hypothesis.text) for hypothesis in hypotheses}
    parent: dict[str, str] = {hypothesis.id: hypothesis.id for hypothesis in hypotheses}
    pairs: list[ProximityPair] = []

    def find(item: str) -> str:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(left: str, right: str) -> None:
        root_left = find(left)
        root_right = find(right)
        if root_left != root_right:
            parent[root_right] = root_left

    for index, left in enumerate(hypotheses):
        for right in hypotheses[index + 1:]:
            similarity = cosine_similarity(vectors[left.id], vectors[right.id])
            if similarity >= threshold:
                pairs.append(ProximityPair(left.id, right.id, round(similarity, 4)))
                union(left.id, right.id)

    roots = {hypothesis.id: find(hypothesis.id) for hypothesis in hypotheses}
    ordered_roots = {
        root: cluster_index
        for cluster_index, root in enumerate(sorted(set(roots.values())), start=1)
    }
    clusters = {
        hypothesis_id: ordered_roots[root]
        for hypothesis_id, root in roots.items()
    }
    return clusters, pairs


def diverse_top_hypotheses(
    hypotheses: list[Hypothesis],
    clusters: dict[str, int],
    n: int,
    max_per_cluster: int = 2,
) -> list[Hypothesis]:
    if n <= 0:
        return []
    by_cluster: dict[int, list[Hypothesis]] = defaultdict(list)
    for hypothesis in sorted(hypotheses, key=lambda item: item.elo, reverse=True):
        by_cluster[clusters.get(hypothesis.id, -1)].append(hypothesis)

    selected: list[Hypothesis] = []
    cluster_taken: Counter[int] = Counter()
    for cluster_id in sorted(
        by_cluster,
        key=lambda key: by_cluster[key][0].elo,
        reverse=True,
    ):
        selected.append(by_cluster[cluster_id][0])
        cluster_taken[cluster_id] += 1
        if len(selected) >= n:
            return selected

    for hypothesis in sorted(hypotheses, key=lambda item: item.elo, reverse=True):
        cluster_id = clusters.get(hypothesis.id, -1)
        if hypothesis not in selected and cluster_taken[cluster_id] < max_per_cluster:
            selected.append(hypothesis)
            cluster_taken[cluster_id] += 1
        if len(selected) >= n:
            break
    if len(selected) < n:
        for hypothesis in sorted(hypotheses, key=lambda item: item.elo, reverse=True):
            if hypothesis not in selected:
                selected.append(hypothesis)
            if len(selected) >= n:
                break
    return selected
