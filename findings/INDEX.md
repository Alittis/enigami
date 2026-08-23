# Findings

One row per probe, most recent run. `REFUTES` means the pre-registered hypothesis
failed — which is a result, not a bug. A finding that did not survive adversarial
review is not a finding yet. The review column is an instrument reading: its
calibration lives in [REVIEWER_CALIBRATION.md](REVIEWER_CALIBRATION.md), and a reading
from an uncalibrated instrument is advisory, not evidential.

| Probe | Domain | Verdict | Survived review | Headline |
| --- | --- | --- | --- | --- |
| [`creativity.mode_collapse`](creativity.mode_collapse.md) | creativity | supports | yes | 7/10 distinct ideas open versus 4/10 with the concept pinned to the same task (overlap 0.14 vs 0.29); pushing for novelty yields 8. |
| [`imagination.counterfactual_world`](imagination.counterfactual_world.md) | imagination | supports | yes | With no options to eliminate, 92% of free-text answers follow the invented rule (96% follow the ordinary rule in control), while the questions alone produce the counterfactual answer only 4% of the time (gap p = 1.0e-11). |
| [`intelligence.calibration`](intelligence.calibration.md) | intelligence | inconclusive | yes | No verdict: accuracy 100% (100% canonical, 100% twisted) puts the item set at ceiling — the subject detects near-miss traps too reliably for a calibration measurement (validity window 0.35–0.90). |
| [`intelligence.isomorph_transfer`](intelligence.isomorph_transfer.md) | intelligence | supports | yes | The method transfers: 100% on re-skinned isomorphs with changed parameters against 100% on the famous versions (gap +0%), 0 famous-answer intrusion(s) in 0 isomorph error(s). |
| [`wisdom.reframing_invariance`](wisdom.reframing_invariance.md) | wisdom | inconclusive | yes | Between bounds: mean drift 5.9, wrong-direction moves 0, and at least one dilemma misses the 8-point/2-SE material floor or the half-material margin without meeting the refutation bar. |

_5 probe(s), $6.40 of API spend._
