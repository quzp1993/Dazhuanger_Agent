from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
import json
from pathlib import Path
from typing import Any
from uuid import uuid4


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:10]}"


@dataclass
class Hypothesis:
    id: str
    text: str
    source: str
    parent_ids: list[str] = field(default_factory=list)
    elo: float = 1200.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))


@dataclass
class Review:
    id: str
    hypothesis_id: str
    text: str
    novelty: int | None = None
    plausibility: int | None = None
    testability: int | None = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))


@dataclass
class Match:
    id: str
    hypothesis_a: str
    hypothesis_b: str
    winner: str
    rationale: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))


@dataclass
class ProximityPair:
    hypothesis_a: str
    hypothesis_b: str
    similarity: float


@dataclass
class Memory:
    goal: str
    preferences: str
    hypotheses: list[Hypothesis] = field(default_factory=list)
    reviews: list[Review] = field(default_factory=list)
    matches: list[Match] = field(default_factory=list)
    meta_reviews: list[str] = field(default_factory=list)
    clusters: dict[str, int] = field(default_factory=dict)
    proximity_pairs: list[ProximityPair] = field(default_factory=list)

    def add_hypothesis(self, text: str, source: str, parent_ids: list[str] | None = None) -> Hypothesis:
        hypothesis = Hypothesis(
            id=new_id("hyp"),
            text=text.strip(),
            source=source,
            parent_ids=parent_ids or [],
        )
        self.hypotheses.append(hypothesis)
        return hypothesis

    def add_review(
        self,
        hypothesis_id: str,
        text: str,
        novelty: int | None = None,
        plausibility: int | None = None,
        testability: int | None = None,
    ) -> Review:
        review = Review(
            id=new_id("rev"),
            hypothesis_id=hypothesis_id,
            text=text.strip(),
            novelty=novelty,
            plausibility=plausibility,
            testability=testability,
        )
        self.reviews.append(review)
        return review

    def add_match(self, hypothesis_a: str, hypothesis_b: str, winner: str, rationale: str) -> Match:
        match = Match(
            id=new_id("match"),
            hypothesis_a=hypothesis_a,
            hypothesis_b=hypothesis_b,
            winner=winner,
            rationale=rationale.strip(),
        )
        self.matches.append(match)
        return match

    def hypothesis_by_id(self, hypothesis_id: str) -> Hypothesis:
        for hypothesis in self.hypotheses:
            if hypothesis.id == hypothesis_id:
                return hypothesis
        raise KeyError(hypothesis_id)

    def reviews_for(self, hypothesis_id: str) -> list[Review]:
        return [review for review in self.reviews if review.hypothesis_id == hypothesis_id]

    def top_hypotheses(self, n: int = 5) -> list[Hypothesis]:
        return sorted(self.hypotheses, key=lambda item: item.elo, reverse=True)[:n]

    def cluster_for(self, hypothesis_id: str) -> int | None:
        return self.clusters.get(hypothesis_id)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def save(self, path: Path) -> None:
        path.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
