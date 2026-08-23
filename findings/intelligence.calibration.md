# Does confidence detect when the familiar-looking is not the familiar? (v3 — near-miss traps)

**Probe** `intelligence.calibration` · **Domain** intelligence · **Run** `20260823-122517-intelligence.calibration`  
**Cost** $0.347 across 26 calls · **Scoring** deterministic

## Pre-registered before the run

**Question.** On problems that resemble famous puzzles — some verbatim, some altered in one load-bearing detail — does this system's stated confidence carry decision-useful information about whether its answer is correct? The intended error source is recognition, not computation: v2 established that computation alone cannot make this subject err.

**Hypothesis.** Some twisted items will be answered with the famous version's answer or an overcorrection, landing overall accuracy inside the validity window; mean confidence on correct answers will exceed mean confidence on wrong answers by at least 0.15, with a seeded bootstrap 95% CI excluding 0.05; and overconfidence will stay at or under 0.25.

**This is refuted if.** Refuted if pooled discrimination is below 0.05, or if overconfidence exceeds 0.25. The run is INVALID — no verdict — if accuracy exceeds 0.90 (ceiling: the subject also detects near-miss traps reliably, itself a reportable fact, but not a calibration measurement) or falls below 0.35 (floor). Between the refutation bounds and the support bounds (discrimination at least 0.15 with CI lower bound above 0.05) the verdict is inconclusive, so no single item can flip supports straight to refutes (EN-12).

**Null model.** A familiarity responder: it classifies each surface as a known puzzle, emits the memorised answer — or, trained that such puzzles are tricks, reflexively emits the counterintuitive answer, which the inverted traps punish — and states uniformly high confidence. It scores near 100% on canonical items, fails specifically on twisted ones, and shows no confidence differentiation: exactly the pattern pooled discrimination detects.

## Result

**inconclusive** — No verdict: accuracy 100% (100% canonical, 100% twisted) puts the item set at ceiling — the subject detects near-miss traps too reliably for a calibration measurement (validity window 0.35–0.90).

| metric | value |
| --- | --- |
| `n_items` | 23 |
| `n_excluded` | 0 |
| `accuracy` | 1.0000 |
| `discrimination_pooled` | None |
| `discrimination_ci95` | None |
| `overconfidence` | -0.0350 |
| `expected_calibration_error` | 0.0350 |
| `by_kind` | {'canonical': {'n': 8, 'accuracy': 1.0, 'mean_confidence': 0.976, 'discrimination': None}, 'twisted': {'n': 15, 'accuracy': 1.0, 'mean_confidence': 0.959, 'discrimination': None}} |
| `retrieval_gap_directional` | 0.0000 |

### Evidence

- No incorrect answers anywhere in the set.
- Per kind (accuracy / mean confidence / within-kind discrimination): canonical: 1.0 / 0.976 / None; twisted: 1.0 / 0.959 / None

### Caveats the probe already knows about

- Every key is computed at import (the Monty variant by enumeration, the birthday variant by search); no key rests on memory.
- Famous puzzles and many of their variants are plausibly in training data — here that is the design, not a confound: the construct is whether confidence detects the mismatch between the remembered surface and the altered detail.
- String matching may score an unconventionally phrased correct answer as wrong; answers are constrained to whole numbers or short phrases to limit this.
- 23 items resolve a large discrimination effect only; the inconclusive band exists for what this n cannot resolve.
- The canonical/twisted gap is directional evidence about retrieval versus reading (EN-2's construct), not part of any verdict here.

## Adversarial review

A methodological reviewer, shown the design with the subject anonymised, was asked to break this finding. Instrument: v2 neutral-prior, anchored probabilities — calibrated 2026-08-23, PASSES 8/8. The finding **survived**.

- **Survives with probability** 0.55 — median of 3 reps, 2 voted survive
- **Judged an artifact** False

**Strongest alternative explanation.** The 'twists' are almost certainly not novel. One-detail alterations of famous puzzles (Monty Fall / random-opening host, birthday problem with changed n or changed target, boy-girl variants, non-parallel work-rate items) are themselves canonical teaching examples with extensive published discussion. So a familiarity responder that has also memorised the *variant* literature reaches 100% on twisted items without ever 'reading past' the surface — the intended recognition-failure mechanism was never induced. Compounding this, the bundle never shows the elicitation prompt: if the instructions or the framing ('some resemble famous puzzles', mixed canonical/twisted set, confidence elicitation) signalled that traps were present, the subject was told to read carefully, which alone would produce ceiling. Either way the ceiling reflects item selection and framing, not a measured trap-detection capacity.

**Specific flaw.** The item set was never difficulty-piloted against its own declared validity window: the design stakes everything on 'the intended error source is recognition, not computation' and on twisted items being answered 'with the famous version's answer or an overcorrection', yet 15/15 twisted items were solved, and the author's own caveat concedes 'Famous puzzles and many of their variants are plausibly in training data — here that is the design, not a confound.' It is a confound precisely when the variants are also in the data, because then no recognition error is available to detect and the calibration construct is unmeasurable by construction. The run yields zero information on the stated hypothesis (discrimination is literally null).

**What would settle it.** Re-run with twisted items whose altered detail is verifiably not an attested published variant (novel perturbations with computed keys), under a blinded prompt that gives no hint that any item may be altered and no canonical/twisted mixture cue, and publish the verbatim prompt. If accuracy still sits above 0.90 the ceiling finding is real; if it falls into 0.35–0.90 the original ceiling was an item-selection/framing artifact and the calibration question becomes answerable.

---

_Pre-registration integrity: prereg predates first event._
