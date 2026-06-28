from __future__ import annotations

import json
import os
from pathlib import Path
import re
import time
from http.client import IncompleteRead
from urllib.error import HTTPError, URLError
from urllib import request


class LLMClient:
    def complete(self, prompt: str) -> str:
        raise NotImplementedError


class MockLLMClient(LLMClient):
    """Deterministic placeholder so the loop can run without external services."""

    def complete(self, prompt: str) -> str:
        lower = prompt.lower()
        if "generate" in lower and "hypotheses" in lower:
            return (
                "1. Stress-state selective vulnerability: A disease cell subset may depend on a stress-response pathway; inhibiting it should reduce viability selectively. Minimal experiment: dose-response assay across matched cell lines.\n"
                "2. Microenvironment-mediated resistance: A stromal or immune signal may protect diseased cells from standard treatment. Minimal experiment: co-culture perturbation with pathway readouts.\n"
                "3. Combination rescue blockade: Pairing a pathway inhibitor with standard therapy may block a compensatory survival route. Minimal experiment: matrix combination assay and Bliss/HSA synergy scoring."
            )
        if "peer-review" in lower or "critically review" in lower:
            return (
                "The hypothesis is plausible if the dependency is stronger in the target cell state than controls. The main novelty risk is that the pathway may already be studied in adjacent diseases. Testability is good because dose-response and perturbation assays are straightforward. Missing evidence includes direct target engagement and biomarkers.\n"
                "Novelty: 3\nPlausibility: 4\nTestability: 5"
            )
        if "better idea" in lower:
            if "hypothesis 1" in lower and "hypothesis 2" in lower:
                return "Hypothesis 1 is more concrete and easier to test, while hypothesis 2 is broader but less specific.\nbetter idea: 1"
            return "better idea: 1"
        if "improved hypotheses" in lower:
            return (
                "1. Biomarker-guided stress vulnerability: Test whether high baseline stress-response markers predict selective sensitivity to pathway inhibition using target engagement and viability assays.\n"
                "2. Mechanism-led combination therapy: Combine a stress-pathway inhibitor with standard therapy to block compensatory survival, then quantify synergy and apoptosis markers."
            )
        return (
            "# Final research overview\n\n"
            "The strongest direction is to prioritize hypotheses with clear mechanisms, measurable biomarkers, and simple validation assays. Next experiments should start with dose-response, target engagement, and control-cell selectivity."
        )


class OpenAICompatibleClient(LLMClient):
    def __init__(self, model: str | None = None, base_url: str | None = None, api_key: str | None = None) -> None:
        load_local_env()
        self.model = model or os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for provider=openai")

    def complete(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a careful scientific reasoning assistant."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.4,
        }
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            f"{self.base_url}/chat/completions",
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        body = post_json_with_retries(req, "OpenAI-compatible")
        return body["choices"][0]["message"]["content"]


class AnthropicCompatibleClient(LLMClient):
    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
    ) -> None:
        load_local_env()
        self.model = (
            model
            or os.environ.get("ANTHROPIC_MODEL")
            or os.environ.get("ANTHROPIC_SMALL_FAST_MODEL")
            or "claude-3-5-haiku-latest"
        )
        self.base_url = (
            base_url
            or os.environ.get("ANTHROPIC_BASE_URL")
            or "https://api.anthropic.com"
        ).rstrip("/")
        self.api_key = (
            api_key
            or os.environ.get("ANTHROPIC_AUTH_TOKEN")
            or os.environ.get("ANTHROPIC_API_KEY")
        )
        if not self.api_key:
            raise ValueError("ANTHROPIC_AUTH_TOKEN or ANTHROPIC_API_KEY is required for provider=anthropic")

    def complete(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
        }
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            f"{self.base_url}/v1/messages",
            data=data,
            headers={
                "x-api-key": self.api_key,
                "Authorization": f"Bearer {self.api_key}",
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        body = post_json_with_retries(req, "Anthropic-compatible")
        content = body.get("content", [])
        if content and isinstance(content, list):
            text_parts = [part.get("text", "") for part in content if isinstance(part, dict)]
            return "\n".join(part for part in text_parts if part)
        if "choices" in body:
            return body["choices"][0]["message"]["content"]
        return json.dumps(body, ensure_ascii=False)


def make_client(provider: str) -> LLMClient:
    if provider == "mock":
        return MockLLMClient()
    if provider == "openai":
        return OpenAICompatibleClient()
    if provider == "anthropic":
        return AnthropicCompatibleClient()
    raise ValueError(f"Unknown provider: {provider}")


def request_timeout_seconds() -> int:
    raw_value = os.environ.get("LLM_REQUEST_TIMEOUT_SECONDS", "300")
    try:
        return max(30, int(raw_value))
    except ValueError:
        return 300


def max_retries() -> int:
    raw_value = os.environ.get("LLM_MAX_RETRIES", "2")
    try:
        return max(0, int(raw_value))
    except ValueError:
        return 2


def retry_delay_seconds(attempt_index: int) -> float:
    raw_value = os.environ.get("LLM_RETRY_BASE_SECONDS", "3")
    try:
        base = max(0.5, float(raw_value))
    except ValueError:
        base = 3.0
    return base * (2 ** attempt_index)


def post_json_with_retries(req: request.Request, provider_name: str) -> dict:
    attempts = max_retries() + 1
    last_error: Exception | None = None
    for attempt_index in range(attempts):
        try:
            with request.urlopen(req, timeout=request_timeout_seconds()) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            if exc.code in {401, 402, 403, 404} or attempt_index >= attempts - 1:
                raise RuntimeError(f"{provider_name} API returned HTTP {exc.code}: {detail}") from exc
            last_error = RuntimeError(f"{provider_name} API returned HTTP {exc.code}: {detail}")
        except (TimeoutError, IncompleteRead, URLError) as exc:
            if attempt_index >= attempts - 1:
                raise RuntimeError(f"{provider_name} API request failed after {attempts} attempts: {exc}") from exc
            last_error = exc
        time.sleep(retry_delay_seconds(attempt_index))
    raise RuntimeError(f"{provider_name} API request failed: {last_error}")


def load_local_env() -> None:
    """Load simple KEY=VALUE pairs from local .env files without extra dependencies."""
    candidates = [Path(".env"), Path("co_scientist_loop") / ".env"]
    for path in candidates:
        if not path.exists():
            continue
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            if key.startswith("export "):
                key = key.removeprefix("export ").strip()
            if key.startswith("$env:"):
                key = key.removeprefix("$env:")
            value = value.strip().strip('"').strip("'")
            os.environ[key] = value


def numbered_items(text: str) -> list[str]:
    matches = re.split(r"\n\s*\d+[\).\s]+", "\n" + text.strip())
    items = [item.strip(" -\n\t") for item in matches if item.strip(" -\n\t")]
    return items
