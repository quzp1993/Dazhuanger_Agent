# Co-Scientist Loop Workflow

Use this reference when implementing or modifying a lightweight scientific
hypothesis loop.

## Minimal Run

1. Parse the user's research goal.
2. Generate initial hypotheses.
3. Review each hypothesis.
4. Cluster hypotheses with the Proximity Agent.
5. Compare hypothesis pairs with the ranking agent, preferring cross-cluster pairs when useful.
6. Update Elo scores after each comparison.
7. Evolve top cluster-diverse hypotheses.
8. Review evolved hypotheses.
9. Repeat for the requested number of rounds.
10. Write `memory.json` and `final_report.md`.

## Avoiding Local Optima

The Proximity Agent computes local text-similarity clusters. Use these clusters to
select evolution seeds across different mechanism families rather than only the
highest-Elo hypothesis. This keeps exploration broad when early ranking favors a
single theme.

Outsider generation periodically asks for hypotheses that differ from dominant
clusters. Use it when cluster counts show that most top hypotheses have collapsed
into one mechanism family.

## Practical Defaults

For demos:

```powershell
python -m co_scientist_loop --goal "..." --rounds 2 --initial-count 2 --evolved-count 1 --matches-per-round 2
```

For deeper runs:

```powershell
python -m co_scientist_loop --goal "..." --rounds 5 --initial-count 5 --evolved-count 3 --matches-per-round 8
```

For diversity-focused runs:

```powershell
python -m co_scientist_loop --goal "..." --rounds 20 --proximity-threshold 0.55 --max-evolution-seeds-per-cluster 1 --outsider-count 2 --outsider-every 2
```

## Debugging

- If no API key is available, use `--provider mock`.
- If OpenAI returns `insufficient_quota`, check project billing and quota.
- If OpenAI returns `unsupported_country_region_territory`, use a supported network or compatible endpoint.
- If an Anthropic-compatible endpoint returns 401, check that base URL, token, and model belong to the same provider.
- If a long run stops after an API timeout, inspect `memory.json` and use `python -m co_scientist_loop.finalize_local` for a local partial summary.
