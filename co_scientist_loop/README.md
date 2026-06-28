# Lightweight Co-Scientist Loop

A small, hackable prototype inspired by the Co-Scientist paper. It runs a synchronous
research loop:

```text
Generation -> Reflection -> Proximity -> Ranking/Elo -> Evolution -> Meta-review
```

It is not a reproduction of Google's internal system. It is a teaching and lab
prototype that keeps the same core loop visible and easy to modify.

## Quick Start

Run without any API key first:

```powershell
python -m co_scientist_loop --goal "YOUR_RESEARCH_QUESTION" --rounds 2
```

Without a configured model provider, the loop uses a deterministic mock model so
you can inspect the workflow and generated files.

## Use A Real LLM

Set environment variables:

```powershell
$env:OPENAI_API_KEY="your_api_key"
$env:OPENAI_MODEL="gpt-4.1-mini"
python -m co_scientist_loop --goal "Your research goal" --rounds 2 --provider openai
```

For OpenAI-compatible endpoints, optionally set:

```powershell
$env:OPENAI_BASE_URL="https://api.openai.com/v1"
```

## Use An Anthropic-Compatible Endpoint

Some providers expose an Anthropic-compatible Messages API. Put these in
`co_scientist_loop/.env`:

```env
ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
ANTHROPIC_AUTH_TOKEN=your_new_token
ANTHROPIC_MODEL=deepseek-v4-pro
```

Then run:

```powershell
python -m co_scientist_loop --goal "Your research goal" --rounds 2 --provider anthropic
```

## Outputs

Each run writes to `runs/<timestamp>/`:

- `memory.json`: all hypotheses, reviews, comparisons, and Elo scores
- `final_report.md`: final synthesized report

## Structure

- `main.py`: command line entry point and supervisor loop
- `agents.py`: Generation, Reflection, Ranking, Evolution, Meta-review agents
- `proximity.py`: local similarity clusters for diversity-aware exploration
- `llm.py`: mock and OpenAI-compatible model clients
- `memory.py`: shared memory data model
- `ranking.py`: Elo updates and pair selection
- `prompts.py`: prompt templates adapted from the paper's supplementary material

## Diversity Controls

Use these options to reduce local-optimum convergence:

```powershell
python -m co_scientist_loop --goal "YOUR_RESEARCH_QUESTION" --rounds 20 --proximity-threshold 0.55 --max-evolution-seeds-per-cluster 1 --outsider-count 2 --outsider-every 2
```

For long API runs, set retry controls in `.env`:

```env
LLM_REQUEST_TIMEOUT_SECONDS=600
LLM_MAX_RETRIES=3
LLM_RETRY_BASE_SECONDS=3
```
