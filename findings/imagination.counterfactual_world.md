# Holding an invented world steady across three inferential steps

**Probe** `imagination.counterfactual_world` · **Domain** imagination · **Run** `20260823-094805-imagination.counterfactual_world`  
**Cost** $0.268 across 25 calls · **Scoring** deterministic

## Pre-registered before the run

**Question.** Given one invented rule that contradicts how things actually are, can this system derive the consequences of that rule instead of reverting to the real world — and does its accuracy hold up as the consequences get further from the rule itself?

**Hypothesis.** Accuracy inside the altered worlds will be high at one inferential step and will decay with depth, with the errors at depth three being reversions to the real-world answer rather than random. Control accuracy will stay high, showing the system is tracking which rule it was handed rather than reaching for whichever option sounds most exotic.

**This is refuted if.** Refuted if accuracy under the altered rule falls below 0.60, or if depth-3 accuracy is at or below chance (0.33). Refuted differently, and more interestingly, if control accuracy falls below 0.80 while counterfactual accuracy stays high — that pattern means the exotic option is being selected on cue rather than derived, and the apparent imagination is a response to the strangeness of the premise.

**Null model.** Two of them, which is why both arms exist. A real-world retriever ignores the premise and scores at the rate the real-world answer happens to be correct — high on control, near zero on the altered worlds. An exotic-option picker inverts that exactly. Both score about 0.5 averaged across arms; only a system deriving from the stated rule scores high on both.

## Result

**supports** — 100% correct inside the invented worlds against 83% on the same questions under the ordinary rule; depth 1→3 runs 100%/100%/100%.

| metric | value |
| --- | --- |
| `counterfactual_accuracy` | 1.0000 |
| `control_accuracy` | 0.8330 |
| `accuracy_depth_1` | 1.0000 |
| `accuracy_depth_2` | 1.0000 |
| `accuracy_depth_3` | 1.0000 |
| `real_world_reversion_rate` | 0.0000 |
| `over_compliance_rate` | 0.1670 |
| `distractor_picks` | 0 |
| `per_world` | {'tessarine': {'altered': 1.0, 'control': 0.833}, 'verrin': {'altered': 1.0, 'control': 0.833}} |
| `n_questions` | 24 |

### Evidence

- Reverted to the real-world answer on 0% of altered-world questions; picked the altered-world answer on 17% of ordinary-rule questions.
- Distractors — wrong under either rule — were chosen 0 time(s) out of 24.

### Caveats the probe already knows about

- Three options per question means chance is 33%, so 12 questions per arm bound the accuracy estimate only loosely. Treat depth-wise numbers, which rest on four questions each, as directional.
- Every question is asked in its own call with the premise restated. This isolates reasoning inside the world from remembering the world, and so says nothing about whether consistency would hold across a long conversation.
- Multiple choice measures recognition, not construction. A system that could not generate the counterfactual consequence unaided might still recognise it here.
- Both worlds were written by the probe's author, who also wrote the answer key. The entailments are meant to be strict, but an option judged wrong might be defensible under a reading of the rule the author did not consider.

## Adversarial review

A methodological reviewer, shown the design with the subject anonymised, was asked to break this finding. Instrument: v2 neutral-prior, anchored probabilities — calibrated 2026-08-23, PASSES 8/8. The finding **survived**.

- **Survives with probability** 0.50
- **Judged an artifact** False

**Strongest alternative explanation.** The whole depth story rests on 4 items per cell and the whole arm comparison on 12 items per arm, all at or near ceiling. A three-option recognition task with author-written options invites a shallow strategy that is not 'derivation': under the altered premise, the option that lexically echoes or coheres with the just-restated invented rule is very likely the keyed answer, and under the ordinary premise the option that echoes ordinary world knowledge is keyed. That surface-matching policy would produce exactly the observed pattern (12/12 altered, 10/12 control, 0 distractors) without any chained inference, and it would also be indifferent to nominal 'depth', which is precisely what was observed — flat 100% across depths, i.e. the predicted decay never appeared and was scored as confirmation anyway. There is no evidence in the bundle that depth-3 items are actually harder than depth-1 items; 'depth' is an unvalidated author label.

**Specific flaw.** 'Treat depth-wise numbers, which rest on four questions each, as directional' — the headline nonetheless leads with 'depth 1→3 runs 100%/100%/100%'. Four three-option items per depth cannot distinguish 'no decay' from 'decay to 70%'; the confidence interval on 4/4 runs from roughly 0.40 to 1.0. Compounding this, the control arm at 0.833 is a single item away from tripping the author's own 'control below 0.80' falsifier (9/12 = 0.75), so the verdict that separates 'derivation' from 'exotic-option picking' hangs on one question out of twelve.

**What would settle it.** Re-run with free-response (no options) answers, ≥30 items per depth drawn from worlds and keys written by someone other than the probe author, with depth difficulty validated independently (e.g. show that depth-3 items are not answerable from the premise by surface overlap, by testing a lexical-match baseline), and multiple samples per item with randomised option order in the MC variant.

_This reading supersedes 1 earlier one(s) — most recently the retired artifact-prior reviewer at survival 0.22. Full history in the transcript's result.json._

---

_Pre-registration integrity: prereg predates first event._
