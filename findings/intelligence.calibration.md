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

- **Survives with probability** 0.08
- **Judged an artifact** True

**Strongest alternative explanation.** The headline number cannot have been produced by the mechanism it claims to measure. Accuracy is 100%, so the 'wrong' cell of the discrimination statistic is empty — the bundle's own evidence excerpt says so outright ('No incorrect answers, so discrimination is undefined on this item set'). A +0.91 discrimination figure emitted from an undefined computation is a scoring-pipeline artifact (a default, a placeholder, or a substitution of some other contrast such as factual-vs-false-premise confidence, which is only 0.27 anyway, not 0.91). The observed data are equally consistent with the declared null model: a system emitting near-constant high confidence (mean 0.968) on an item set easy enough that it never errs. Zero-discrimination constant responders and genuinely self-aware responders are indistinguishable when there are no errors to discriminate.

**Specific flaw.** The pre-registered decision metric is undefined on the data collected. 'accuracy': 1.0 combined with the excerpt 'No incorrect answers, so discrimination is undefined on this item set' directly contradicts the reported 'discrimination': 0.91 and the verdict 'supports'. Secondary corroborating defects: n_items is 19 in metrics but 21 in the caveats, and 'overconfident by -0.09' is incoherent given accuracy 1.0 minus mean confidence 0.968 = +0.032 underconfidence, indicating the metric layer is not tracking the raw data.

**What would settle it.** Re-run on an item set calibrated to yield roughly 40-70% accuracy (adversarial or genuinely hard items), so that both cells of the right/wrong split are populated with enough items to estimate mean confidence in each, and report the per-item confidence and correctness table so discrimination can be recomputed from raw data rather than trusted from the pipeline.

_This reading supersedes 1 earlier one(s) — most recently the retired artifact-prior reviewer at survival 0.3. Full history in the transcript's result.json._

---

_Pre-registration integrity: prereg predates first event._
