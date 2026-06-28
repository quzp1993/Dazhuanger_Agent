# Architecture

The prototype is intentionally synchronous and inspectable. It keeps the main
ideas of Co-Scientist without reproducing the full production system.

## Loop

```text
scientist goal
  -> Generation
  -> Reflection
  -> Proximity
  -> Ranking Tournament
  -> Evolution
  -> Reflection of evolved hypotheses
  -> repeat
  -> Meta-review
```

## Components

### Shared Memory

`memory.json` stores:

- research goal and preferences
- hypotheses
- reviews
- ranking matches
- Elo scores
- proximity clusters and similar hypothesis pairs
- meta-review outputs

### Generation Agent

Generates initial hypotheses from the research goal and evaluation preferences.
Each hypothesis is expected to include a mechanism, novelty rationale, and
minimal test.

### Reflection Agent

Reviews each hypothesis for plausibility, novelty risk, testability, missing
evidence, and safety concerns. It extracts simple 1-5 scores when the model
returns them.

### Ranking Agent

Compares pairs of hypotheses using a scientific-debate style prompt. Pair
selection prefers cross-cluster comparisons when possible, then close Elo scores.
The winner receives an Elo increase and the loser receives an Elo decrease.

### Proximity Agent

Computes a lightweight local text-similarity graph with token cosine similarity.
Hypotheses above the similarity threshold are grouped into clusters. The clusters
are used to preserve diversity during pair selection and evolution.

The threshold is configurable. Higher values split broad mechanism families into
more clusters; lower values merge related hypotheses more aggressively.

### Evolution Agent

Takes top-ranked hypotheses and improves them by strengthening mechanisms,
combining complementary ideas, adding concrete experiments, or simplifying the
claim. Seed hypotheses are selected with cluster diversity rather than pure Elo
alone, reducing local-optimum convergence.

Every N rounds, Generation can also create outsider hypotheses from a prompt that
explicitly asks for mechanisms different from the dominant clusters.

### Meta-review Agent

Synthesizes the top hypotheses, reviews, and rankings into a final research
overview.

Long runs checkpoint `memory.json` after reviews, ranking matches, proximity
updates, and evolved hypothesis reviews, so partial progress survives API
timeouts or quota failures.

## Files

- `co_scientist_loop/main.py`: supervisor loop and CLI
- `co_scientist_loop/agents.py`: agent implementations
- `co_scientist_loop/prompts.py`: prompt templates
- `co_scientist_loop/ranking.py`: Elo update logic
- `co_scientist_loop/memory.py`: data model and JSON persistence
- `co_scientist_loop/proximity.py`: similarity scoring and cluster-aware selection
- `co_scientist_loop/llm.py`: mock, OpenAI-compatible, and Anthropic-compatible clients
