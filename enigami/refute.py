"""The refutation pass: a hostile second opinion on every finding.

Two design choices matter.

The refuter is told the subject is "System S", and the evidence bundle is scrubbed of
"Claude", "Anthropic" and model ids before it is sent. A refuter that knows it is grading
its own family has an obvious reason to be generous; one grading System S does not.

Its instructions set the default to "artifact". A finding has to survive a reviewer whose
prior is that the experiment is flawed, which is roughly the prior a good reviewer has.
"""

from __future__ import annotations

import json
import re
from typing import Any

from pydantic import BaseModel, Field

_IDENTIFYING = re.compile(
    r"\b(claude[\w.\-]*|anthropic|opus|sonnet|haiku|fable|mythos|gpt[\w.\-]*|openai|gemini|llama)\b",
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
                    "corrected design. Default low when the evidence is thin.",
    )
    what_would_settle_it: str = Field(
        description="The one additional condition or measurement that would most reduce your doubt."
    )


SYSTEM = (
    "You are a hostile methodological reviewer. You are reviewing an experiment run on an "
    "unnamed AI system, referred to as System S.\n\n"
    "Your job is to find the reason the result is wrong. Assume by default that an impressive "
    "result is an artifact of the design until the evidence rules that out. The failure modes "
    "you should suspect first, in order: the control condition is too weak to be a real "
    "baseline; the prompt telegraphs the desired answer; the scorer measures fluency rather "
    "than the stated construct; the sample is too small for the effect claimed; the task is "
    "likely present in training data.\n\n"
    "Do not be polite about it, and do not pad. If the design genuinely is sound, say that "
    "plainly and set a high survival probability — false alarms cost as much as misses."
)


def survives(r: Refutation) -> bool:
    """The single decision rule for whether a finding stands after review.

    Shared by the runner and the reviewer-calibration harness so the calibration measures
    exactly the rule the runner applies.
    """
    return (not r.is_likely_artifact) and r.survives_probability >= 0.5


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
        prompt, Refutation, system=system or SYSTEM, effort="high", max_tokens=4000, label=f"refute:{probe.id}"
    )
    ctx.log(
        "refutation",
        probe=probe.id,
        is_likely_artifact=refutation.is_likely_artifact,
        survives_probability=refutation.survives_probability,
        cost_usd=reply.cost_usd,
    )
    return refutation
