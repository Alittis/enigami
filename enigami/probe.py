"""Probe contract: pre-registration, findings, and discovery.

The one rule this file enforces in code rather than in prose: a probe cannot run without
declaring, up front, what result would refute it and what a system lacking the capacity
would produce. The runner writes that declaration to the transcript *before* the first API
call, so a finding can never be reverse-engineered from a result that happened to look good.

That is the whole anti-self-flattery mechanism. Everything else is bookkeeping.
"""

from __future__ import annotations

import importlib.util
import inspect
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

from . import config

SCORERS = ("deterministic", "blind-judge", "human")
VERDICTS = ("supports", "refutes", "inconclusive")

_MIN = 40  # characters — long enough that "n/a" and "TODO" cannot pass


@dataclass(frozen=True)
class Prereg:
    """Written before the probe runs. Checked at import time, not at run time."""

    question: str
    hypothesis: str
    falsifier: str
    null_model: str
    scorer: str

    def __post_init__(self) -> None:
        for name in ("question", "hypothesis", "falsifier", "null_model"):
            value = (getattr(self, name) or "").strip()
            if len(value) < _MIN:
                raise ValueError(
                    f"Prereg.{name} must be a real statement of at least {_MIN} characters "
                    f"(got {len(value)}). A probe without a stated {name} cannot be falsified, "
                    "which makes any result it produces unpublishable here."
                )
        if self.scorer not in SCORERS:
            raise ValueError(f"Prereg.scorer must be one of {SCORERS}, got {self.scorer!r}")

    def as_dict(self) -> dict[str, str]:
        return {
            "question": self.question,
            "hypothesis": self.hypothesis,
            "falsifier": self.falsifier,
            "null_model": self.null_model,
            "scorer": self.scorer,
        }


@dataclass
class Finding:
    verdict: str
    headline: str
    metrics: dict[str, Any] = field(default_factory=dict)
    evidence: list[str] = field(default_factory=list)
    caveats: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.verdict not in VERDICTS:
            raise ValueError(f"verdict must be one of {VERDICTS}, got {self.verdict!r}")

    def as_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict,
            "headline": self.headline,
            "metrics": self.metrics,
            "evidence": self.evidence,
            "caveats": self.caveats,
        }


class Context:
    """What a probe is handed: a subject, a judge, a log, and a thread pool."""

    def __init__(self, subject, judge, logger: Callable[[str, dict], None], workers: int = 6):
        self.subject = subject
        self.judge = judge
        self._log = logger
        self.workers = workers

    def log(self, event: str, **data: Any) -> None:
        self._log(event, data)

    def map(self, fn: Callable[[Any], Any], items: Sequence[Any]) -> list[Any]:
        """Run independent samples concurrently, preserving order."""
        if len(items) == 1:
            return [fn(items[0])]
        with ThreadPoolExecutor(max_workers=min(self.workers, len(items))) as pool:
            return list(pool.map(fn, items))


class Probe:
    """Subclass, set the four class attributes, implement `run`."""

    id: str = ""
    domain: str = ""
    title: str = ""
    prereg: Prereg
    est_calls: int = 0  # rough call count, so `list` can warn before an expensive run

    def run(self, ctx: Context) -> Finding:  # pragma: no cover - interface
        raise NotImplementedError

    # -- validation ------------------------------------------------------
    def validate(self) -> None:
        if not self.id:
            raise ValueError(f"{type(self).__name__} has no id")
        if self.domain not in config.DOMAINS:
            raise ValueError(f"{self.id}: domain must be one of {config.DOMAINS}, got {self.domain!r}")
        if not isinstance(getattr(self, "prereg", None), Prereg):
            raise ValueError(f"{self.id}: missing a Prereg block")


def discover(root: Path | None = None) -> dict[str, Probe]:
    """Load every probe module under probes/ and return {id: probe}.

    A probe module exposes a module-level `PROBE`. Import errors are fatal: a probe that
    cannot be loaded is a probe silently missing from the report.
    """
    root = root or config.PROBES
    found: dict[str, Probe] = {}
    for path in sorted(root.rglob("*.py")):
        if path.name.startswith("_"):
            continue
        # Module name mirrors the path so two probes can share a filename across domains.
        dotted = "probes." + ".".join(path.relative_to(root).with_suffix("").parts)
        spec = importlib.util.spec_from_file_location(dotted, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load probe module {path}")
        module = importlib.util.module_from_spec(spec)
        # Registered before exec: pydantic resolves postponed annotations through sys.modules.
        sys.modules[dotted] = module
        spec.loader.exec_module(module)
        probe = getattr(module, "PROBE", None)
        if probe is None:
            raise ImportError(f"{path} defines no module-level PROBE")
        if inspect.isclass(probe):
            probe = probe()
        probe.validate()
        if probe.id in found:
            raise ValueError(f"Duplicate probe id {probe.id!r} in {path}")
        found[probe.id] = probe
    return found


def select(probes: dict[str, Probe], targets: Iterable[str]) -> list[Probe]:
    """Resolve CLI targets: probe ids, domain names, or 'all'."""
    targets = list(targets) or ["all"]
    if "all" in targets:
        return list(probes.values())
    chosen: list[Probe] = []
    for t in targets:
        if t in probes:
            chosen.append(probes[t])
        elif t in config.DOMAINS:
            chosen.extend(p for p in probes.values() if p.domain == t)
        else:
            raise KeyError(
                f"Unknown probe or domain {t!r}. Known probes: {', '.join(sorted(probes))}; "
                f"domains: {', '.join(config.DOMAINS)}"
            )
    seen, unique = set(), []
    for p in chosen:
        if p.id not in seen:
            seen.add(p.id)
            unique.append(p)
    return unique
