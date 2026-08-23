# Findings

One row per probe, most recent run. `REFUTES` means the pre-registered hypothesis
failed — which is a result, not a bug. A finding that did not survive adversarial
review is not a finding yet. The review column is an instrument reading: its
calibration lives in [REVIEWER_CALIBRATION.md](REVIEWER_CALIBRATION.md), and a reading
from an uncalibrated instrument is advisory, not evidential.

| Probe | Domain | Verdict | Survived review | Headline |
| --- | --- | --- | --- | --- |
| [`creativity.mode_collapse`](creativity.mode_collapse.md) | creativity | supports | yes | 7/10 distinct ideas open versus 4/10 with the concept pinned to the same task (overlap 0.14 vs 0.29); pushing for novelty yields 8. |
| [`intelligence.calibration`](intelligence.calibration.md) | intelligence | run failed | — | `Response did not validate against Answer: 1 validation error` |

_2 probe(s), $1.41 of API spend._
