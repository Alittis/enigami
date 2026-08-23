# enigami — Backlog

Single source of truth for feedback, bugs and tasks. Item ids use the `EN-` prefix and are
never reused. The implementing commit's subject starts with the item id (`EN-N:`), which is
what links this file to git history.

**Type**: 🐞 Bug · ✨ Enhancement · ❓ Needs discussion · 🔧 Chore
**Priority**: P1 (soon) · P2 (planned) · P3 (nice-to-have)
**Status**: Triage → Todo → Doing → Blocked → Done

---

## Open

### EN-6 🔧 Only one of four probes has been run against the real API — P1 — Doing

- **Problem:** `imagination.counterfactual_world` ran live on 2026-08-23. The other three have
  still only met the offline stub.
- **Want:** One live run of all four probes, findings committed, and the four pre-registered
  hypotheses either supported or refuted on the record.
- **Grounding:** [`enigami/report.py`](../enigami/report.py) refuses offline runs, so
  `findings/INDEX.md` correctly reads "no live runs yet".
- **Discussion:** Unblocked — key is set and the live path is fixed (`EN-11`). The first live
  run cost $0.268 for 25 calls, so the remaining three should land near $1. Run
  `uv run enigami run intelligence wisdom creativity`.
- **Verify:** `findings/INDEX.md` lists four probes with verdicts; `uv run enigami verify`
  reports zero unverifiable pre-registrations.

### EN-10 🐞 The imagination probe cannot support the claim it makes — P1 — Todo

- **Problem:** The first live run returned 100% inside the invented worlds and 83% under the
  ordinary rule, and the pre-registered rule called that `supports`. The anonymised reviewer
  refuted it and is right on every count. Verified independently: 12/12 versus 10/12 is Fisher
  exact two-tailed **p = 0.478**, indistinguishable from no difference; and the control arm at
  0.833 sits **one item** from the 0.80 falsifier — a third over-compliance error would have
  flipped the verdict to refuted. A conclusion that hinges on one item is not a conclusion.
- **Want:** A redesign that can actually discriminate. From the review, in priority order:
  1. **Open-ended generation instead of multiple choice.** With options present, "pick whichever
     option is consistent with the sentence I was just handed" scores 12/12 with no derivation,
     and flat 100%/100%/100% across depths is exactly what that shallow policy predicts.
  2. **A grader who wrote neither the worlds nor the key.**
  3. **≥30 items per depth.** Four per depth cell gives a 95% CI of roughly 0.40–1.00; it cannot
     tell "no decay" from "no power to see decay".
  4. **Depth-3 items where the counterfactual answer has no more lexical overlap with the stated
     premise than the real-world answer does.** Surface echo is currently a free path to correct.
  5. **A premise-omitted arm**, to measure how much the option set alone gives away.
- **Grounding:** [`findings/imagination.counterfactual_world.md`](../findings/imagination.counterfactual_world.md)
  carries the full review; raw run in `transcripts/20260823-094805-imagination.counterfactual_world/`.
- **The catch:** Requirements 1 and 3 together turn a 25-call probe into a few hundred calls plus
  free-text grading. That is the honest cost of the question, but it should be a deliberate
  decision rather than a quiet scope increase.
- **Verify:** Counterfactual accuracy at depth 3 ≥0.85 under the new conditions, beating
  control-arm over-compliance by a margin that survives a significance test.

### EN-12 🔧 Falsifier thresholds are set without regard to what the sample can resolve — P1 — Todo

- **Problem:** `imagination.counterfactual_world` pre-registered "refuted if control accuracy
  falls below 0.80" against 12 control items. The gap between 10/12 (0.833, supports) and 9/12
  (0.750, refutes) is a single item, so the verdict was decided by sampling noise. The other
  three probes were written the same way and have not been checked for it.
- **Want:** Each probe's thresholds audited against its n, so that no verdict can be flipped by
  one item; where n cannot be raised, the probe should report a verdict of `inconclusive` inside
  the band its sample cannot resolve.
- **Grounding:** `Prereg.falsifier` enforces that a threshold *exists*, not that it is
  meaningful — [`enigami/probe.py`](../enigami/probe.py).
- **The catch:** This is a flaw in the pre-registration mechanism, which is the repo's central
  claim. Worth fixing in `Prereg` (require a stated resolution) rather than probe by probe.
- **Verify:** For every probe, a one-item change at the threshold moves the verdict to
  `inconclusive`, never straight from `supports` to `refutes`.

### EN-2 ✨ Nothing separates reasoning from retrieval — P1 — Todo

- **Problem:** `intelligence.calibration` tests self-knowledge, not reasoning. A model that
  has memorised a puzzle is indistinguishable here from one that solves it.
- **Want:** A probe pairing classic puzzles with structurally identical isomorphs whose surface
  is rewritten — different entities, different cover story, same inference. A large gap between
  the pair is retrieval; a small gap is reasoning.
- **Grounding:** The gap between the two conditions is the measurement, so both must be scored
  by the same deterministic key — see `imagination.counterfactual_world` for the two-arm shape.
- **The catch:** Writing an isomorph that is genuinely equally hard is the whole difficulty. A
  rewrite that is accidentally harder produces a gap that looks like contamination.
- **Verify:** Probe loads, offline run green, gap reported with the isomorph's independent
  difficulty argued in the caveats.

### EN-3 ✨ Sycophancy under pushback is untested — P1 — Todo

- **Problem:** `wisdom.reframing_invariance` measures drift across independent calls. It cannot
  see the failure everyone actually encounters: caving within a conversation when the user
  pushes back.
- **Want:** State a defensible position, then push back in two conditions — social pressure with
  no new argument, versus a genuine new argument. Wisdom holds in the first and moves in the
  second. Same invariance/responsiveness shape, applied to conversational pressure.
- **Grounding:** Named as a scope limit in
  [`probes/wisdom/reframing_invariance.py`](../probes/wisdom/reframing_invariance.py) caveats.
- **The catch:** Needs multi-turn calls; `Subject.ask` is single-turn today and will need a
  conversation method.
- **Verify:** Position-change rate under pressure-only pushback is reported separately from
  under argued pushback.

### EN-5 ✨ Counterfactual consistency is only tested one question at a time — P2 — Todo

- **Problem:** Each question in `imagination.counterfactual_world` restates the world in its
  own call. That isolates reasoning from memory deliberately, but leaves the more interesting
  question untouched: does an invented world survive twenty turns of conversation?
- **Want:** A long-conversation variant where the world is established once, then probed at
  increasing distance, watching for drift back to the real world.
- **Grounding:** Named as a scope limit in the probe's caveats.
- **The catch:** Depends on the same multi-turn support as `EN-3`; build that once.
- **Verify:** Reversion rate reported as a function of turn depth.

### EN-4 ✨ Creativity is measured only as diversity — P2 — Todo

- **Problem:** `creativity.mode_collapse` counts distinct ideas. It says nothing about whether
  the system can satisfy constraints that genuinely pull against each other, where the cheap
  move is to quietly drop one.
- **Want:** A probe with adversarial constraint sets and deterministic per-constraint checking,
  so dropping a constraint is detected rather than judged.
- **Verify:** Per-constraint satisfaction rates, and which constraint is dropped first.

### EN-7 ❓ The judge is the same model family as the subject — P2 — Triage

- **Problem:** `config.JUDGE_MODEL` equals `SUBJECT_MODEL`. Shared failure modes mean a judged
  finding is less independent than it looks.
- **Want:** A decision on what to do about it.
- **Discussion:** Three options, none free. (a) A weaker judge — cheaper and genuinely more
  independent, but likely unable to detect a stronger subject's failures, which biases toward
  "supports". (b) A non-Claude judge — real independence, but adds a provider and a dependency
  to a repo that currently has one. (c) Human spot-checking of a sample — the only true ground
  truth, and the only option that does not scale. **Open question: which?**
- **Grounding:** [`project/ARCHITECTURE.md`](ARCHITECTURE.md) §4 records the current trade.
- **Verify:** A decision written into ARCHITECTURE.md §4, not a code change.

### EN-9 🐞 Eight calibration answer keys were written from memory — P2 — Todo

- **Problem:** The `FACTUAL` items in `intelligence.calibration` have keys the probe's author
  wrote from recall. A wrong key registers as a subject error and inflates measured
  overconfidence.
- **Want:** Each factual key carries a citation, or the item is dropped.
- **Grounding:** [`probes/intelligence/calibration.py`](../probes/intelligence/calibration.py)
  `FACTUAL`; already disclosed in the probe's caveats.
- **The catch:** The six computed and five false-premise items do not have this dependency, so
  the cheap fix is to drop the factual items entirely — at the cost of losing the mid-range of
  the confidence scale, which is where calibration is most interesting.
- **Verify:** Every remaining factual item has a source, or `FACTUAL` is empty.

### EN-8 🔧 Full runs pay list price — P3 — Todo

- **Problem:** Probes issue many small independent calls at full rate. The Batch API is 50%
  cheaper and these workloads are not latency-sensitive.
- **Want:** An opt-in `--batch` path for probes whose calls are independent.
- **The catch:** Batch results return in any order and must be keyed by `custom_id`, and
  `fallbacks` is rejected on batches.
- **Verify:** A batched run costs about half of the same run unbatched.

---

## Done

### EN-11 🐞 The live path was broken in two ways the offline stub could not surface — P1 — Done

- **Problem:** The first live run 400'd. Two independent defects. (a) `strict_schema` emitted
  `minimum`/`maximum` from Pydantic's `Field(ge=…, le=…)`; the API rejects them —
  *"For 'number' type, properties maximum, minimum are not supported"*. (b) Refutation shared a
  `try` block with the probe, so that 400 on the review call discarded a finding that had
  already cost 24 successful calls.
- **Want:** Unsupported keywords stripped from the schema with bounds still enforced on parse,
  and refutation isolated as its own failure domain.
- **Shipped:** 2026-08-23, commit `<this commit>` — bounds restated in field descriptions since
  they no longer reach the model; two regression tests added (24 tests total). Verified by the
  successful re-run: 25 calls, $0.268, finding and review both recorded.

### EN-1 🔧 Empty directory, no harness, no method — P1 — Done

- **Problem:** The repo was an empty directory. Investigating four capacities needed a method
  before it needed code, and specifically a method resistant to the subject grading itself.
- **Want:** A harness where pre-registration is enforced by the constructor, scoring is blind
  where it cannot be deterministic, and every finding survives an anonymised hostile review —
  plus one fully realised probe per capacity.
- **Shipped:** 2026-08-23 — 8 harness modules, 4 probes, 21 tests, `project/` docs. Verified by
  `uv run pytest -q` (21 passed) and `uv run enigami run --offline all` (4 probes end to end,
  0 findings written, which is the correct offline behaviour).

---

## Progress log

- **2026-08-23** — **The design constraint that mattered was an API fact, not a philosophical
  one.** `temperature` no longer exists on the current Claude model family and returns a 400,
  which removes the obvious way to study output diversity. `creativity.mode_collapse` varies by
  independent resampling instead, and `Subject.ask` raises on sampling parameters rather than
  letting the API reject them later. Caught by reading the `claude-api` skill before writing
  code, not by a failing request.
- **2026-08-23** — **Every probe got a control condition that could beat it.** The design rule
  that did the most work: `Prereg.null_model` is required and must describe a system without the
  capacity that would nonetheless score well. It forced the decision metric in
  `intelligence.calibration` from calibration error to discrimination (a constant-confidence
  responder scores well on the former), and it added the ordinary-rule arm to
  `imagination.counterfactual_world` (an exotic-option picker scores well without it).
- **2026-08-23** — **The offline stub found a real gap in itself.** `test_offline_stub_validates_
  against_the_schema_it_is_given` failed on a nested Pydantic model; the stub was flat. Fixed by
  making it recurse over the resolved strict schema rather than by relaxing the test. No shipped
  probe used a nested object field, so this would have surfaced later as a confusing failure in
  a probe someone else wrote.
