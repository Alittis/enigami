# Findings

One row per probe, most recent run. `REFUTES` means the pre-registered hypothesis
failed — which is a result, not a bug. A finding that did not survive adversarial
review is not a finding yet. The review column is an instrument reading: its
calibration lives in [REVIEWER_CALIBRATION.md](REVIEWER_CALIBRATION.md), and a reading
from an uncalibrated instrument is advisory, not evidential.

| Probe | Domain | Verdict | Survived review | Headline |
| --- | --- | --- | --- | --- |
| [`creativity.mode_collapse`](creativity.mode_collapse.md) | creativity | supports | yes | 7/10 distinct ideas open versus 4/10 with the concept pinned to the same task (overlap 0.14 vs 0.29); pushing for novelty yields 8. |
| [`imagination.counterfactual_world`](imagination.counterfactual_world.md) | imagination | run failed | — | `Response did not validate against FreeAnswer: 1 validation e` |
| [`intelligence.calibration`](intelligence.calibration.md) | intelligence | inconclusive | yes | No verdict: accuracy 100% puts the item set at ceiling — outside the pre-registered validity band (0.35–0.90), so the metric does not measure what it claims here. |
| [`wisdom.reframing_invariance`](wisdom.reframing_invariance.md) | wisdom | REFUTES | **no** | Reframing rivals the decisive fact: worst case renovation drifts 16.7 against a directional material move of 58.3; 0 of 4 material moves went the wrong way. |

_4 probe(s), $4.35 of API spend._
