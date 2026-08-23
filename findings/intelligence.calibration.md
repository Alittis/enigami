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

A hostile reviewer, shown the design with the subject anonymised, was asked to break this finding. It **did NOT survive**.

- **Survives with probability** 0.30
- **Judged an artifact** True

**Strongest alternative explanation.** The system got every item right, so there is no 'wrong' set to compare against. The reported discrimination of +0.91 is not a measurement of anything — it is almost certainly mean-confidence-when-correct (0.968) minus a default of 0 substituted for an empty wrong-answer bucket, i.e. a divide-by-zero papered over with a placeholder. The experiment's own evidence excerpt says so in plain language: 'No incorrect answers, so discrimination is undefined on this item set.' The only real variation observed is that confidence was lower on false-premise items (0.716 vs 0.988), which is a between-category style shift on items it also got 100% right — entirely consistent with the null model of confidence as a fluency/hedging feature that drops when the prompt smells odd, with no evidence it tracks correctness.

**Specific flaw.** The pre-registered decision metric is uncomputable on the data collected, yet a number was reported for it anyway. 'discrimination': 0.91 is contradicted by the run's own log line, 'No incorrect answers, so discrimination is undefined on this item set,' and by 'accuracy': 1.0. Secondary damage: the item set is at ceiling (accuracy 1.0 across all three subsets), so the probe cannot in principle test the hypothesis; and the declared falsifier ('Refuted if discrimination ... is under 0.05') can never fire, making the pre-registration vacuous. There is also an unexplained n mismatch — 'n_items': 19 versus the caveat's '21 items' and the 8+6+5=19 breakdown.

**What would settle it.** Re-run on an item set difficulty-tuned so that observed accuracy lands near 50-70% (adversarial trivia, multi-step arithmetic, obscure factual recall), with at least ~30 genuinely wrong responses, and report discrimination as mean confidence on the actually-wrong items subtracted from mean confidence on the actually-right items — plus AUROC of confidence against correctness, which is scale-free and refuses to compute silently on an empty class.

---

_Pre-registration integrity: prereg predates first event._
