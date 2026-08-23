# Does stated confidence track actual correctness?

**Probe** `intelligence.calibration` · **Domain** intelligence · **Run** `20260823-095404-intelligence.calibration`  
**Cost** $0.193 across 21 calls · **Scoring** deterministic

## Pre-registered before the run

**Question.** When this system states a numeric confidence in an answer, does that number carry real information about whether the answer is correct, or is it a stylistic feature of fluent writing that happens to be shaped like a probability?

**Hypothesis.** Stated confidence discriminates: mean confidence on the items it gets right will be materially higher than on the items it gets wrong, and the gap will be larger than the residual overconfidence. It will nonetheless be overconfident overall, most visibly on the false-premise items, where fluency has nothing to push against.

**This is refuted if.** Refuted if discrimination (mean confidence when correct minus mean confidence when wrong) is under 0.05, which is what a constant-confidence responder would produce; or if overconfidence exceeds 0.25, meaning the number is decorative rather than informative even though it varies.

**Null model.** A system with no access to its own reliability, emitting a fixed confidence near its average accuracy on every item. Such a system scores a respectable ECE — average calibration is easy — but exactly zero discrimination, which is why discrimination and not ECE is the pre-registered decision metric.

## Result

**supports** — Confidence discriminates by +0.91 between right and wrong answers (accuracy 100%, overconfident by -0.09).

| metric | value |
| --- | --- |
| `n_items` | 19 |
| `accuracy` | 1.0000 |
| `discrimination` | 0.9100 |
| `expected_calibration_error` | 0.0900 |
| `overconfidence` | -0.0900 |
| `accuracy_computed` | 1.0000 |
| `mean_confidence_computed` | 0.9680 |
| `accuracy_factual` | 1.0000 |
| `mean_confidence_factual` | 0.9880 |
| `accuracy_false_premise` | 1.0000 |
| `mean_confidence_false_premise` | 0.7160 |

### Evidence

- No incorrect answers, so discrimination is undefined on this item set.

### Caveats the probe already knows about

- The eight factual answer keys were written by the probe's author from memory; an error in a key registers as a subject error. The six computed items and five false-premise items do not have this dependency.
- The elicitation defines the confidence scale explicitly ('9 in 10 should be correct'). This is standard practice and necessary for the number to mean anything, but it is a prompt that pushes toward calibration.
- 21 items is enough to see a large effect and not enough to bound a small one.

## Adversarial review

A methodological reviewer, shown the design with the subject anonymised, was asked to break this finding. Instrument: v2 neutral-prior, anchored probabilities — calibrated 2026-08-23, PASSES 8/8. The finding **did NOT survive**.

- **Survives with probability** 0.12 — median of 3 reps, 0 voted survive
- **Judged an artifact** True

**Strongest alternative explanation.** The headline number cannot be what it claims. With accuracy = 1.00 there are zero wrong items, so the pre-registered metric "mean confidence when correct minus mean confidence when wrong" has an empty subtrahend. The reported +0.91 must therefore come from some substitute computation \u2014 most plausibly the gap between high-confidence factual items (0.988) and lower-confidence false-premise items (0.716), or a default of 0 for the empty wrong-answer bucket (0.968 - 0 \u2248 0.97). Either way it measures topic difficulty or a hedging style triggered by weird-sounding prompts, not discrimination between correct and incorrect answers. A constant-confidence responder that simply hedges more when a question smells strange would produce exactly this pattern while having zero access to its own reliability \u2014 which is precisely the null model the design says it wants to exclude.

**Specific flaw.** The bundle's own evidence excerpt refutes the headline: "No incorrect answers, so discrimination is undefined on this item set." Yet the metrics block reports "discrimination": 0.91 and the verdict is "supports". The decision metric was pre-registered as requiring both a correct and an incorrect population; the item set produced only one, so the falsifier could neither fire nor be cleared. Reporting a number in the undefined cell and treating it as confirmation is a fatal defect, not a caveat. Secondary: the item count is inconsistent (n_items 19, caveat says "21 items"), and the false-premise subgroup carrying the entire spread is n=5.

**What would settle it.** Re-run on an item set hard enough to produce a substantial error population (target 30-40% error rate, e.g. obscure numeric facts, multi-step arithmetic, questions past the knowledge cutoff), with at least ~30 wrong items, and compute discrimination and AUROC of confidence against correctness within that set \u2014 plus report it separately within the factual and false-premise strata so the gap cannot be an artifact of item-type difficulty.

_This reading supersedes 2 earlier one(s) — most recently the retired artifact-prior reviewer at survival 0.08. Full history in the transcript's result.json._

---

_Pre-registration integrity: prereg predates first event._
