# enigami — Backlog

Single source of truth for feedback, bugs and tasks. Item ids use the `EN-` prefix and are
never reused. The implementing commit's subject starts with the item id (`EN-N:`), which is
what links this file to git history.

**Type**: 🐞 Bug · ✨ Enhancement · ❓ Needs discussion · 🔧 Chore
**Priority**: P1 (soon) · P2 (planned) · P3 (nice-to-have)
**Status**: Triage → Todo → Doing → Blocked → Done

---

## Open

### EN-6 🔧 No probe has ever been run against the real API — P1 — Blocked

- **Problem:** Every probe has been exercised only against the offline stub. Nothing in
  `findings/` is real, and no hypothesis has met a result.
- **Want:** One live run of all four probes, findings committed, and the four pre-registered
  hypotheses either supported or refuted on the record.
- **Grounding:** [`enigami/report.py`](../enigami/report.py) refuses offline runs, so
  `findings/INDEX.md` correctly reads "no live runs yet".
- **Discussion:** Blocked on an API key. `./deploy/scripts/setup-anthropic-env.sh`, then
  `uv run enigami run all`. Roughly 114 calls, a few dollars.
- **Verify:** `findings/INDEX.md` lists four probes with verdicts; `uv run enigami verify`
  reports zero unverifiable pre-registrations.

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
