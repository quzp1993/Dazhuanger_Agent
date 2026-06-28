---
name: co-scientist-loop
description: Build, run, explain, or modify a lightweight Co-Scientist style scientific hypothesis loop with Generation, Reflection, Proximity, Ranking/Elo, Evolution, and Meta-review agents. Use when the user asks to create multi-agent research workflows, generate and rank scientific hypotheses, avoid local optima with diversity-aware clustering, run the local `co_scientist_loop` prototype, adapt prompts, debug provider configuration, or interpret `memory.json` and `final_report.md` outputs.
---

# Co-Scientist Loop

## Overview

Use this skill to operate a lightweight multi-agent scientific reasoning loop. The loop is a practical prototype of the Co-Scientist pattern: generate hypotheses, review them, cluster similar ideas, compare them through a ranking tournament, evolve strong and diverse ideas, and synthesize a final report.

## Workflow

1. Clarify the research goal and any constraints.
2. Choose a provider: `mock`, `openai`, or `anthropic`.
3. Start small: `--rounds 2 --initial-count 2 --evolved-count 1 --matches-per-round 2`.
4. Inspect `memory.json` for hypotheses, reviews, matches, Elo scores, and proximity clusters.
5. Inspect `final_report.md` for the synthesized scientific overview.
6. Increase rounds and counts only after the provider is stable.
7. For local-optimum avoidance, tune `--proximity-threshold`, `--max-evolution-seeds-per-cluster`, `--outsider-count`, and `--outsider-every`.

## Commands

Mock run:

```powershell
python -m co_scientist_loop --goal "YOUR_RESEARCH_QUESTION" --rounds 2
```

OpenAI-compatible run:

```powershell
python -m co_scientist_loop --goal "Your research question" --rounds 2 --provider openai
```

Anthropic-compatible run:

```powershell
python -m co_scientist_loop --goal "Your research question" --rounds 2 --provider anthropic
```

## Provider Configuration

Read keys from `co_scientist_loop/.env`. Never print or commit API keys.

OpenAI-compatible:

```env
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-4.1-mini
```

Anthropic-compatible:

```env
ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
ANTHROPIC_AUTH_TOKEN=your_key
ANTHROPIC_MODEL=deepseek-v4-pro
```

Long-run reliability:

```env
LLM_REQUEST_TIMEOUT_SECONDS=600
LLM_MAX_RETRIES=3
LLM_RETRY_BASE_SECONDS=3
```

Diversity-focused run:

```powershell
python -m co_scientist_loop --goal "YOUR_RESEARCH_QUESTION" --rounds 20 --proximity-threshold 0.55 --max-evolution-seeds-per-cluster 1 --outsider-count 2 --outsider-every 2
```

## Output Review

When explaining results:

- Treat hypotheses as speculative.
- Use Elo as a prioritization signal, not proof.
- Use proximity clusters to explain whether the loop explored multiple mechanism families.
- Cite the strongest hypothesis, key weaknesses, and recommended experiments.
- Use `memory.json` when the user asks how a conclusion was reached.

## References

- Read `references/workflow.md` when changing loop parameters, debugging runs, or explaining the end-to-end workflow.
