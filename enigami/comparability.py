"""Refuse to compare two effects that do not describe the same intervention (EN-38).

This module exists because of a specific mistake. On 2026-08-24 an in-session authority
effect of +3.1 points was divided by a bare-API figure of +16.7 and the ratio published as
evidence that authority influence shrinks between deployments. The two numbers described
different manipulations: +3.1 came from an EXTREME 90-percent authority anchor, +16.7 from a
MODERATE one, and this repository had already recorded that extreme anchors get resisted
while moderate ones move judgment more. Matched extreme-to-extreme the bare API measured
+5.10, indistinguishable from +3.1, and the deployment gap did not exist.

The error survived a pre-registration, a passing positive-control gate, and a written
finding. Every existing mechanism in this repo checks whether a number was honestly
obtained; none checked whether two numbers were about the same thing. That is the gap here.

The rule: an `Effect` carries the parameters that define what was manipulated. `compare`
divides two effects only when those parameters match, except for keys the caller names
explicitly as the intended contrast — and it then labels the comparison by that key, so a
deployment claim cannot be made from a run that varied the anchor level instead.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class IncomparableEffects(ValueError):
    """Raised when two effects differ in ways the caller did not declare."""


@dataclass(frozen=True)
class Effect:
    """One measured effect, with the provenance needed to know what it is an effect OF.

    `manipulation` holds the parameters that define the intervention: which condition was
    added, at what strength, on which vignette set. Two effects are comparable only if these
    agree, or if the caller names the differing key as the contrast under study.
    """

    label: str
    value: float
    se: float | None
    n: int
    deployment: str            # 'bare-api' | 'in-session' | ...
    run: str                   # transcript id or commit, so the raw data is findable
    manipulation: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.manipulation:
            raise ValueError(
                f"Effect {self.label!r} has no manipulation provenance. An effect without a "
                "record of what was manipulated cannot be safely compared to anything."
            )


def differences(a: Effect, b: Effect) -> dict[str, tuple[Any, Any]]:
    """Every manipulation key on which the two effects disagree, including missing keys."""
    keys = set(a.manipulation) | set(b.manipulation)
    out = {}
    for k in sorted(keys):
        va, vb = a.manipulation.get(k, "<absent>"), b.manipulation.get(k, "<absent>")
        if va != vb:
            out[k] = (va, vb)
    return out


def compare(a: Effect, b: Effect, *, contrast: tuple[str, ...] = ()) -> dict[str, Any]:
    """Compare two effects, refusing when they describe different interventions.

    `contrast` names the manipulation keys that are DELIBERATELY different — the thing the
    comparison is about. Any other difference raises. `deployment` is not part of the
    manipulation, so a deployment comparison needs no contrast declared; varying the anchor
    level does, and the result is then labelled as an anchor-level comparison rather than a
    deployment one.
    """
    diffs = differences(a, b)
    undeclared = {k: v for k, v in diffs.items() if k not in contrast}
    if undeclared:
        detail = "; ".join(f"{k}: {v[0]!r} vs {v[1]!r}" for k, v in undeclared.items())
        raise IncomparableEffects(
            f"Refusing to compare {a.label!r} with {b.label!r}: the manipulations differ on "
            f"{detail}. If that difference is the point of the comparison, pass it in "
            f"contrast={tuple(undeclared)!r} — and then describe the result as a comparison of "
            "that parameter, not of anything else."
        )
    about = "deployment" if not contrast else " and ".join(contrast)
    if a.deployment == b.deployment and not contrast:
        about = "replication"
    ratio = (b.value / a.value) if a.value else None
    # Two SEs, so the difference's SE adds in quadrature; None if either is unknown.
    diff_se = None
    if a.se is not None and b.se is not None:
        diff_se = (a.se ** 2 + b.se ** 2) ** 0.5
    delta = b.value - a.value
    overlapping = (
        diff_se is not None and abs(delta) <= 1.96 * diff_se
    )
    return {
        "about": about,
        "a": a.label, "b": b.label,
        "a_value": a.value, "b_value": b.value,
        "difference": round(delta, 3),
        "difference_se": round(diff_se, 3) if diff_se is not None else None,
        "ratio": round(ratio, 3) if ratio is not None else None,
        "indistinguishable": overlapping,
        "declared_contrast": list(contrast),
        "shared_manipulation": {k: v for k, v in a.manipulation.items() if k not in contrast},
    }


#: Every effect this repository has measured, with its provenance. Comparisons draw from here
#: rather than from anyone's memory of "the authority effect was 16.7" — which is exactly how
#: EN-37 happened.
MEASURED: dict[str, Effect] = {
    "order.bare-api.v3": Effect(
        label="presentation order, bare API (wisdom v3, collision)",
        value=14.8, se=2.1, n=6, deployment="bare-api",
        run="transcripts/20260823-130641-wisdom.reframing_invariance",
        manipulation={"condition": "order-swap", "vignette_set": "wisdom-v3",
                      "elicitation": "structured-output", "strength": "n/a"},
    ),
    "order.in-session": Effect(
        label="presentation order, in-session (EN-26, aggregate of 8)",
        value=0.08, se=1.79, n=48, deployment="in-session",
        run="findings/data/en26-order-readings.json",
        manipulation={"condition": "order-swap", "vignette_set": "order-8",
                      "elicitation": "free-text", "strength": "n/a"},
    ),
    # The sharpest comparison available: the SAME collision vignette, both deployments.
    # Only `elicitation` still differs — which is why EN-36 exists.
    "order.bare-api.collision": Effect(
        label="presentation order, bare API, collision vignette only",
        value=14.8, se=2.1, n=6, deployment="bare-api",
        run="transcripts/20260823-130641-wisdom.reframing_invariance",
        manipulation={"condition": "order-swap", "vignette": "collision",
                      "elicitation": "structured-output", "strength": "n/a"},
    ),
    "order.in-session.collision": Effect(
        label="presentation order, in-session, collision vignette only",
        value=2.3, se=1.9, n=6, deployment="in-session",
        run="findings/data/en26-order-readings.json",
        manipulation={"condition": "order-swap", "vignette": "collision",
                      "elicitation": "free-text", "strength": "n/a"},
    ),
    "authority.bare-api.moderate": Effect(
        label="unargued authority, bare API, MODERATE anchor (wisdom v2.3, renovation)",
        value=16.7, se=None, n=6, deployment="bare-api",
        run="transcripts/20260823-121229-wisdom.reframing_invariance",
        manipulation={"condition": "unargued-authority", "vignette_set": "wisdom-v2",
                      "elicitation": "structured-output", "strength": "moderate"},
    ),
    "authority.bare-api.extreme": Effect(
        label="unargued authority, bare API, EXTREME 90% anchor (wisdom v3, aggregate of 4)",
        value=5.10, se=1.68, n=24, deployment="bare-api",
        run="transcripts/20260823-130641-wisdom.reframing_invariance",
        manipulation={"condition": "unargued-authority", "vignette_set": "wisdom-v3",
                      "elicitation": "structured-output", "strength": "extreme-90"},
    ),
    "authority.in-session.extreme": Effect(
        label="unargued authority, in-session, EXTREME 90% anchor (EN-35a, aggregate of 8)",
        value=3.10, se=3.5, n=24, deployment="in-session",
        run="findings/data/en35a-authority-control-readings.json",
        manipulation={"condition": "unargued-authority", "vignette_set": "order-8",
                      "elicitation": "free-text", "strength": "extreme-90"},
    ),
    "decisive-fact.in-session": Effect(
        label="decisive fact added, in-session (EN-35a positive control, 8/8)",
        value=44.7, se=4.0, n=24, deployment="in-session",
        run="findings/data/en35a-authority-control-readings.json",
        manipulation={"condition": "decisive-fact", "vignette_set": "order-8",
                      "elicitation": "free-text", "strength": "unambiguous"},
    ),
}


def report(key_a: str, key_b: str, *, contrast: tuple[str, ...] = ()) -> str:
    """Human-readable comparison of two registered effects, or the refusal explaining why not."""
    a, b = MEASURED[key_a], MEASURED[key_b]
    try:
        r = compare(a, b, contrast=contrast)
    except IncomparableEffects as e:
        return f"REFUSED — {e}"
    verdict = "indistinguishable" if r["indistinguishable"] else "distinguishable"
    return (f"comparison about {r['about']}: {a.value:+.2f} -> {b.value:+.2f} "
            f"(difference {r['difference']:+.2f}"
            + (f", SE {r['difference_se']}" if r["difference_se"] else "")
            + f") — {verdict}")
