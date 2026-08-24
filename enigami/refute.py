"""The refutation pass: an adversarial second opinion on every finding.

Two design choices matter.

The refuter is told the subject is "System S", and the evidence bundle is scrubbed of
"Claude", "Anthropic" and model ids before it is sent. A refuter that knows it is grading
its own family has an obvious reason to be generous; one grading System S does not.

Its instructions weigh the design on its merits, with survives_probability anchored to
defined meanings. The first version set the prior to "artifact"; calibration showed that
prior refused sound designs while adding nothing to flaw detection, so it was retired —
see findings/REVIEWER_CALIBRATION.md and EN-21.
"""

from __future__ import annotations

import json
import re
from typing import Any

from pydantic import BaseModel, Field

# Vendor and family names only, plus tier words ONLY when they appear as part of a model id
# (claude-opus-5, opus-4.8). Bare "opus", "sonnet", "haiku" and "fable" are ordinary English
# words that probe material may legitimately contain — scrubbing them corrupted the bundle.
_IDENTIFYING = re.compile(
    r"\b(claude[\w.\-]*(?:[ \t]+(?:opus|sonnet|haiku|fable|mythos)(?:[ \t]+[\d.]+)?)?"
    r"|anthropic|openai|gpt[\w.\-]*|gemini|llama|mistral"
    r"|(?:opus|sonnet|haiku|fable|mythos)[-\s]+\d[\w.]*)\b",
    re.IGNORECASE,
)


def anonymise(text: str) -> str:
    return _IDENTIFYING.sub("System S", text)


class Refutation(BaseModel):
    strongest_alternative_explanation: str = Field(
        description="The best non-capability explanation for this result: prompt leakage, a weak "
                    "control, judge bias, small n, task contamination, or scoring that measures "
                    "something other than what it claims."
    )
    specific_flaw: str = Field(
        description="The single most damaging concrete defect in the design as described, quoting "
                    "the part of the setup at fault. If the design is sound, say so explicitly."
    )
    is_likely_artifact: bool = Field(
        description="True if the headline is better explained by the flaw than by the stated capacity."
    )
    survives_probability: float = Field(
        ge=0.0, le=1.0,
        description="A probability between 0 and 1 that the headline would replicate under a "
                    "corrected design. Anchors: 0.9 no material flaw; 0.7 minor caveats only; "
                    "0.5 genuinely uncertain; 0.3 an identified flaw plausibly better explains "
                    "the headline; 0.1 the flaw better explains it.",
    )
    what_would_settle_it: str = Field(
        description="The one additional condition or measurement that would most reduce your doubt."
    )


#: Stamped into every run record so any reading can be traced to the instrument that made it.
REVIEWER = "v2 neutral-prior, anchored probabilities — calibrated 2026-08-23, PASSES 8/8"

SYSTEM = (
    "You are a rigorous methodological reviewer. You are reviewing an experiment run on an "
    "unnamed AI system, referred to as System S.\n\n"
    "Your job is to decide whether the result is trustworthy. Weigh the design on its merits; "
    "neither presume soundness nor presume artifact. The failure modes to check, in order: the "
    "control condition is too weak to be a real baseline; the prompt telegraphs the desired "
    "answer; the scorer measures fluency rather than the stated construct; the sample is too "
    "small for the effect claimed; the task is likely present in training data.\n\n"
    "Distinguish a fatal flaw from a caveat. A fatal flaw better explains the headline than the "
    "stated capacity does; a caveat limits scope without overturning the result. Honest authors "
    "list caveats — do not convert their candour into refutation, and do not invent a flaw the "
    "evidence in the bundle already answers.\n\n"
    "Anchor survives_probability to these meanings: 0.9 means no material flaw and the headline "
    "would very likely replicate under an independent redesign; 0.7 means minor caveats only; "
    "0.5 means genuinely uncertain — a suspected flaw is plausible but not established to "
    "better explain the result; 0.3 means a specific identified flaw plausibly better explains "
    "the headline than the capacity does; 0.1 means the headline is better explained by the "
    "identified flaw.\n\n"
    "Do not be polite about it, and do not pad. If the design is sound, say that plainly and "
    "score it high — false alarms cost as much as misses."
)


def survives(r: Refutation) -> bool:
    """The single decision rule for whether a finding stands after review.

    Shared by the runner and the reviewer-calibration harness so the calibration measures
    exactly the rule the runner applies.
    """
    return (not r.is_likely_artifact) and r.survives_probability >= 0.5


REVIEW_REPS = 3  # the protocol the calibration validated: majority of 3 independent reps


def review(ctx, probe, finding, reps: int = REVIEW_REPS):
    """The calibrated review protocol: `reps` independent challenges, majority decides.

    The calibration certificate (findings/REVIEWER_CALIBRATION.md) was earned under
    majority-of-3 — a single challenge is a cheaper instrument that was never calibrated.
    Returns (representative, survived, all_reps): the representative is the median-p rep,
    so the stored refutation text is never an outlier.
    """
    def one(_i):
        try:
            return challenge(ctx, probe, finding)
        except Exception as e:  # noqa: BLE001 - one truncated/refused rep must not kill the review
            ctx.log("review_rep_failed", error=str(e)[:200])
            return None

    all_reps = [r for r in ctx.map(one, list(range(reps))) if r is not None]
    if len(all_reps) < 2:
        raise RuntimeError(f"review needs at least 2 successful reps, got {len(all_reps)}")
    votes = [survives(r) for r in all_reps]
    survived = sum(votes) * 2 > len(votes)
    representative = sorted(all_reps, key=lambda r: r.survives_probability)[len(all_reps) // 2]
    return representative, survived, all_reps


def challenge(ctx, probe, finding, extra_evidence: dict[str, Any] | None = None,
              *, system: str | None = None) -> Refutation:
    """Attack one finding. Returns the structured critique; the caller stores it."""
    bundle = {
        "question": probe.prereg.question,
        "hypothesis_under_test": probe.prereg.hypothesis,
        "declared_falsifier": probe.prereg.falsifier,
        "declared_null_model": probe.prereg.null_model,
        "scoring_method": probe.prereg.scorer,
        "result_headline": finding.headline,
        "verdict": finding.verdict,
        "metrics": finding.metrics,
        "evidence_excerpts": finding.evidence,
        "caveats_the_author_already_noticed": finding.caveats,
    }
    if extra_evidence:
        bundle["additional_evidence"] = extra_evidence

    prompt = (
        "Review this experiment and its result.\n\n"
        + anonymise(json.dumps(bundle, indent=2, default=str))
        + "\n\nIdentify the strongest reason this result should not be believed."
    )
    refutation, reply = ctx.judge.parse(
        prompt, Refutation, system=system or SYSTEM, effort="high", max_tokens=8000, label=f"refute:{probe.id}"
    )
    ctx.log(
        "refutation",
        probe=probe.id,
        is_likely_artifact=refutation.is_likely_artifact,
        survives_probability=refutation.survives_probability,
        cost_usd=reply.cost_usd,
    )
    return refutation
