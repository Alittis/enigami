"""Run probes and record everything.

Ordering matters: the pre-registration is written to disk and flushed before the first API
call of the run. If the manifest's mtime is later than the first event, the run is suspect.
`enigami verify` checks exactly that.
"""

from __future__ import annotations

import json
import os
import platform
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import config, refute
from .client import ProbeError, Subject
from .probe import Context, Finding, Probe


@dataclass
class RunResult:
    probe_id: str
    run_id: str
    directory: Path
    finding: Finding | None
    refutation: Any = None
    error: str | None = None
    cost_usd: float = 0.0
    calls: int = 0
    offline: bool = False
    elapsed_s: float = 0.0
    survived: bool | None = field(default=None)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Run:
    def __init__(self, probe: Probe, *, offline: bool = False, seed: int = 1729,
                 subject_model: str | None = None, workers: int = 6):
        self.probe = probe
        self.offline = offline
        self.seed = seed
        self.workers = workers
        self.subject_model = subject_model or config.SUBJECT_MODEL
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        self.run_id = f"{stamp}-{probe.id}"
        self.dir = config.TRANSCRIPTS / self.run_id
        self._events: Any = None

    # -- transcript -------------------------------------------------------
    def _open(self) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        manifest = {
            "run_id": self.run_id,
            "probe": self.probe.id,
            "domain": self.probe.domain,
            "title": self.probe.title,
            "started_at": _now(),
            "offline": self.offline,
            "seed": self.seed,
            "subject_model": self.subject_model,
            "judge_model": config.JUDGE_MODEL,
            "preregistration": self.probe.prereg.as_dict(),
            "host": {"python": platform.python_version(), "platform": platform.platform()},
        }
        path = self.dir / "manifest.json"
        with open(path, "w") as fh:
            json.dump(manifest, fh, indent=2)
            fh.flush()
            os.fsync(fh.fileno())          # prereg is durable before any call goes out
        time.sleep(0.01)                    # guarantee a distinct mtime from the first event
        self._events = open(self.dir / "events.jsonl", "a")

    def log(self, event: str, data: dict | None = None, **kw) -> None:
        # Context passes a dict positionally; the runner passes keywords. Accept both.
        record = {"t": _now(), "event": event, **(data or {}), **kw}
        self._events.write(json.dumps(record, default=str) + "\n")
        self._events.flush()

    # -- execution --------------------------------------------------------
    def execute(self) -> RunResult:
        self._open()
        started = time.time()
        subject = Subject(self.subject_model, offline=self.offline)
        judge = Subject(config.JUDGE_MODEL, offline=self.offline)
        ctx = Context(subject, judge, self.log, workers=self.workers)
        ctx.seed = self.seed  # probes that shuffle read this

        result = RunResult(
            probe_id=self.probe.id, run_id=self.run_id, directory=self.dir,
            finding=None, offline=self.offline,
        )
        try:
            finding = self.probe.run(ctx)
            if not isinstance(finding, Finding):
                raise ProbeError(f"{self.probe.id}.run returned {type(finding).__name__}, not a Finding")
            self.log("finding", **finding.as_dict())
            result.finding = finding

            refutation = refute.challenge(ctx, self.probe, finding)
            result.refutation = refutation
            result.survived = (
                not refutation.is_likely_artifact and refutation.survives_probability >= 0.5
            )
        except ProbeError as e:
            result.error = str(e)
            self.log("error", kind="ProbeError", message=str(e))
        except Exception as e:  # noqa: BLE001 - a crashed probe must not kill the batch
            result.error = f"{type(e).__name__}: {e}"
            self.log("error", kind=type(e).__name__, message=str(e))

        result.elapsed_s = round(time.time() - started, 1)
        result.cost_usd = round(subject.total_cost + judge.total_cost, 4)
        result.calls = len(subject.calls) + len(judge.calls)

        payload = {
            "run_id": self.run_id,
            "probe": self.probe.id,
            "domain": self.probe.domain,
            "title": self.probe.title,
            "offline": self.offline,
            "finished_at": _now(),
            "elapsed_s": result.elapsed_s,
            "cost_usd": result.cost_usd,
            "calls": result.calls,
            "error": result.error,
            "preregistration": self.probe.prereg.as_dict(),
            "finding": result.finding.as_dict() if result.finding else None,
            "refutation": result.refutation.model_dump() if result.refutation else None,
            "survived_refutation": result.survived,
        }
        (self.dir / "result.json").write_text(json.dumps(payload, indent=2, default=str))
        (self.dir / "calls.json").write_text(
            json.dumps({"subject": subject.calls, "judge": judge.calls}, indent=2, default=str)
        )
        self._events.close()
        return result


def latest_results() -> list[dict]:
    """Most recent result.json per probe id, newest first."""
    by_probe: dict[str, tuple[str, dict]] = {}
    for path in sorted(config.TRANSCRIPTS.glob("*/result.json")):
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        rid = data.get("run_id", "")
        probe = data.get("probe", "")
        if probe not in by_probe or rid > by_probe[probe][0]:
            by_probe[probe] = (rid, data)
    return [d for _, d in sorted(by_probe.values(), key=lambda x: x[0], reverse=True)]


def verify_ordering(run_dir: Path) -> tuple[bool, str]:
    """Check the pre-registration predates the run's first recorded event."""
    manifest, events = run_dir / "manifest.json", run_dir / "events.jsonl"
    if not manifest.exists():
        return False, "no manifest.json — pre-registration missing"
    if not events.exists():
        return True, "no events recorded"
    if manifest.stat().st_mtime > events.stat().st_mtime:
        return False, "manifest.json is newer than events.jsonl — prereg may have been edited after the run"
    return True, "prereg predates first event"
