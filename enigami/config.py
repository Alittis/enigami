"""Model registry, pricing, and environment loading.

Pricing is USD per 1M tokens, from the Anthropic pricing table cached 2026-06-24.
It is used only for local cost estimates in run manifests — never for billing.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRANSCRIPTS = REPO_ROOT / "transcripts"
FINDINGS = REPO_ROOT / "findings"
PROBES = REPO_ROOT / "probes"

DOMAINS = ("intelligence", "wisdom", "creativity", "imagination")


@dataclass(frozen=True)
class Model:
    id: str
    input_per_mtok: float
    output_per_mtok: float


MODELS: dict[str, Model] = {
    "claude-opus-5": Model("claude-opus-5", 5.00, 25.00),
    "claude-opus-4-8": Model("claude-opus-4-8", 5.00, 25.00),
    "claude-sonnet-5": Model("claude-sonnet-5", 3.00, 15.00),
    "claude-haiku-4-5": Model("claude-haiku-4-5", 1.00, 5.00),
    "claude-fable-5": Model("claude-fable-5", 10.00, 50.00),
}

#: The model under investigation. Every probe runs against this unless it says otherwise.
SUBJECT_MODEL = "claude-opus-5"

#: The model that scores blind comparisons. Deliberately the same tier as the subject:
#: a weaker judge cannot detect a stronger subject's failures, which would bias every
#: probe toward "supports". See project/ARCHITECTURE.md section 4.
JUDGE_MODEL = "claude-opus-5"

#: Effort for judging and refutation. High, because a lazy judge is a flattering judge.
JUDGE_EFFORT = "high"

#: Sampling parameters do not exist on the current model family. See client.py.
FORBIDDEN_PARAMS = ("temperature", "top_p", "top_k")


def cost_usd(model_id: str, input_tokens: int, output_tokens: int,
             cache_read: int = 0, cache_write: int = 0) -> float:
    """Estimate USD for one call. Cache reads bill ~0.1x, cache writes ~1.25x."""
    m = MODELS.get(model_id)
    if m is None:
        return 0.0
    return (
        input_tokens * m.input_per_mtok
        + cache_read * m.input_per_mtok * 0.10
        + cache_write * m.input_per_mtok * 1.25
        + output_tokens * m.output_per_mtok
    ) / 1_000_000


def load_env(path: Path | None = None) -> None:
    """Load KEY=VALUE lines from .env into os.environ without overwriting real env vars.

    Deliberately not python-dotenv: one file, one format, no dependency.
    """
    env_file = path or (REPO_ROOT / ".env")
    if not env_file.exists():
        return
    for raw in env_file.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


def have_credentials() -> bool:
    load_env()
    return bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"))
