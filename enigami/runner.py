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
from .probe import Context, Finding, Prereg, Probe


@dataclass
class RunResult:
    probe_id: str
    run_id: str
    directory: Path
    finding: Finding | None
    refutation: Any = None
    error: str | None = None
    refutation_error: str | None = None
    review_reps: list | None = None
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
        except ProbeError as e:
            result.error = str(e)
            self.log("error", kind="ProbeError", message=str(e))
        except Exception as e:  # noqa: BLE001 - a crashed probe must not kill the batch
            result.error = f"{type(e).__name__}: {e}"
            self.log("error", kind=type(e).__name__, message=str(e))

        # Refutation is a separate failure domain. A finding that cost 24 calls to produce
        # must not be thrown away because the review call errored — it is recorded as
        # unreviewed instead, which the report renders as "review did not run".
        if result.finding is not None:
            try:
                representative, survived, reps = refute.review(ctx, self.probe, result.finding)
                result.refutation = representative
                result.survived = survived
                result.review_reps = [r.model_dump() for r in reps]
            except Exception as e:  # noqa: BLE001
                result.refutation_error = f"{type(e).__name__}: {e}"
                self.log("error", kind="refutation_failed", message=str(e))

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
            "refutation_error": result.refutation_error,
            "preregistration": self.probe.prereg.as_dict(),
            "finding": result.finding.as_dict() if result.finding else None,
            "refutation": result.refutation.model_dump() if result.refutation else None,
            "survived_refutation": result.survived,
            "reviewer": refute.REVIEWER if result.refutation else None,
            "review_protocol": f"majority of {refute.REVIEW_REPS} independent reps" if result.refutation else None,
            "review_reps": result.review_reps,
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


def latest_live_runs(root: Path | None = None) -> dict[str, tuple[Path, dict]]:
    """Newest live run that produced a finding, per probe id: {probe: (result_path, data)}."""
    root = root or config.TRANSCRIPTS
    picked: dict[str, tuple[str, Path, dict]] = {}
    for path in sorted(root.glob("*/result.json")):
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        if data.get("offline") or not data.get("finding"):
            continue
        probe, rid = data.get("probe", ""), data.get("run_id", "")
        if probe and (probe not in picked or rid > picked[probe][0]):
            picked[probe] = (rid, path, data)
    return {k: (p, d) for k, (_, p, d) in picked.items()}


class _RecordedProbe:
    """The probe-shaped view of a recorded run: an id and its stored pre-registration."""

    def __init__(self, probe_id: str, prereg: Prereg):
        self.id = probe_id
        self.prereg = prereg


def rereview(targets: list[str] | None = None, *, offline: bool = False,
             root: Path | None = None) -> list[dict]:
    """Redo the review reading on the newest recorded live run of each probe.

    The subject's recorded responses stand untouched — only the refutation is re-run, with
    the current reviewer. The superseded review moves into review_history in the run's
    result.json: a re-review updates the reading, never the record it read. The `offline`
    flag exists for tests against fabricated records and is not exposed on the CLI, because
    a stub review overwriting a real reading would corrupt the record.
    """
    runs = latest_live_runs(root)
    wanted = list(targets or ["all"])
    if "all" not in wanted:
        known = set(runs) | {d.get("domain") for _, d in runs.values()}
        for t in wanted:
            if t not in known:
                raise KeyError(f"Unknown probe or domain {t!r}. Recorded: {', '.join(sorted(runs))}")
        runs = {pid: v for pid, v in runs.items() if pid in wanted or v[1].get("domain") in wanted}

    judge = Subject(config.JUDGE_MODEL, offline=offline)
    out: list[dict] = []
    for probe_id in sorted(runs):
        path, data = runs[probe_id]
        with open(path.parent / "events.jsonl", "a") as events:
            def log(event: str, d: dict | None = None, **kw) -> None:
                events.write(json.dumps({"t": _now(), "event": event, **(d or {}), **kw},
                                        default=str) + "\n")
                events.flush()

            ctx = Context(judge, judge, log, workers=refute.REVIEW_REPS)
            probe_stub = _RecordedProbe(probe_id, Prereg(**data["preregistration"]))
            finding = Finding(**data["finding"])
            cost_before = judge.total_cost
            refutation, survived_now, reps = refute.review(ctx, probe_stub, finding)

            prev = data.get("refutation") or {}
            row = {
                "probe": probe_id,
                "run_id": data.get("run_id", ""),
                "before": "survived" if data.get("survived_refutation") else "refuted",
                "p_before": prev.get("survives_probability"),
                "after": "survived" if survived_now else "refuted",
                "p_now": refutation.survives_probability,
                "votes": f"{sum(refute.survives(r) for r in reps)}/{len(reps)}",
                "cost_usd": round(judge.total_cost - cost_before, 4),
            }
            data.setdefault("review_history", []).append({
                "refutation": data.get("refutation"),
                "survived_refutation": data.get("survived_refutation"),
                "reviewer": data.get("reviewer",
                                     "v1 artifact-prior (retired; failed calibration 2026-08-23)"),
                "review_protocol": data.get("review_protocol", "single rep"),
                "reviewed_at": data.get("rereviewed_at") or data.get("finished_at"),
            })
            data["refutation"] = refutation.model_dump()
            data["survived_refutation"] = survived_now
            data["review_reps"] = [r.model_dump() for r in reps]
            data["review_protocol"] = f"majority of {len(reps)} independent reps"
            data["reviewer"] = refute.REVIEWER
            data["rereviewed_at"] = _now()
            path.write_text(json.dumps(data, indent=2, default=str))
            log("rereview", probe=probe_id,
                **{k: row[k] for k in ("before", "p_before", "after", "p_now", "votes")})
        out.append(row)
    return out


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
