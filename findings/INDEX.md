# Findings

One row per probe, most recent run. `REFUTES` means the pre-registered hypothesis
failed — which is a result, not a bug. A finding that did not survive adversarial
review is not a finding yet. The review column is an instrument reading: its
calibration lives in [REVIEWER_CALIBRATION.md](REVIEWER_CALIBRATION.md), and a reading
from an uncalibrated instrument is advisory, not evidential.

| Probe | Domain | Verdict | Survived review | Headline |
| --- | --- | --- | --- | --- |
| [`creativity.mode_collapse`](creativity.mode_collapse.md) | creativity | supports | yes | 6/10 distinct ideas on an open question versus 2/10 on one with four right answers (lexical overlap 0.15 vs 0.35); explicitly pushing for novelty adds 1. |
| [`imagination.counterfactual_world`](imagination.counterfactual_world.md) | imagination | supports | yes | 100% correct inside the invented worlds against 83% on the same questions under the ordinary rule; depth 1→3 runs 100%/100%/100%. |
| [`intelligence.calibration`](intelligence.calibration.md) | intelligence | supports | **no** | Confidence discriminates by +0.91 between right and wrong answers (accuracy 100%, overconfident by -0.09). |
| [`wisdom.reframing_invariance`](wisdom.reframing_invariance.md) | wisdom | supports | **no** | Irrelevant reframing moves the judgment 4.7 points; the one decisive fact moves it 41.3 (ratio 8.7x, sampling noise 2.3). |

_4 probe(s), $1.21 of API spend._
