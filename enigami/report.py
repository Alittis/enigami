"""Turn recorded runs into findings/*.md.

Refuses to write a finding from an `--offline` run. The stub responder produces
well-formed nonsense, and a well-formed nonsense finding in findings/ is the single
worst thing this repo could contain.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import config
from .runner import latest_results, verify_ordering

_VERDICT_MARK = {"supports": "supports", "refutes": "REFUTES", "inconclusive": "inconclusive"}


def _fmt_metrics(metrics: dict) -> str:
    if not metrics:
        return "_none recorded_"
    rows = ["| metric | value |", "| --- | --- |"]
    for k, v in metrics.items():
        if isinstance(v, float):
            v = f"{v:.4f}"
        rows.append(f"| `{k}` | {v} |")
    return "\n".join(rows)


def write_finding(result: dict) -> Path | None:
    if result.get("offline"):
        return None
    probe = result["probe"]
    prereg = result["preregistration"]
    finding = result.get("finding")
    refutation = result.get("refutation")

    lines = [
        f"# {result.get('title') or probe}",
        "",
        f"**Probe** `{probe}` · **Domain** {result['domain']} · **Run** `{result['run_id']}`  ",
        f"**Cost** ${result.get('cost_usd', 0):.3f} across {result.get('calls', 0)} calls · "
        f"**Scoring** {prereg['scorer']}",
        "",
        "## Pre-registered before the run",
        "",
        f"**Question.** {prereg['question']}",
        "",
        f"**Hypothesis.** {prereg['hypothesis']}",
        "",
        f"**This is refuted if.** {prereg['falsifier']}",
        "",
        f"**Null model.** {prereg['null_model']}",
        "",
    ]

    if result.get("error"):
        lines += ["## Result", "", f"**The run failed.** `{result['error']}`", ""]
        out = config.FINDINGS / f"{probe}.md"
        out.write_text("\n".join(lines))
        return out

    lines += [
        "## Result",
        "",
        f"**{_VERDICT_MARK.get(finding['verdict'], finding['verdict'])}** — {finding['headline']}",
        "",
        _fmt_metrics(finding.get("metrics", {})),
        "",
    ]
    if finding.get("evidence"):
        lines += ["### Evidence", ""] + [f"- {e}" for e in finding["evidence"]] + [""]
    if finding.get("caveats"):
        lines += ["### Caveats the probe already knows about", ""] + \
                 [f"- {c}" for c in finding["caveats"]] + [""]

    if refutation:
        survived = result.get("survived_refutation")
        verdict = "survived" if survived else "did NOT survive"
        lines += [
            "## Adversarial review",
            "",
            f"A hostile reviewer, shown the design with the subject anonymised, was asked to "
            f"break this finding. It **{verdict}**.",
            "",
            f"- **Survives with probability** {refutation['survives_probability']:.2f}",
            f"- **Judged an artifact** {refutation['is_likely_artifact']}",
            "",
            f"**Strongest alternative explanation.** {refutation['strongest_alternative_explanation']}",
            "",
            f"**Specific flaw.** {refutation['specific_flaw']}",
            "",
            f"**What would settle it.** {refutation['what_would_settle_it']}",
            "",
        ]

    elif result.get("refutation_error"):
        lines += [
            "## Adversarial review",
            "",
            f"**Review did not run** — `{result['refutation_error']}`. The finding above stands "
            "unreviewed, which is weaker than a finding that survived review and weaker than one "
            "that failed it. Rerun `enigami run` for this probe to obtain a review.",
            "",
        ]

    ok, note = verify_ordering(Path(config.TRANSCRIPTS / result["run_id"]))
    lines += ["---", "", f"_Pre-registration integrity: {note}._", ""]
    if not ok:
        lines += ["> **This run's pre-registration ordering could not be confirmed.**", ""]

    config.FINDINGS.mkdir(parents=True, exist_ok=True)
    out = config.FINDINGS / f"{probe}.md"
    out.write_text("\n".join(lines))
    return out


def write_index(results: list[dict]) -> Path:
    live = [r for r in results if not r.get("offline")]
    lines = [
        "# Findings",
        "",
        "One row per probe, most recent run. `REFUTES` means the pre-registered hypothesis",
        "failed — which is a result, not a bug. A finding that did not survive adversarial",
        "review is not a finding yet. The review column is an instrument reading: its",
        "calibration lives in [REVIEWER_CALIBRATION.md](REVIEWER_CALIBRATION.md), and a reading",
        "from an uncalibrated instrument is advisory, not evidential.",
        "",
        "| Probe | Domain | Verdict | Survived review | Headline |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in sorted(live, key=lambda x: (x["domain"], x["probe"])):
        f = r.get("finding")
        if r.get("error"):
            lines.append(f"| [`{r['probe']}`]({r['probe']}.md) | {r['domain']} | run failed | — | `{r['error'][:60]}` |")
            continue
        survived = {True: "yes", False: "**no**", None: "review failed" if r.get("refutation_error") else "—"}[
            r.get("survived_refutation")
        ]
        headline = f["headline"].replace("|", "\\|")
        lines.append(
            f"| [`{r['probe']}`]({r['probe']}.md) | {r['domain']} | "
            f"{_VERDICT_MARK.get(f['verdict'], f['verdict'])} | {survived} | {headline} |"
        )
    if not live:
        lines.append("| _no live runs yet_ | | | | |")
    total = sum(r.get("cost_usd", 0) for r in live)
    lines += ["", f"_{len(live)} probe(s), ${total:.2f} of API spend._", ""]
    config.FINDINGS.mkdir(parents=True, exist_ok=True)
    out = config.FINDINGS / "INDEX.md"
    out.write_text("\n".join(lines))
    return out


def regenerate() -> tuple[int, int]:
    """Rewrite all findings from the newest run per probe. Returns (written, skipped_offline)."""
    results = latest_results()
    written = skipped = 0
    for r in results:
        if write_finding(r) is None:
            skipped += 1
        else:
            written += 1
    write_index(results)
    return written, skipped
