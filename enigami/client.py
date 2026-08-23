"""Thin wrapper over the Messages API, plus an offline stub for plumbing tests.

Two things here are load-bearing for the method, not just convenience:

1. `Subject.ask` refuses `temperature` / `top_p` / `top_k`. They were removed from the
   current model family and return a 400. That matters here because "vary the temperature"
   is the obvious way to study output diversity, and it is not available — the creativity
   probes get their variance from independent resampling instead. Failing loudly beats a
   confusing 400 three probes later.

2. Every call is recorded with its usage, cost and request id, so a finding can be traced
   back to the exact exchanges that produced it.
"""

from __future__ import annotations

import copy
import json
import os
import threading
from dataclasses import dataclass, field
from typing import Any

from . import config


@dataclass
class Reply:
    text: str
    thinking: str = ""
    model: str = ""
    stop_reason: str | None = None
    refusal_category: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    request_id: str | None = None

    @property
    def refused(self) -> bool:
        return self.stop_reason == "refusal"

    def as_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "thinking": self.thinking,
            "model": self.model,
            "stop_reason": self.stop_reason,
            "refusal_category": self.refusal_category,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost_usd": round(self.cost_usd, 6),
            "request_id": self.request_id,
        }


class ProbeError(RuntimeError):
    """Raised for conditions that invalidate a probe run rather than just a call."""


def strict_schema(model: type) -> dict[str, Any]:
    """Pydantic model -> a strict JSON Schema the API will accept.

    Inlines `$defs`/`$ref` and forces `additionalProperties: false` with every property
    required, which is what `json_schema` output format expects.
    """
    raw = model.model_json_schema()
    defs = raw.pop("$defs", {})

    def resolve(node: Any) -> Any:
        if isinstance(node, list):
            return [resolve(n) for n in node]
        if not isinstance(node, dict):
            return node
        if "$ref" in node:
            name = node["$ref"].rsplit("/", 1)[-1]
            merged = copy.deepcopy(defs[name])
            merged.update({k: v for k, v in node.items() if k != "$ref"})
            return resolve(merged)
        out = {k: resolve(v) for k, v in node.items()}
        if out.get("type") == "object" and "properties" in out:
            out["additionalProperties"] = False
            out["required"] = list(out["properties"].keys())
        return out

    return resolve(raw)


class Subject:
    """The thing under investigation. Also used as the judge, with a different model/effort."""

    def __init__(self, model: str = config.SUBJECT_MODEL, *, offline: bool = False):
        self.model = model
        self.offline = offline
        self._lock = threading.Lock()
        self.calls: list[dict[str, Any]] = []
        self.total_cost = 0.0
        self._client = None if offline else self._build_client()

    @staticmethod
    def _build_client():
        import anthropic

        config.load_env()
        if not config.have_credentials():
            raise ProbeError(
                "No Anthropic credentials found.\n"
                "Run:  ./deploy/scripts/setup-anthropic-env.sh\n"
                "Or run any command with --offline to exercise the harness without the API."
            )
        return anthropic.Anthropic(max_retries=4)

    def ask(
        self,
        prompt: str,
        *,
        system: str | None = None,
        model: str | None = None,
        effort: str = "high",
        max_tokens: int = 8000,
        schema: type | None = None,
        thinking: bool = True,
        label: str = "",
        **kwargs: Any,
    ) -> Reply:
        for bad in config.FORBIDDEN_PARAMS:
            if bad in kwargs:
                raise ProbeError(
                    f"`{bad}` was removed from the current Claude model family and returns a 400. "
                    "Vary independent samples instead (see enigami/client.py docstring)."
                )
        model = model or self.model

        if self.offline:
            reply = _stub_reply(prompt, model, schema)
        else:
            reply = self._live(prompt, system, model, effort, max_tokens, schema, thinking)

        with self._lock:
            self.total_cost += reply.cost_usd
            self.calls.append({"label": label, "model": model, **reply.as_dict()})
        return reply

    def _live(self, prompt, system, model, effort, max_tokens, schema, thinking) -> Reply:
        import anthropic

        output_config: dict[str, Any] = {"effort": effort}
        if schema is not None:
            output_config["format"] = {"type": "json_schema", "schema": strict_schema(schema)}

        req: dict[str, Any] = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
            "output_config": output_config,
        }
        if system:
            req["system"] = system
        if thinking:
            req["thinking"] = {"type": "adaptive", "display": "summarized"}

        try:
            resp = self._client.messages.create(**req)
        except anthropic.BadRequestError as e:
            raise ProbeError(f"Bad request for model {model}: {e}") from e
        except anthropic.AuthenticationError as e:
            raise ProbeError("Anthropic rejected the API key. Re-run setup-anthropic-env.sh.") from e
        except anthropic.RateLimitError as e:
            raise ProbeError(f"Rate limited after retries: {e}") from e
        except anthropic.APIStatusError as e:
            raise ProbeError(f"API error {e.status_code}: {e.message}") from e
        except anthropic.APIConnectionError as e:
            raise ProbeError(f"Network error reaching the API: {e}") from e

        text = "".join(b.text for b in resp.content if b.type == "text")
        think = "".join(getattr(b, "thinking", "") for b in resp.content if b.type == "thinking")
        u = resp.usage
        cache_read = getattr(u, "cache_read_input_tokens", 0) or 0
        cache_write = getattr(u, "cache_creation_input_tokens", 0) or 0

        category = None
        if resp.stop_reason == "refusal" and getattr(resp, "stop_details", None):
            category = getattr(resp.stop_details, "category", None)

        return Reply(
            text=text,
            thinking=think,
            model=resp.model,
            stop_reason=resp.stop_reason,
            refusal_category=category,
            input_tokens=u.input_tokens,
            output_tokens=u.output_tokens,
            cost_usd=config.cost_usd(model, u.input_tokens, u.output_tokens, cache_read, cache_write),
            request_id=resp._request_id,
        )

    def parse(self, prompt: str, schema: type, **kwargs: Any):
        """Ask for structured output and validate it. Raises ProbeError on a refusal."""
        reply = self.ask(prompt, schema=schema, **kwargs)
        if reply.refused:
            raise ProbeError(f"Refused ({reply.refusal_category}) — cannot score this call.")
        try:
            return schema.model_validate_json(reply.text), reply
        except Exception as e:
            raise ProbeError(f"Response did not validate against {schema.__name__}: {e}\n{reply.text[:400]}") from e


def _stub_value(spec: dict[str, Any]) -> Any:
    """Smallest value satisfying one resolved JSON-Schema node."""
    if "const" in spec:
        return spec["const"]
    if "enum" in spec:
        return spec["enum"][0]
    for branch in spec.get("anyOf", spec.get("oneOf", [])):
        if branch.get("type") != "null":
            return _stub_value(branch)
    kind = spec.get("type")
    if kind == "object":
        return {k: _stub_value(v) for k, v in spec.get("properties", {}).items()}
    if kind == "array":
        n = spec.get("minItems", 0)
        return [_stub_value(spec.get("items", {}))] * n
    if kind == "integer":
        return int(spec.get("minimum", 1))
    if kind == "number":
        lo, hi = spec.get("minimum", 0.0), spec.get("maximum", 1.0)
        return float(min(max(0.5, lo), hi))
    if kind == "boolean":
        return False
    return "offline-stub"


def _stub_reply(prompt: str, model: str, schema: type | None) -> Reply:
    """Deterministic offline responder, so the pipeline can be exercised with no key.

    It is not a model and never stands in for one — `--offline` runs are marked
    `offline: true` in the manifest and are refused by the report writer.
    """
    if schema is not None:
        text = json.dumps(_stub_value(strict_schema(schema)))
    else:
        text = f"offline-stub reply to a {len(prompt)}-char prompt"
    return Reply(text=text, model=f"{model}(offline)", stop_reason="end_turn")
