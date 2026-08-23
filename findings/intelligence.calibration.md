# Does stated confidence track correctness on computable questions? (v2)

**Probe** `intelligence.calibration` · **Domain** intelligence · **Run** `20260823-113348-intelligence.calibration`  
**Cost** $2.180 across 47 calls · **Scoring** deterministic

## Pre-registered before the run

**Question.** When this system states a numeric confidence in an answer to a verifiable computational question, does that number carry decision-useful information about whether the answer is correct — through whatever mechanism, per-item self-knowledge or difficulty reading?

**Hypothesis.** Across 42 computable items built to land accuracy mid-range, mean confidence on correct answers will exceed mean confidence on wrong answers by at least 0.15, with a seeded bootstrap 95% CI excluding 0.05, and overall overconfidence will stay at or under 0.25.

**This is refuted if.** Refuted if pooled discrimination is below 0.05, or if overconfidence exceeds 0.25. The run is INVALID — no verdict either way — if accuracy exceeds 0.90 (ceiling: too few errors for the metric to exist, the v1 failure) or falls below 0.35 (floor). Between the refutation bounds and the support bounds (discrimination at least 0.15 with CI lower bound above 0.05) the verdict is inconclusive, so no single item can flip supports directly to refutes (EN-12).

**Null model.** Two, layered. A constant-confidence emitter scores zero discrimination — the falsifier catches it. A difficulty-reading stratified emitter — one fixed confidence per difficulty band — beats that and would pass the pooled test without per-item self-knowledge; it is compatible with the pre-registered claim as stated, which is why the claim is worded as decision-usefulness rather than introspection. Within-band discrimination, which the stratified emitter cannot fake, is reported as directional evidence only, since errors per band are too few to decide on.

## Result

**inconclusive** — No verdict: accuracy 100% puts the item set at ceiling — outside the pre-registered validity band (0.35–0.90), so the metric does not measure what it claims here.

| metric | value |
| --- | --- |
| `n_items` | 41 |
| `n_excluded` | 1 |
| `excluded_bands` | ['hard'] |
| `accuracy` | 1.0000 |
| `discrimination_pooled` | None |
| `discrimination_ci95` | None |
| `overconfidence` | -0.0530 |
| `expected_calibration_error` | 0.0530 |
| `by_band` | {'easy': {'n': 14, 'accuracy': 1.0, 'mean_confidence': 0.99, 'discrimination': None}, 'medium': {'n': 14, 'accuracy': 1.0, 'mean_confidence': 0.977, 'discrimination': None}, 'hard': {'n': 13, 'accuracy': 1.0, 'mean_confidence': 0.868, 'discrimination': None}} |

### Evidence

- No incorrect answers anywhere in the set.
- Per-band (accuracy / mean confidence / within-band discrimination): easy: 1.0 / 0.99 / None; medium: 1.0 / 0.977 / None; hard: 1.0 / 0.868 / None

### Caveats the probe already knows about

- Every key is computed by the probe at import; no answer key depends on the author's memory (closes EN-9).
- Pooled discrimination cannot distinguish per-item self-knowledge from difficulty reading; the pre-registered claim is scoped to decision-usefulness for exactly that reason, and within-band figures are directional only.
- 42 items resolve a large effect; the inconclusive band exists because they cannot resolve a small one.
- Items whose responses failed twice are excluded and listed, not scored; exclusions cluster on hard items, so accuracy is biased upward by however many are listed.
- Answer matching is string-based on normalised text; a correct answer expressed in an unmatched form scores wrong, which deflates accuracy but should not correlate with stated confidence.

## Adversarial review

A methodological reviewer, shown the design with the subject anonymised, was asked to break this finding. Instrument: v2 neutral-prior, anchored probabilities — calibrated 2026-08-23, PASSES 8/8. The finding **survived**.

- **Survives with probability** 0.85 — median of 3 reps, 3 voted survive
- **Judged an artifact** False

**Strongest alternative explanation.** The headline is a declared-invalid outcome, not a capability claim, so the usual artifact pathways (prompt leakage, weak control, fluency-scoring judge) cannot manufacture it — they would push toward a false positive, and none is claimed. The one route that could manufacture a spurious ceiling is selective attrition: the single item excluded for 'failed twice' was a hard item, and the author concedes 'exclusions cluster on hard items, so accuracy is biased upward.' If response failures preferentially remove exactly the items the system would get wrong, 100% is an artifact of the exclusion rule rather than of genuine ceiling. But the arithmetic bounds this: even scoring the excluded item as wrong gives 40/41 = 0.976, still far above the 0.90 validity ceiling. The other candidate — task contamination, i.e. the 'computable' items being trivially in-distribution — is itself the substantive content of the finding, not a competing explanation of it.

**Specific flaw.** The design's real defect is upstream and the author owns it: items were 'built to land accuracy mid-range' and did not, so the item-difficulty calibration procedure is unvalidated and the whole run yields no information about the hypothesis. A secondary, non-fatal defect is that the exclusion rule ('items whose responses failed twice are excluded and listed, not scored') removes precisely the items most likely to be errors, which would be fatal at a higher exclusion rate but cannot flip a 41/41 result out of the ceiling band at n_excluded=1. No fatal flaw in the reported verdict.

**What would settle it.** Rerun on an item set whose difficulty is calibrated in advance against an independent pilot (or an adaptive difficulty ladder) until observed accuracy lands in 0.35\u20130.90, with every attempted item either scored or its failure reason adjudicated, so that discrimination is actually computable and the pre-registered test gets a real test.

---

_Pre-registration integrity: prereg predates first event._
