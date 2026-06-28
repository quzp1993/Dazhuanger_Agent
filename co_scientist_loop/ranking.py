from __future__ import annotations

from itertools import combinations

from .memory import Hypothesis, Match


def expected_score(rating_a: float, rating_b: float) -> float:
    return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))


def update_elo(winner: Hypothesis, loser: Hypothesis, k: float = 24.0) -> None:
    expected_winner = expected_score(winner.elo, loser.elo)
    expected_loser = expected_score(loser.elo, winner.elo)
    winner.elo += k * (1.0 - expected_winner)
    loser.elo += k * (0.0 - expected_loser)


def select_pairs(hypotheses: list[Hypothesis], existing_matches: list[Match], max_pairs: int) -> list[tuple[Hypothesis, Hypothesis]]:
    return select_pairs_with_clusters(hypotheses, existing_matches, {}, max_pairs)


def select_pairs_with_clusters(
    hypotheses: list[Hypothesis],
    existing_matches: list[Match],
    clusters: dict[str, int],
    max_pairs: int,
) -> list[tuple[Hypothesis, Hypothesis]]:
    seen = {
        tuple(sorted((match.hypothesis_a, match.hypothesis_b)))
        for match in existing_matches
    }
    candidates: list[tuple[int, float, Hypothesis, Hypothesis]] = []
    for left, right in combinations(hypotheses, 2):
        key = tuple(sorted((left.id, right.id)))
        if key in seen:
            continue
        same_cluster = clusters.get(left.id) == clusters.get(right.id)
        cluster_penalty = 1 if same_cluster and clusters else 0
        candidates.append((cluster_penalty, abs(left.elo - right.elo), left, right))
    candidates.sort(key=lambda item: (item[0], item[1]))
    return [(left, right) for _, _, left, right in candidates[:max_pairs]]
