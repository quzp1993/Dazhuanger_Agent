# Usage Guide

## Mock Run

Use this first to verify the workflow without network or API cost:

```powershell
python -m co_scientist_loop --goal "YOUR_RESEARCH_QUESTION" --rounds 2
```

## Real Model Run

Create `co_scientist_loop/.env` from `.env.example`, then choose a provider.

OpenAI-compatible:

```powershell
python -m co_scientist_loop --goal "Your research question" --rounds 2 --provider openai
```

Anthropic-compatible:

```powershell
python -m co_scientist_loop --goal "Your research question" --rounds 2 --provider anthropic
```

## Runtime Controls

- `--rounds`: number of ranking/evolution cycles
- `--initial-count`: initial hypotheses to generate
- `--evolved-count`: evolved hypotheses per round
- `--matches-per-round`: pairwise ranking matches per round
- `--provider`: `mock`, `openai`, or `anthropic`
- `--out`: output directory
- `--proximity-threshold`: similarity threshold for clustering
- `--max-evolution-seeds-per-cluster`: cap Evolution seeds from one cluster
- `--outsider-count`: outsider hypotheses to generate periodically
- `--outsider-every`: generate outsiders every N rounds; `0` disables it

For slow or expensive models, start small:

```powershell
python -m co_scientist_loop `
  --goal "Your research question" `
  --rounds 2 `
  --initial-count 2 `
  --evolved-count 1 `
  --matches-per-round 2 `
  --outsider-count 1 `
  --outsider-every 3 `
  --provider anthropic
```

## Output Interpretation

`final_report.md` is a model-generated synthesis, not a validated scientific
result. Use `memory.json` to inspect the full path: each hypothesis, review,
match rationale, Elo change, proximity cluster, and similar-hypothesis pairs.

## Avoiding Local Optima

The loop includes a local Proximity Agent. It clusters similar hypotheses and
uses those clusters to:

- prefer ranking comparisons across different hypothesis themes
- choose Evolution seeds from multiple clusters instead of only the global top Elo
- expose cluster IDs in `memory.json` and meta-review materials

For long diversity-focused runs:

```powershell
python -m co_scientist_loop `
  --goal "YOUR_RESEARCH_QUESTION" `
  --rounds 20 `
  --provider anthropic `
  --proximity-threshold 0.55 `
  --max-evolution-seeds-per-cluster 1 `
  --outsider-count 2 `
  --outsider-every 2
```

The stricter cluster cap and more frequent outsider generation help prevent the
loop from converging too early on one mechanism family.

## Reliability Controls

Set these in `.env` for long API runs:

```env
LLM_REQUEST_TIMEOUT_SECONDS=600
LLM_MAX_RETRIES=3
LLM_RETRY_BASE_SECONDS=3
```

The loop checkpoints `memory.json` after reviews, matches, and proximity updates,
so partial results are preserved if a long run stops.
