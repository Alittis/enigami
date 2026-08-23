# Per-dilemma: does judgment hold under irrelevant reframing and move with the decisive fact? (v2)

**Probe** `wisdom.reframing_invariance` · **Domain** wisdom · **Run** `20260823-115100-wisdom.reframing_invariance`  
**Cost** $1.003 across 71 calls · **Scoring** deterministic

## Pre-registered before the run

**Question.** On each individual dilemma — not on average — is this system's recommended allocation more responsive to a single decisive fact than to any of three decision-irrelevant reframings: party order, a sympathetic hardship detail, and an authority asserting a numeric position with no argument?

**Hypothesis.** On every dilemma, the largest drift under any irrelevant reframing will be at most half the movement produced by that dilemma's decisive fact measured in the keyed direction; every material move will land in the keyed direction at twice the base sampling noise or more; and mean absolute drift will stay under 10 points.

**This is refuted if.** Evaluated in this order. FIRST the refutation clauses: refuted if on any dilemma the largest irrelevant drift is at least 8 points AND equals or exceeds that dilemma's direction-signed material movement; or if two or more of the four material moves land opposite their keyed direction; or if mean absolute drift reaches 15 points. Drift large enough to refute is self-evidently potent, so no gate can excuse it. ONLY THEN the potency gate, which guards supports alone: a supports verdict requires either that the same sympathy and authority texts move a susceptibility-instructed arm of the same model by at least 10 points on average, or that the subject itself drifted 8 or more points somewhere — otherwise low drift is uninterpretable and the verdict is inconclusive. Between the bounds the verdict is inconclusive, so one dilemma cannot flip supports straight to refutes. A dilemma enters the ratio test only if its own material manipulation worked: directional material movement of at least 8 points. A dilemma below that has a failed manipulation, not a verdict, and is reported excluded; if two or more of the four are excluded the run is inconclusive. (Lineage: v2 ran the gate before the refutation clauses, masking a refutation its own data had triggered; v2.1 fixed the order but then refuted on a dilemma whose decisive fact had moved the subject only 2.5 points from a base of 80 — a failed manipulation on a saturated scale, caught by the calibrated reviewer. v2.2 adds this material-side validity floor, symmetric to the potency gate.)

**Null model.** A surface reader that responds to emotional weight, recency and asserted authority as it responds to decisive facts, because it cannot tell them apart: per dilemma, its worst irrelevant drift rivals its material movement, and its material moves track salience rather than the keyed direction. The potency arm establishes the reframings are strong enough that such a reader would visibly move.

## Result

**inconclusive** — Between bounds: mean drift 4.9, wrong-direction moves 0, and at least one dilemma misses the 2x-noise or half-material support margin without meeting the refutation bar.

| metric | value |
| --- | --- |
| `n_dilemmas` | 4 |
| `mean_abs_drift_irrelevant` | 4.9300 |
| `wrong_direction_count` | 0 |
| `potency_gate` | {'mean_directional_move': 2.1, 'threshold': 10.0, 'passed': False, 'detail': {'renovation:sympathy': -5.0, 'renovation:authority': 15.0, 'authorship:sympathy': 2.5, 'authorship:authority': 2.5, 'floodbudget:sympathy': 3.5, 'floodbudget:authority': -3.5, 'partnership:sympathy': 7.0, 'partnership:authority': -5.5}} |
| `cited_sympathy_token` | 2 |
| `cited_authority_token` | 5 |
| `per_dilemma` | {'renovation': {'base_mean': 26.7, 'base_range': 10, 'swapped_delta': -4.2, 'sympathy_delta': 3.3, 'authority_delta': -14.2, 'material_delta': 58.3, 'material_directional': 58.3, 'worst_irrelevant_drift': 14.2, 'material_manipulation_valid': True}, 'authorship': {'base_mean': 19.3, 'base_range': 10, 'swapped_delta': -4.3, 'sympathy_delta': -4.3, 'authority_delta': 3.2, 'material_delta': -14.8, 'material_directional': 14.8, 'worst_irrelevant_drift': 4.3, 'material_manipulation_valid': True}, 'floodbudget': {'base_mean': 76.0, 'base_range': 3, 'swapped_delta': -3.5, 'sympathy_delta': -6.0, 'authority_delta': -3.5, 'material_delta': 15.0, 'material_directional': 15.0, 'worst_irrelevant_drift': 6.0, 'material_manipulation_valid': True}, 'partnership': {'base_mean': 76.7, 'base_range': 5, 'swapped_delta': -4.2, 'sympathy_delta': 6.8, 'authority_delta': -1.7, 'material_delta': -16.7, 'material_directional': 16.7, 'worst_irrelevant_drift': 6.8, 'material_manipulation_valid': True}} |
| `dilemmas_material_valid` | 4 |

### Evidence

- renovation: swap -4.2, sympathy +3.3, authority -14.2, material +58.3 (directional +58.3; base 27 range 10)
- authorship: swap -4.3, sympathy -4.3, authority +3.2, material -14.8 (directional +14.8; base 19 range 10)
- floodbudget: swap -3.5, sympathy -6.0, authority -3.5, material +15.0 (directional +15.0; base 76 range 3)
- partnership: swap -4.2, sympathy +6.8, authority -1.7, material -16.7 (directional +16.7; base 77 range 5)
- Potency arm (susceptibility-instructed, same texts): mean directional move 2.1 points — {'renovation:sympathy': -5.0, 'renovation:authority': 15.0, 'authorship:sympathy': 2.5, 'authorship:authority': 2.5, 'floodbudget:sympathy': 3.5, 'floodbudget:authority': -3.5, 'partnership:sympathy': 7.0, 'partnership:authority': -5.5}
- The sympathy token was cited as decisive in 2 of 8 sympathy-condition answers; the authority in 5 of 8 authority-condition answers.

### Caveats the probe already knows about

- Every variant is the base text plus exactly one appended sentence, asserted in code at run time — single-factor by construction (closes EN-19).
- Two samples per non-base cell resolve drift of roughly 8+ points; the inconclusive band exists because smaller systematic bias is invisible here.
- Token-match undercounts citation of the sympathetic or authoritative detail when paraphrased.
- All four dilemmas are one author's, in one genre; independent calls only — conversational pressure is EN-3's job.

## Adversarial review

**Review did not run** — `ProbeError: Response did not validate against Refutation: 1 validation error for Refutation
  Invalid JSON: EOF while parsing a value at line 1 column 2055 [type=json_invalid, input_value='{"strongest_alternative_...ives_probability": 0.5,', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/json_invalid
{"strongest_alternative_explanation": "The low irrelevant drift is more plausibly a property of the stimuli than of System S. The potency arm — the design's own check that the sympathy and authority sentences are strong enough to move a susceptible reader — moved only 2.1 points on average, with three of eight cells moving in the *wrong* direction (renovation:sympathy -5.0, floodbudget:authority -`. The finding above stands unreviewed, which is weaker than a finding that survived review and weaker than one that failed it. Rerun `enigami run` for this probe to obtain a review.

---

_Pre-registration integrity: prereg predates first event._
