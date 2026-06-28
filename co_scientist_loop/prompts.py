GENERATION_PROMPT = """You are a scientific hypothesis generation agent.

Goal:
{goal}

Criteria for strong hypotheses:
{preferences}

Generate {count} distinct, novel, and testable research hypotheses. For each
hypothesis, include:
- a short title
- the causal mechanism
- why it may be novel
- a minimal experiment that could test it

Return the hypotheses as a numbered list.
"""

OUTSIDER_GENERATION_PROMPT = """You are a scientific hypothesis generation agent tasked with escaping local optima.

Goal:
{goal}

Criteria for strong hypotheses:
{preferences}

Current dominant hypothesis themes:
{current_themes}

Generate {count} outsider hypotheses that are intentionally different from the
dominant themes above while still being plausible, testable, and mechanistically
specific. Avoid merely renaming the same mechanism.

For each hypothesis, include:
- a short title
- the causal mechanism
- why it differs from the current dominant themes
- a minimal experiment that could test it

Return the hypotheses as a numbered list.
"""

REFLECTION_PROMPT = """You are a scientific peer-review agent.

Goal:
{goal}

Evaluation criteria:
{preferences}

Hypothesis:
{hypothesis}

Critically review this hypothesis for:
1. plausibility
2. novelty risk
3. testability
4. missing evidence
5. safety or ethical concerns

End with integer scores from 1 to 5 in this exact format:
Novelty: <1-5>
Plausibility: <1-5>
Testability: <1-5>
"""

RANKING_PROMPT = """You are a ranking agent simulating a structured scientific debate.

Goal:
{goal}

Criteria:
{preferences}

Hypothesis 1:
{hypothesis_a}

Review of hypothesis 1:
{review_a}

Hypothesis 2:
{hypothesis_b}

Review of hypothesis 2:
{review_b}

Compare the two hypotheses through a concise debate. Consider correctness,
novelty, feasibility, specificity, and experimental value. Conclude with exactly
one final line:
better idea: <1 or 2>
"""

EVOLUTION_PROMPT = """You are an evolution agent that improves promising scientific hypotheses.

Goal:
{goal}

Criteria:
{preferences}

Top hypotheses:
{top_hypotheses}

Generate {count} improved hypotheses by doing one or more of:
- strengthening the mechanism
- making the experiment more concrete
- combining complementary ideas
- using analogy from related domains
- simplifying the hypothesis so it is easier to test

Return the improved hypotheses as a numbered list.
"""

META_REVIEW_PROMPT = """You are a meta-review agent.

Goal:
{goal}

Criteria:
{preferences}

Top hypotheses and reviews:
{materials}

Write a concise final research overview:
1. ranked hypotheses
2. strongest rationale
3. key weaknesses
4. recommended next experiments
"""
