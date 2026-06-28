# Dazhuanger Agent

Lightweight Co-Scientist style multi-agent loop for scientific hypothesis generation.

Dazhuanger Agent is a scientist agent project for AI for Science.

This repository contains a small, readable prototype inspired by Google DeepMind's
Co-Scientist paper. It is designed for journal club demos, lab exploration, and
rapid experimentation with scientific-reasoning agents.

## What It Does

The loop runs five agent roles:

```text
Generation -> Reflection -> Proximity -> Ranking/Elo -> Evolution -> Meta-review
```

- **Generation** creates candidate research hypotheses.
- **Reflection** reviews plausibility, novelty risk, testability, and missing evidence.
- **Proximity** clusters similar hypotheses and helps preserve diversity.
- **Ranking** compares hypotheses through a structured debate prompt and updates Elo scores.
- **Evolution** improves top-ranked hypotheses into clearer, stronger, more testable variants.
- **Meta-review** synthesizes the final ranked research overview.

This is not a full reproduction of Co-Scientist. It is a compact implementation of
the core loop so researchers can inspect, modify, and extend the workflow.

The Proximity step is included to reduce local-optimum behavior: the loop avoids
evolving only the single highest-Elo theme by selecting promising hypotheses
across multiple similarity clusters. It can also periodically generate
**outsider hypotheses** that are intentionally different from the dominant
clusters.

## Quick Start

Run with the built-in mock model:

```powershell
python -m co_scientist_loop --goal "YOUR_RESEARCH_QUESTION" --rounds 2
```

Run with an OpenAI-compatible endpoint:

```powershell
python -m co_scientist_loop --goal "Your research question" --rounds 2 --provider openai
```

Run with an Anthropic-compatible endpoint:

```powershell
python -m co_scientist_loop --goal "Your research question" --rounds 2 --provider anthropic
```

## Configuration

Copy `.env.example` to `co_scientist_loop/.env` and fill in your provider settings.
Never commit real API keys.

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
ANTHROPIC_SMALL_FAST_MODEL=deepseek-v4-pro
```

## Example

```powershell
python -m co_scientist_loop `
  --goal "YOUR_RESEARCH_QUESTION" `
  --rounds 2 `
  --initial-count 2 `
  --evolved-count 1 `
  --matches-per-round 2 `
  --proximity-threshold 0.5 `
  --max-evolution-seeds-per-cluster 2 `
  --outsider-count 1 `
  --outsider-every 3 `
  --provider anthropic `
  --out runs\example_run
```

Outputs are written to the selected run directory:

- `memory.json`: hypotheses, reviews, matches, Elo scores, and meta-reviews
- `final_report.md`: final synthesized research overview

## Documentation

- [Architecture](docs/architecture.md)
- [Usage Guide](docs/usage.md)
- [Prompt Design](docs/prompts.md)
- [Skill Guide](skills/co-scientist-loop/SKILL.md)

## Safety Notes

Treat all generated hypotheses as speculative. Use this loop for ideation and
research planning, not as scientific proof. Validate claims through literature
review, expert judgment, and experiments.
