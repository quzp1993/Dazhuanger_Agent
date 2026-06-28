# Prompt Design

The prompts are simplified versions of the roles described in the Co-Scientist
supplementary material.

## Generation

The generation prompt asks for distinct, novel, testable hypotheses with:

- title
- causal mechanism
- novelty rationale
- minimal experiment

The outsider generation prompt is used every configured interval. It summarizes
dominant clusters and asks for hypotheses that are intentionally different while
remaining plausible and testable. This prompt is the main exploration mechanism
for escaping local optima.

## Reflection

The reflection prompt asks for peer-review style critique:

- plausibility
- novelty risk
- testability
- missing evidence
- safety or ethical concerns

It ends with structured scores:

```text
Novelty: <1-5>
Plausibility: <1-5>
Testability: <1-5>
```

## Ranking

The ranking prompt uses a structured debate rather than a direct "A or B?"
question. This helps reduce position bias and forces explicit comparison of:

- correctness
- novelty
- feasibility
- specificity
- experimental value

It ends with:

```text
better idea: <1 or 2>
```

## Proximity

The proximity step does not call an LLM. It tokenizes hypothesis text, computes
cosine similarity, and clusters hypotheses above a similarity threshold. These
clusters guide ranking and evolution so the loop keeps exploring distinct
mechanistic themes.

## Evolution

The evolution prompt improves top hypotheses by:

- strengthening mechanisms
- making experiments concrete
- combining related ideas
- using analogy from adjacent domains
- simplifying claims

Evolution receives cluster-diverse seed hypotheses, not only the top global Elo
hypotheses. This reduces local-optimum behavior.

## Meta-review

The meta-review prompt turns the top hypotheses and reviews into a final research
overview with ranked hypotheses, rationale, weaknesses, and next experiments.
