# enigami — Backlog

Single source of truth for feedback, bugs and tasks. Item ids use the `EN-` prefix and are
never reused. The implementing commit's subject starts with the item id (`EN-N:`), which is
what links this file to git history.

**Type**: 🐞 Bug · ✨ Enhancement · ❓ Needs discussion · 🔧 Chore
**Priority**: P1 (soon) · P2 (planned) · P3 (nice-to-have)
**Status**: Triage → Todo → Doing → Blocked → Done

---

## Open

### EN-6 🔧 All four probes have run; not one produced a usable verdict — P1 — Done

- **Problem:** All four ran live on 2026-08-23 for $1.21 total. All four scored `supports`; all
  four were refuted by review (survival 0.22–0.30). Not one verdict can currently be cited.
- **Want:** One live run of all four probes, findings committed, and the four pre-registered
  hypotheses either supported or refuted on the record.
- **Grounding:** [`enigami/report.py`](../enigami/report.py) refuses offline runs, so
  `findings/INDEX.md` correctly reads "no live runs yet".
- **Discussion:** Unblocked — key is set and the live path is fixed (`EN-11`). The first live
  run cost $0.268 for 25 calls, so the remaining three should land near $1. Run
  `uv run enigami run intelligence wisdom creativity`.
- **Verify:** Four probes listed with verdicts — done. Remaining: a verdict that survives
  review, which needs EN-13 (is the reviewer calibrated?) answered first.
- **Shipped:** 2026-08-23 — closed by the re-review under the calibrated instrument and its
  majority-of-3 protocol. Final readings of record: imagination.counterfactual_world
  **survived 3/3** (reps 0.50/0.52/0.62 — unanimous but weak; the reviewer's residual doubts
  are exactly EN-10's redesign list); creativity.mode_collapse refuted 1/3 (median 0.45,
  floor-arm confound EN-16); wisdom.reframing_invariance refuted 1/3 (median 0.45,
  aggregation EN-14 plus a new point: the responsiveness metric counts magnitude including
  the wrong-direction move); intelligence.calibration refuted 0/3 (median 0.12, the recorded
  finding predates the EN-18 fix and carries the contradiction). Every superseded reading is
  preserved in review_history. Surviving verdicts beyond this one item await the redesigns.

### EN-10 🐞 The imagination probe cannot support the claim it makes — P1 — Done

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
- **Discussion (2026-08-23 rescan):** Both control-arm misses turn out to be defective items,
  not subject errors. Tessarine depth-3 control: the keyed answer is membranes-spread-wide — on
  an explicitly *airless* planet, where membranes do nothing; the subject said exactly that and
  was scored wrong. Verrin depth-3 control: the keyed answer is a will — under a control premise
  stating the rule "admits no wills"; no option is correct there at all. True control accuracy on
  well-formed items is 10/10, and `over_compliance = 2/12` (which the reviewer read as
  exotic-picker leakage) is an artifact of the key. Both defects sit at depth 3: the probe author
  failed to hold his own worlds steady exactly where the subject was being tested on it.
- **The catch:** Requirements 1 and 3 together turn a 25-call probe into a few hundred calls plus
  free-text grading. That is the honest cost of the question, but it should be a deliberate
  decision rather than a quiet scope increase.
- **Verify:** Counterfactual accuracy at depth 3 ≥0.85 under the new conditions, beating
  control-arm over-compliance by a margin that survives a significance test.

- **Shipped:** 2026-08-23 — v2: free text (no options to eliminate), third world, premise-omitted leakage arm, blind proposition-matching grader, arm-level decision with Fisher exact. Result: supports, survived 3/3 at 0.78 (92%/96%/3.7%). Verify satisfied differently than written: the decision is arm-level per EN-12; depth-3 ran 1.00 directionally.
### EN-12 🔧 Falsifier thresholds are set without regard to what the sample can resolve — P1 — Done

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

- **Shipped:** 2026-08-23 — every v2 prereg uses separated verdict bands with an inconclusive middle and explicit validity windows. Live evidence the bands work: calibration returned no-verdict at ceiling instead of a number; wisdom sat inconclusive rather than flipping.
### EN-13 ❓ The reviewer refuted 4 of 4 findings, and nothing establishes it can do otherwise — P1 — Done

- **Problem:** Every finding was judged an artifact (survival 0.22, 0.25, 0.30, 0.30). A reviewer
  that refutes everything carries exactly as little information as one that accepts everything,
  and its prior was set to "artifact" by instruction in `refute.SYSTEM`. Until it demonstrates it
  can pass something, its verdicts are not evidence.
- **Counter-evidence, which is why this is `❓` and not `🐞`:** three of its four critiques were
  independently checked and were correct — the Fisher exact value (p = 0.4783), the fabricated
  discrimination metric (a genuine code bug, `EN-18`), and the item-count mismatch. Generic
  hostility does not produce checkable, specific, correct claims.
- **Want:** A positive control. Feed the reviewer a finding known to be sound — a deliberately
  over-powered probe, or a synthetic result with a real effect and adequate n — and see whether
  it passes. Also feed it a known-bad finding to confirm it still refutes.
- **The catch:** Constructing a finding that is *known* sound requires the ground truth the
  harness exists to establish. The tractable version is synthetic: fabricate a result with a
  large effect, n in the hundreds, and no design flaw, and check the reviewer does not invent one.
- **Answered (2026-08-23):** Built and run — 8 cases × 3 reps, pre-registered rule committed at
  `ce65fe5` before the live run. **Stage 1 (instrument as used): REFUTES-EVERYTHING** — 1/4
  sound cases survived, 4/4 flawed refuted. That verdict is binding: the four probe-refutation
  *labels* are downgraded to advisory. Stage 2 (neutral prior, diagnostic): sound 2/4, flawed
  still 4/4 at essentially unchanged probabilities — the default-to-artifact instruction costs
  specificity and buys no sensitivity (EN-21). The two sound cases that failed both stages
  failed because **the reviewer was right and the case labels were wrong**: both lack
  manipulation checks, a real hole the author missed while certifying them (EN-22). Flaw-match
  on the flawed cases was exact — the post-hoc case's review named both the post-treatment
  conditioning and the verdict-contradicts-falsifier tell.
- **Shipped:** 2026-08-23 — `enigami calibrate`, `findings/REVIEWER_CALIBRATION.md`, run in
  `transcripts/*-reviewer-calibration/`. $2.12, 48 calls.

### EN-21 🔧 Drop the reviewer's default-to-artifact instruction — P1 — Done

- **Problem:** Calibration stage 2 isolated the variable: removing only the "assume artifact by
  default" sentence moved `sound_calibration_n400` from 1/3 surviving (mean p 0.433) to 3/3
  (0.773) while all four flawed cases stayed refuted at essentially unchanged probabilities
  (0.04–0.21). The hostile prior costs specificity and buys zero sensitivity — flaw detection
  comes from the failure-mode checklist, not the prior.
- **Want:** `refute.SYSTEM` rewritten to the stage-2 neutral form, plus explicit anchors for
  `survives_probability` (what 0.2, 0.5, 0.8 mean), then recalibrate against the repaired case
  set (EN-22).
- **Grounding:** [`enigami/reviewer_control.py`](../enigami/reviewer_control.py) `STAGE2_SYSTEM`
  is the tested wording; stage-2 numbers in `findings/REVIEWER_CALIBRATION.md`.
- **The catch:** Stage 2 still only reached 2/4 sound — but both residual failures traced to
  defects in the cases, not the reviewer (EN-22). The cases were fixed first.
- **Verify:** PASSES on the repaired calibration set — met.
- **Shipped:** 2026-08-23, commit `3859d5f` — SYSTEM rewritten to the tested neutral form, plus
  probability anchors (0.9/0.7/0.5/0.3/0.1 with defined meanings), a fatal-flaw-versus-caveat
  rule, and the anchors replacing "default low when the evidence is thin" in the schema field.
  Stage 2 retired. Verified by the recalibration: **PASSES, 8/8 cases, 24/24 reps** — sound
  mean p 0.73–0.81, flawed 0.05–0.19, a 0.54 separation gap ($1.06).

### EN-22 🐞 Three "sound" calibration cases contained real flaws the reviewer legitimately caught — P1 — Done

- **Problem:** `sound_sycophancy_null` has no manipulation check — nothing validates that the
  "argued pushback" arm contained genuine arguments, so its affirmed null is uninterpretable and
  its power claim guards the wrong failure mode. `sound_invariance_worstcase` never establishes
  that the irrelevant reframings are strong enough to move any system — decisive-by-design vs
  ignorable-by-design, both by the same author. The reviewer found both holes in every rep, both
  stages. The calibration's ground truth was wrong for 2 of 4 sound cases.
- **Want:** Repair both cases (add manipulation-check evidence: human-rated argument strength;
  a susceptible-system positive control showing the reframings can move something) or replace
  them with cases that survive the author's own adversarial pass. Then rerun `enigami calibrate`.
- **Grounding:** Reviewer objections quoted in `findings/REVIEWER_CALIBRATION.md`; the same
  manipulation-check gap exists in the real wisdom probe and folds into EN-19's fix.
- **The catch:** For the second time today the tool outperformed the toolmaker (EN-18 was the
  first). The temptation is to keep relabeling cases until the reviewer passes — that is
  p-hacking the calibration. Repairs must add evidence the reviewer said was missing, not
  reword until it agrees.
- **Verify:** Every sound case survives an adversarial read by a fresh session before the rerun.
  *Satisfied differently than written:* the adversarial read came from the failing reviewer's own
  recorded objections — three reps per case, each independently naming the same hole — a stronger
  source than a fresh session, since the repairs answer exact objections on record.
- **Shipped:** 2026-08-23, commit `3859d5f` — scope grew from two cases to three: the rescan of
  the first calibration showed `sound_calibration_n400`'s objections were also right (pooled
  discrimination over a curated difficulty mixture is fakeable by a stratified-constant emitter).
  Repairs, each adding exactly the missing evidence: within-band discrimination breakdown with
  the null upgraded to the stratified emitter (calibration case); a potency gate showing the
  identical reframings move a susceptibility-instructed system 18.7 points, numeric-anchor
  authorities, vividness ratings (invariance case); a rater-verified manipulation check and a
  0.87 decisive-refutation positive-control arm (sycophancy case). Verified by the
  recalibration: all three now survive 3/3 at p 0.74–0.81 while all four planted flaws are
  still refuted 0/3 — sensitivity was not traded for specificity.

### EN-14 🐞 The wisdom verdict averages across dilemmas and hides a case that met the falsifier — P1 — Done

- **Problem:** Averaged, drift is 4.7 against material movement of 41.3 — a clean 8.7x. Per
  dilemma, `authorship` had an unargued authority move the judgment **11.3 points** while the
  decisive fact moved it **10.7**. The falsifier as written compares
  means (4.7 vs 41.3) and therefore did not fire — the reviewer's "verbatim" was an
  overstatement, repeated here uncritically on 2026-08-23 and corrected the same day in the
  rescan. The real defect stands unchanged: the prereg aggregated where it should have bound the
  worst case, so a dilemma where an unargued authority outweighs the decisive fact still scores
  `supports`.
- **Want:** The verdict computed per dilemma and aggregated by the worst case, not the mean. One
  dilemma meeting the falsifier should refute, or at minimum force `inconclusive`.
- **Grounding:** [`probes/wisdom/reframing_invariance.py`](../probes/wisdom/reframing_invariance.py)
  computes `mean_drift` and `mean_response` across all dilemmas before comparing them.
- **Verify:** Re-scoring the recorded run in `transcripts/20260823-095455-*` yields `refutes` or
  `inconclusive`, not `supports`.

- **Shipped:** 2026-08-23 — v2.2: the verdict binds the per-dilemma worst case; refutation clauses evaluate before any validity gate; the ratio test requires the dilemma's own material fact to have demonstrably worked (8+ directional points). Under these rules v1's and v2's data read refutes/inconclusive, never supports — the Verify line met.
### EN-15 🐞 Confidence cannot be measured while the subject out-computes every item bank — P1 — Done

- **Problem:** 19/19 correct, including all five false-premise traps. With no wrong answers the
  decision metric does not exist and the falsifier can never fire, so the pre-registration is
  vacuous on this item set.
- **Want:** Items hard enough to produce a genuine error rate — target 60–80% accuracy so the
  confidence scale is exercised across its range. Harder computed items (longer arithmetic,
  deeper primes), more obscure factual items, and false premises subtler than a fabricated
  element name.
- **Grounding:** `accuracy_computed`, `accuracy_factual` and `accuracy_false_premise` all 1.0 in
  `transcripts/20260823-095404-*`.
- **The catch:** Tuning items until errors appear is p-hacking the difficulty. Set the target
  accuracy band first, write items to it, and do not iterate on the observed result.
- **Verify:** Accuracy between 0.6 and 0.8, and discrimination defined.
- **Discussion (2026-08-23, v3 result):** Near-miss traps ceilinged too — 23/23 including all
  15 twisted variants (EN-23). Two item classes now exhausted. Remaining options: effort-capped
  answering (guaranteed errors, openly a different subject condition) or cited obscure facts
  (ceiling-risky). The trap bank itself is kept: its canonical/twisted contrast is EN-2's
  instrument, and 15/15 trap detection at high effort is a standing directional finding.
- **Decision (2026-08-23):** The user accepted option (c): *unmeasurable at high effort* stands
  as the intelligence-calibration result of record. Three ceilings — 19/19, 42/42, 23/23 — with
  the guard's no-verdict reading surviving review twice is the finding; no further item classes
  will be tried under this item. Reopening calibration means a new item with a new construct
  (e.g. the effort-capped condition), not a fourth bank here.
- **Discussion (2026-08-23, v2 result):** v2 shipped 42 all-computed items across three bands,
  with a validity window returning no-verdict outside 0.35–0.90 accuracy. The subject scored
  **42/42** — the 763rd prime, the digit sum of 99^99, 170 Collatz steps — so with 16k thinking
  tokens, pure computation cannot produce an error rate on this subject at any humane cost. The
  guard held (the ceiling reading survived review 3/3 at 0.85). Blocked on the item-class
  decision now tracked as EN-23. **Open question.**

### EN-17 🐞 A hypothesis can make several claims while the falsifier tests only one — P2 — Done

- **Problem:** The wisdom prereg predicted "the sympathy condition will produce the largest of the
  three drifts". Sympathy produced the **smallest** (3.2 versus authority's 7.0) — the prediction
  was wrong — and the verdict was `supports` anyway, because the falsifier only covered mean
  drift. `Prereg` enforces that a falsifier exists, not that it covers what the hypothesis claims.
- **Want:** Either hypotheses restricted to the single claim the falsifier tests, or a structured
  prereg listing each claim with its own falsifier and verdict.
- **Verify:** No probe's hypothesis asserts something its falsifier cannot reach.

- **Shipped:** 2026-08-23 — all four v2 preregs claim only what their falsifiers decide; side measures (themes, depth trends, citation rates) are explicitly evidence that decides nothing.
### EN-16 🐞 The creativity floor arm confounds constraint with question identity — P2 — Done

- **Problem:** The narrow arm asks a different question with four right answers; the open arm asks
  for an invention. The reviewer is right that "6/10 versus 2/10" is explained by that difference
  alone, and isolates nothing about the system.
- **Want:** A floor from the same question — for example the open question asked with an
  instruction that fixes the answer space — or a human baseline on the identical prompt.
- **The catch:** The narrow arm still does useful work as a metric floor; this is an argument for
  adding an arm, not deleting one.
- **Verify:** A diversity difference that survives holding the question constant.

- **Shipped:** 2026-08-23 — v2 floor is the same invention task with the concept pinned to v1's own modal idea. Result: supports, survived 2/3 at 0.62 (7 vs 4 ideas, themes 3 vs 1).
### EN-19 🐞 Wisdom probe variants are not single-factor changes — P2 — Done

- **Problem:** Two construction defects found in the 2026-08-23 rescan. (a) `floodbudget`'s
  material variant changes *two* things at once — it adds the sole-water-supply fact but also
  deletes the relocation-list detail — and it bounds the plant's harm at "six weeks without
  drinking water", arguably making the plant *less* compelling than the base's open-ended
  framing; the `material_direction=+1` key is contestable, so the "1 of 3 material changes moved
  the wrong way" evidence line is contaminated. (b) `authorship`'s sympathy sentence describes
  the supervisor but is appended under the header `SITUATION OF THE STUDENT`.
- **Want:** Every variant differs from base by exactly one clause, diff-checkable; sympathy text
  attached to the party it describes; direction keys re-argued in a sentence each.
- **Grounding:** [`probes/wisdom/reframing_invariance.py`](../probes/wisdom/reframing_invariance.py)
  `DILEMMAS`; raw rows in `transcripts/20260823-095455-*`. The subject's base-condition
  floodbudget reasoning already assumed the plant serves the whole town, so making that explicit
  added less than deleting the relocation detail removed.
- **Verify:** A diff of each variant against base touches one clause; every direction key
  carries its argument.

- **Shipped:** 2026-08-23 — every variant is base plus exactly one appended sentence, asserted in code at run time; sympathy attaches to the party it describes; authority anchors moved to extremes after v2.1 showed two sat at or below the base positions.
### EN-23 ❓ What item class can make this subject err honestly? — P1 — Done

- **Problem:** EN-15's v2 proved computable items cannot produce errors at 16k thinking tokens,
  and without errors calibration has nothing to measure. The construct needs tasks where the
  subject is genuinely uncertain while ground truth stays verifiable.
- **Want:** A decision between: (a) effort-capped answering — same items, thinking constrained,
  framed openly as "the subject at low effort"; (b) verifiable non-computable items with cited
  keys (reintroduces EN-9's authoring risk, mitigated by citations); (c) prediction items scored
  later; (d) adversarial near-miss items designed to invite specific slips.
- **Verify:** A run landing inside the 0.35–0.90 validity window.
- **Shipped:** 2026-08-23, commit `23af1cf` — the user chose near-miss traps; v3 ran 8 canonical
  + 15 twisted items with computed keys (Monty variants by enumeration: 67 vs 50; birthday by
  search: 23 vs 253; coins by exhaustion). **Verify not met: 23/23, ceiling again** — the
  subject caught every trap, inverted ones included, with confidence dipping 0.976→0.959 on
  twisted items. The reading survived review 2/3 at 0.55. The question this item asked is now
  sharper and lives on in EN-15: after brutal computation and near-miss traps both ceilinged,
  effort-capped answering is the one remaining guaranteed-error class.

### EN-24 ✨ Wisdom needs power, not more redesigns — P2 — Done

- **Problem:** v2.2's design is sound; the calibrated reviewer's remaining objection is
  resolution only — base noise from 3 reps, condition deltas from 2-sample means. The verdict
  was a near-miss inconclusive: one clause, one dilemma.
- **Want:** The identical v2.2 design at 6 reps per cell (~200 calls, ~$3), the rep count the
  synthetic sound-invariance case already showed satisfies the calibrated reviewer.
- **Grounding:** `transcripts/20260823-115100-*` — strengthened facts moved +58/+15/+15/+17
  against mean drift 4.9 and zero wrong-direction moves; authority citation rose to 5/8 (from
  v1's 0/6) once anchors were extreme.
- **Verify:** A verdict other than inconclusive, whichever it is, surviving review.
- **Shipped:** 2026-08-23, commit `3f80502` — v2.3: 6 reps per cell everywhere, support-margin
  noise floor = max(8, 2×SE of the material effect). **Verify as written was not met**: the
  verdict is again inconclusive — but no longer for power reasons. At SE 0.8–2.1 the blocker is
  one localized, replicated phenomenon: floodbudget's order-swap and sympathy drifts (−10.5,
  ~5 SE, present in all four design versions) against a material effect (+11.3) capped by a
  base of 79.2 with no upward headroom. Three of four dilemmas pass the support margin cleanly.
  The reading survived review 2/3 at 0.50; the residual design fact is EN-25.

### EN-25 🐞 Floodbudget's scale is saturated and one dilemma's drift decides the run — P2 — Done

- **Problem:** Floodbudget's base allocation sits at ~79 of 100, so its material fact can move
  at most ~21 points up while irrelevant drift has all the room it wants downward — the
  half-material support margin is nearly unpassable there by construction. Meanwhile its
  order-swap/sympathy drift (−10.5, ~5 SE) is the one robust "unwisdom" signal in the data and
  deserves its own clean measurement rather than being an obstruction.
- **Want:** Per the calibrated reviewer's prescription: rebuild dilemmas so base allocations
  land mid-scale (40–60), giving both directions headroom; validate each sympathy/authority
  sentence's potency per dilemma; and consider promoting the replicated order-swap effect to
  its own probe (presentation-order sensitivity), where it is the phenomenon, not the noise.
- **Grounding:** `transcripts/20260823-121229-*`; the drift replicates across
  `20260823-095455` (−9.3), `114452` (−12.5), `115100` (−6.0), `121229` (−10.5).
- **Verify:** All four dilemmas' bases land 40–60 in a pilot; the wisdom verdict resolves out
  of inconclusive, whichever way.
- **Shipped:** 2026-08-23, commit `513e67a` — four rebuilt mid-scale dilemmas (severance,
  estate, collision, reservoir); pilot passed first round (50.0/50.0/44.0/40.0). **Verify half
  met:** bases ✓; the verdict stayed inconclusive ✗ — but no longer from design artifacts: the
  blocker is the order-swap effect itself, replicated at +14.8 (~7 SE) on collision's 45.8 base
  after replicating at −10.5 on floodbudget's 79. De-confounding was the item's purpose and it
  succeeded; the promotion condition fired and the effect is now EN-26's phenomenon. Also
  recorded: sympathy stimuli are null manipulations on this subject (4/24 cited, inert even
  susceptibility-instructed), so per-dilemma sympathy potency validation is unachievable with
  the instructed-arm instrument — the self-evident-potency clause is what functions. Forcing a
  fourth design to extract a binary verdict would be verdict-shopping; the structured answer
  stands in the progress log. Cost: pilot $0.18 + run $2.35, inside the $2.5–3.2 estimate.

### EN-2 ✨ Nothing separates reasoning from retrieval — P1 — Done

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
- **Shipped:** 2026-08-23, commit `276b5ee` (pre-registered) — `intelligence.isomorph_transfer`:
  12 famous structures × (famous + 2 isomorphs), 36 solver-computed keys, famous values as test
  oracles, import-time guard against isomorph keys colliding with famous answers (fired twice
  during authoring). Result: **supports, survived 3/3 at 0.75** — 100% both arms, gap 0.0, zero
  famous-answer intrusions, one visible exclusion. Cost $1.38 vs the pre-run estimate $1.8–4.0.
  The reviewer's residual scopes the successor: method-retrieval vs method-derivation needs
  novel-structure puzzles — a candidate future item, not this one.


### EN-27 ✨ The product is a skill: evaluate and improve W/C/I in-session — P1 — Done

- **Problem:** The goal crystallised on 2026-08-23: enigami's deliverable is a Claude Code
  **skill** that evaluates and improves wisdom, creativity and imagination for users working
  with Claude on prepaid plans — not an open-ended API research program. The skill's users have
  no API keys, so the product must run in-session; its remaining development therefore moves
  in-session too (fresh-context subagents on plan usage, $0 marginal API cost). The $23.90 of
  API spend to date is the R&D that bought the calibrated method and the evidence base the
  skill will teach.
- **Want:** A skill with three parts. (1) A compact eval battery run via subagents — one
  subagent per item, fresh context = independence — e.g. order-swap vignette pairs, a
  creativity diversity sample, imagination free-response with a leakage check; ≤ ~30 calls per
  run. (2) A scorecard comparing the user's readings against this repo's baselines. (3) An
  improvement playbook applying the measured findings as prompt patterns: judge in both orders
  and average (order effects of 10–15 points, twice replicated); ask for the first idea to be
  discarded (novelty push added ideas and themes); restate invented rules explicitly (92–100%
  adherence); strip or flag unargued authority claims (moderate anchors dragged 16.7 points;
  extreme named ones were resisted); lead with decisive facts (12/12 right-direction).
- **Mechanism demo (2026-08-23):** the collision order-swap item ran as 4 in-session subagents
  (2 per order): van-first 35/55, car-first 50/55 — direction matches the API finding (car
  presented first bears more), magnitude unresolved at n=2, ~31k plan tokens per call, $0 API.
- **The catch:** In-session subjects carry the Claude Code system prompt — ecologically right
  for the skill's purpose but not comparable 1:1 with the bare-API baselines; subagents have no
  structured-output enforcement (lenient parsing needed); plan caps bound battery size. The
  eval is a screening instrument; the API harness stays frozen as the calibration lab.
- **Verify:** The skill runs end-to-end in a fresh session on plan usage only and produces a
  scorecard plus applied playbook.
- **Shipped:** 2026-08-23, commits `4375b80` + this one — skill/enigami/ (SKILL.md, battery.py,
  PLAYBOOK.md), installed via symlink to ~/.claude/skills/enigami and visible in the session
  skill list. Acceptance run passed the Verify line: 26 subject subagents + 2 blind judges,
  entirely on plan usage (~1.0M tokens incl. the 4-agent mechanism demo, $0 API), zero
  unparseable responses, scorecard written to enigami-scorecard-2026-08-23.md. Readings:
  wisdom order effects +2.5/−4.0 (both under the 8-point flag — smaller in-session than the
  bare-API +14.8); creativity 6/6 distinct ideas across 4 themes (the Lull reappeared, once);
  imagination 4/4 altered + 2/2 control; intelligence 6/6 at LOW effort — the honesty rule
  reported it as unmeasured-at-ceiling, spawning EN-28.

### EN-28 🐞 "Low effort" does not make the subject err either — P3 — Done

- **Problem:** The skill's intelligence module pins subagent effort to low, expecting errors
  that make calibration measurable. The acceptance run came back 6/6 — including Collatz-703
  (36 seconds of visible deliberation) and 3^333 mod 1009 — so the effort cap constrains
  style, not arithmetic reliability, at least on this bank. Fourth ceiling of the project.
- **Want:** Either a genuinely harder low-effort bank (items beyond what constrained thinking
  can grind: longer chains, larger expansions), or drop the calibration pretence and reframe
  the module as what it demonstrably is — a reliability spot-check whose honest output at
  ceiling is "no errors to calibrate against".
- **Grounding:** enigami-scorecard-2026-08-23.md; the lab's three previous ceilings (19/19,
  42/42, 23/23) at high effort.
- **Verify:** Either a run inside the 0.35–0.90 window, or the module's copy re-scoped.
- **Shipped:** 2026-08-23 — re-scoped (the second option): the module is now titled a
  reliability spot-check at low effort, calibration when errors permit; the scorecard baseline
  and PLAYBOOK pattern 2 state plainly that claude-opus-5 stayed at ceiling at every effort
  tried, and that on models which do err the discrimination reading becomes meaningful.

### EN-29 🔧 Publication readiness: public repo, MIT, portable skill — P1 — Done

- **Problem:** The user decided the repo goes public (skill and lab together), which changes
  what the skill must survive: strangers, other machines, other models, and permanent git
  history. Known cracks: local paths in provenance, model-unscoped claims (one measurably
  falsified for claude-opus-5), the EN-28 mislabel, published-item contamination, and the
  author's work email in every commit.
- **Want:** The fine-tune pass before any remote exists; the remote itself is deliberately NOT
  created yet.
- **Shipped:** 2026-08-23. (1) All 30 commits' author/committer rewritten to
  alittis@icloud.com before any push can bake the work address into public history; the
  backlog's commit references remapped to the post-rewrite SHAs, including one that had
  pointed at an amended-away commit. (2) LICENSE: MIT. (3) SKILL.md de-localized — provenance
  points into the repo it ships in, install documented in README, no local paths anywhere
  tracked. (4) Every claim scoped to claude-opus-5/2026-08-23 with "priors, not norms"
  language in SKILL.md, PLAYBOOK.md and the scorecard header; the playbook's low-effort
  premise corrected to what the acceptance run actually measured. (5) EN-28 resolved by
  re-scope: the intelligence module is now a reliability spot-check that becomes calibration
  when a model errs. (6) Contamination clause added and `--custom` implemented across
  items/judgeprompts/score (private intelligence/wisdom/imagination items, schema documented,
  id-collision refused loudly, tested). (7) Instruction lint: effort-unavailable and
  judge-failure paths added, all thresholds carry their scale. (8) Hygiene: no work-domain strings and no
  absolute local paths in tracked files; report generator now writes repo-relative run paths.
- **Verify:** `git log` shows a single public identity; 39 tests pass; `battery.py items`
  round-trips with and without `--custom`. **Remaining, deliberately:** create the public
  remote and push — on the user's word only.

### EN-30 🐞 The battery's lenient parsers mis-scored silently — seven confirmed audit findings — P1 — Done

- **Problem:** The pre-publication adversarial audit (5 auditors + skeptics; battery dimension
  completed first) found seven real defects in `skill/enigami/battery.py`, every one confirmed
  by direct reproduction before fixing. The worst four were silent mis-scores — the exact
  failure class this repo exists to prevent: (1) an unparseable imagination-grader reply was
  scored as the subject failing every item (0/4 printed as fact); (2) `_first_json` crashed
  uncaught on JSON followed by brace-containing prose, killing the whole scorecard; (3)
  `_alloc` took the first small integer anywhere, so "Given the 40,000 in damage, 65." scored
  40 — enough to fabricate or mask an order effect at n=2; (4) `_num_conf` matched a bare
  comma (correct answers scored wrong), read prose numbers ("The 300th prime is 1987" → 300),
  and read "Confidence: 10" as certainty 1.0. Plus: an all-unparseable intelligence arm
  vanished from the scorecard instead of being reported; every `open()` was locale-dependent
  (Windows crash on realistic data); and subject responses were spliced into judge prompts
  undelimited, letting a response spoof judge structure — the one channel where the measured
  model could reach its own scores.
- **Shipped:** 2026-08-23. `_first_json` uses `raw_decode` and never raises; a failed grader
  renders "module not scored", judge-omitted ids are counted separately from subject misses,
  and letters are case-normalized; `_alloc` reads only the first line and returns a value only
  when exactly one standalone 0–100 candidate exists (thousands groups and ranges rejected) —
  unambiguous or visibly excluded; `_num_conf` requires a pure-number line for the answer and
  refuses out-of-range confidence; empty arms are reported with their exclusion counts;
  `encoding="utf-8"` on every file op plus stdout reconfigure; subject text is fenced in
  data-only tags with breakout sequences neutralized and both judges instructed accordingly.
  All seven reproductions frozen as a regression bank (40 tests passing). The acceptance run's
  numbers survive unchanged — its responses happened to be clean-format — but the luck is gone
  from the design.

### EN-31 🔧 Full pre-publication audit: 36 confirmed findings fixed — P1 — Done

- **Problem:** Publishing publicly means strangers inherit every defect. A five-dimension
  adversarial audit (battery code, skill docs, harness code, doc truthfulness, residual
  hygiene), each dimension followed by a skeptic that tried to refute its own finder, produced
  38 findings: 36 confirmed, 2 refuted as stale (they described pre-publication-pass code).
- **Blockers, all fixed:** the four battery parser defects (EN-30); `project/BACKLOG.md`'s own
  hygiene claim named the author's work email domain — the exact string the EN-29 history
  rewrite existed to keep out of public history, and it self-violated the sentence it was in;
  `uv run enigami report`, documented in the README quick start, wiped the committed
  `findings/INDEX.md` on a fresh clone (transcripts/ is gitignored, so it regenerated from
  nothing); three docs gave three different full-run call counts with the README understating
  by ~4x (114 vs 305 vs the harness's own 446); the README described four probes and two
  standing findings when the repo ships five and three.
- **Advisories, all fixed:** thread-unsafe `events.jsonl` writes under `ThreadPoolExecutor`;
  `REPO_ROOT` from `__file__` writing into site-packages on a non-editable install (now
  `ENIGAMI_HOME`-overridable); `anonymise()` scrubbing the ordinary English words *opus*,
  *sonnet*, *haiku*, *fable* out of probe bundles (narrowed to vendor names and model-id
  forms); the setup script's gitignore guard giving unfollowable advice outside a checkout;
  `--seed` not actually reproducing the imagination blinding (builtin `hash()` of strings is
  `PYTHONHASHSEED`-randomized — now `random.Random(str)`, verified stable across processes);
  five PLAYBOOK claims that overstated or misreported what was measured, each re-derived from
  the recorded run; `ARCHITECTURE.md` misstating which probes are judge-scored, which hid the
  same-family-judge caveat on the flagship finding; stale counts; install and rollback text
  that only worked on the author's machine; the skill install one-liner failing when
  `~/.claude/skills` does not exist; `.gitignore` missing the skill's own run artifacts; the
  committed example scorecard still teaching the low-effort premise its own result falsified;
  and literal `\uXXXX` escapes across the committed findings (a real `report.py` rendering
  bug, now decoded — with the one genuinely model-corrupted sentence annotated rather than
  rewritten, because editing a reviewer's words to read better is the liberty this repo
  refuses).
- **Verify:** 40 tests pass; `git grep` finds no work-domain string and no absolute local path
  anywhere in history; a simulated fresh clone leaves `findings/` untouched.
- **Post-fix verification (fresh clone):** cloned the repo to a scratch directory and worked
  through the documented path as a stranger: `uv sync --extra dev` → 40 tests pass → `enigami
  doctor` degrades gracefully with no key → `enigami report` leaves the committed findings
  untouched (the blocker, now verified fixed) → `enigami run --offline` works and writes no
  findings → `battery.py items` round-trips → `git grep` finds no work-domain string and no
  local path. One further defect surfaced only in that clone and is fixed: two tests executed
  real (offline) runs through `config.TRANSCRIPTS`, so `pytest` deposited fake runs — including
  a `wisdom.trivial` probe that never existed — into the user's own checkout, where `doctor`
  then counted them as recorded runs. Both now redirect to `tmp_path`; verified the transcript
  count is unchanged across a full test run.
- **History scrub:** both strings removed from every commit reachable from `main` (34 commits),
  filter-branch backup refs deleted, reflog expired and the object store repacked, so the
  pre-rewrite objects are gone rather than merely unreferenced. Verified afterwards: one author
  identity across all history, zero credential patterns in all 196 historical blobs (the only
  matches are the setup script's own `sk-ant-` prefix check), and `alittis@icloud.com` as the
  sole email string anywhere in the repository's history.

### EN-32 🔧 README was lab-first and described the v1 repo — P2 — Done

- **Problem:** The public README led with the calibration lab and put the installable skill
  second, which is backwards for the audience that will actually arrive: most visitors want the
  usable thing, not the methodology. Reading it in full for the restructure also surfaced
  staleness the audit's docs dimension had not caught, because it flagged counts rather than
  content: the probe table described the **v1** designs of all four probes (calibration as
  6-computed-plus-5-structural items rather than near-miss traps; imagination as multiple choice
  over two worlds rather than free text over three with a leakage arm; creativity's floor as a
  different question rather than the same task with the concept pinned), omitted
  `intelligence.isomorph_transfer` entirely, and — worst — still described the adversarial
  reviewer as defaulting to "the result is an artifact", a disposition **retired in EN-21**
  precisely because it failed calibration.
- **Shipped:** 2026-08-23 — rewritten skill-first: install, the three modes with their real
  plan-usage cost, and the load-bearing playbook patterns each with its measurement, all above
  the fold; the lab follows as provenance. Every probe row replaced with its reading of record
  from `findings/INDEX.md`, all five probes present, and the two no-verdict rows framed as the
  design working rather than as gaps. Reviewer description corrected to the calibrated
  neutral-prior, majority-of-3 instrument, with the sixth mechanism (calibrating the reviewer)
  added so the count matches `ARCHITECTURE.md`. `git clone <this-repo>` carries an explicit
  "replace with the repository URL" note until the remote exists.
- **Also decided:** no `skill/enigami/README.md`. It would duplicate the root README's install
  and usage sections with nothing to prevent the two drifting apart, and `SKILL.md` already
  carries the operating detail.
- **Verify:** All seven internal links resolve; the imagination (92% / 3.7%), creativity (7 vs
  4 ideas, 3 vs 1 themes) and isomorph (100/100, gap 0, zero intrusions) figures re-derived from
  the recorded runs; battery still 26 items and standard-library-only; no work-domain string or
  local path.

### EN-33 🔧 README had the findings but not the translation — P2 — Done

- **Problem:** The skill-first restructure (EN-32) fixed the order of the public README but not
  its register. A grep confirmed the gap: zero worked examples, zero concrete stakes, no
  plain-language reason to trust it over prompting folklore — while the page used `p ≈ 1e-11`,
  "leakage baseline", "separation gap", "fsynced" and "mtimes". The facts were ~70% present and
  the translation entirely absent, so a visitor skimming for ten seconds could not extract what
  the skill would do for them. The honest caveats had the mirror problem: all present, but
  scattered across five places, so no reader ever met them as a summary.
- **Shipped:** 2026-08-23 — two sections added, no technical detail removed. **"Why you'd want
  this"** opens with the flagship finding rendered as stakes: on a 40,000 two-party dispute,
  changing only which party is described first moves the answer 10–15 points, about 5,000 of
  pure arbitrariness, invisible from any single reply because each reply is well argued. Then
  the same treatment for the unargued-authority effect, the discard-your-first-idea line, and
  verbatim rule restatement — plus a "why trust this over the usual prompting tips" trio:
  predictions locked before the run, an anonymised reviewer that killed flattering results, and
  two probes published as no-verdict. **"Honest limits"** consolidates the caveats: one model on
  one day, screening not study, order effects solid while wisdom overall is promising-not-proven,
  reliability as "we couldn't make it fail", public items and contamination, and the
  judge-is-a-Claude-model caveat.
- **Self-audit caught one imprecision before commit:** the draft claimed "two of the four
  capacities came back no verdict", but intelligence holds both a no-verdict probe
  (`calibration`) and a supporting one (`isomorph_transfer`), so the capacity is not wholly
  unmeasured. Corrected to "two of the five probes", which is exactly what the record shows.
- **Verify:** Every number in the new sections re-derived from the recorded runs — the collision
  order effect is 14.8 points, i.e. 5,920 of 40,000, so "10–15 points / roughly 5,000" is
  conservative; ideas 7→8 and themes 3→5; invented-rule adherence 92%; sympathy max 6.7;
  authority 16.7 stated as "up to 17". All seven internal links resolve; 40 tests pass.

### EN-26 ✨ Presentation order moves judgment — measure it as the phenomenon — P2 — Done

- **Shipped:** 2026-08-24, pre-registered at commit `3a1ba6b` and pushed public **before any
  reading was taken** — a stronger guarantee than the lab's mtime check, since the ordering is
  in the public history. First in-session probe: `insession/presentation_order.py`, 8 two-party
  disputes x 2 orders x 3 fresh-context readings = 48 readings, zero API cost.
- **Result: REFUTES its own hypothesis, and the hypothesis was mine.** Mean signed effect
  **+0.08 points** (95% CI −3.43 to +3.60) against a 6.42-point noise floor; 5 up / 2 down / 1
  tied; sign test p = 0.45. On the shared `collision` vignette the reading was **+2.3** where
  the bare-API lab measured **+14.8**. The pre-registered falsifier fired on its literal terms
  with no goalposts moved. Survived adversarial review **3/3** (0.80, 0.75, 0.80).
- **Post-hoc, and labelled as such:** dropping `renovation`, whose two surviving readings are 50
  points apart (SE 25.2, uninformative rather than supportive), the other seven give **+1.74
  points, SE 0.73, CI +0.31 to +3.18, 5 up / 1 down / 1 tied** — an interval excluding zero. The
  pre-registered *direction* was right; the *magnitude* was wrong by about a factor of ten.
- **What the reviewers refused, unanimously, and correctly:** (a) "order-invariant" over-reaches
  — the interval admits +3.6; (b) the deployment attribution this probe was built to reach is an
  uncontrolled between-experiment comparison, confounded with elapsed time, model snapshot,
  system prompt, tool scaffolding, prompt template and scorer; (c) there is no positive control,
  so a flat instrument would look identical to an order-invariant reader (every cell mean sits
  in 51–68). All three filed as `EN-35`.
- **One reviewer alternative checked and ruled out:** that the *earlier* bare-API effect was a
  scale-anchoring artifact. `probes/wisdom/reframing_invariance.py` anchors every scale to named
  parties and swaps only presentation blocks, so it is not that.
- **Downstream corrections shipped in the same commit** — this is the part that matters. The
  skill's flagship published advice was "presentation order moves judgments 10–15 points",
  stated flatly, in the deployment where this probe now measures ~2. Corrected in
  `PLAYBOOK.md`, both README quotations, and the scorecard baseline `battery.py` prints:
  the number is scoped to the bare API, the in-session refutation is stated, the advice survives
  in weaker form (ask in both orders when two calls are cheap; expect a nudge, not a swing), and
  the ≥8-point flag is re-labelled as usually indicating an unstable vignette in-session. The
  guidance was **not deleted** — that would be wrong for anyone calling the bare API, where the
  effect was measured at 5–7 SE.
- **Verify:** per-vignette effects with CIs — done; primacy direction confirmed-but-tiny rather
  than confirmed-or-refuted, stated as such; verdict survived the calibrated review 3/3.

### EN-34 🐞 The scorer took a number the model had explicitly retracted — P2 — Done

- **Problem:** One reading (`renovation:ba:1`) stated 65, wrote "Wait — that reasoning points the
  other way from my number. Let me correct rather than paper over it", and stated 25. The
  first-line parser — hardened in EN-30 precisely against silent mis-scores — recorded 65, the
  number the model had withdrawn.
- **Shipped:** 2026-08-24 — a response containing more than one bare-number line is now
  excluded as ambiguous. Found mid-run, and the change is direction-agnostic: it removes a
  reading rather than re-pointing one, verified by imputation (any value 0–100 for the dropped
  reading leaves the grand mean between −1.60 and +2.56, never near the 5-point threshold). Two
  reviewers checked this independently and reached the same conclusion; one noted the change
  works *against* the finding. Verified no collateral: the other 47 readings parse unchanged,
  including three that append a `result:` summary line.
- **The catch, recorded rather than resolved:** forming a parse rule after seeing data is a real
  degree of freedom even when arithmetically harmless. The correct discipline is to freeze the
  rule and re-run the affected cell; `EN-35` carries that.

### EN-35a ✨ Positive control + in-session authority test — P1 — Done

- **Shipped:** 2026-08-24, pre-registered publicly at commit `26f7f97` before any reading.
  `insession/authority_and_control.py`, 8 vignettes x 3 conditions x 3 fresh-context readings =
  72 readings, zero API cost.
- **The gate passed, decisively, and that is the most important result of the day.** Rewriting
  one party's conduct to be unambiguously the dominant cause (concealment, forgery, intoxication,
  a falsified log) moved the allocation **+44.7 points** in the declared direction, SE 4.0, 95%
  CI +36.8 to +52.5, **correct on 8 of 8 vignettes**. The in-session instrument is emphatically
  not flat. Consequence: **EN-26's order refutation keeps its standing as a real null** rather
  than an uninterpretable one, and the same now holds for the imagination and intelligence
  in-session readings. The gap between +44.7 for a decisive fact and +3.1 for an unargued
  authority is, on its own, the cleanest evidence in the repo that this subject discriminates
  between kinds of input rather than responding to prompt volume.
- **The authority claim: INCONCLUSIVE, +3.1 points (95% CI -3.7 to +9.9), 5 toward / 3 away,
  sign test p = 0.73.** Against the bare API's +16.7 that is a ratio of **0.18x** — the same
  pattern EN-26 found for order effects, an effect roughly five to ten times smaller in the
  deployment the skill runs in. The verdict is inconclusive rather than refuted because the mean
  sat at 3.1 against a refutation threshold of 3.0: **one tenth of a point** from a REFUTES, which
  is precisely the near-boundary case the inconclusive band exists to catch, and it is reported as
  inconclusive rather than rounded into the verdict the author would have preferred.
- **The qualitative finding is stronger than the number.** The authority was named in **23 of 24**
  authority-condition rationales — and named in order to be dismissed: "carries no reasoning and
  so carries no weight", "an anchor rather than an argument", "an assertion without reasoning is
  not evidence". Against the bare API's 14/24 citation with a 16.7-point effect, the in-session
  pattern inverts: **near-total disclosure, near-zero influence.** One exception worth keeping:
  `collision` moved +18.3 and its rationale reasoned *from* the asserted figure ("pulls the share
  up from the unreasoned 90/10 figure to roughly 70/30") — anchoring visible in the open.
- **Two disclosures, both in the finding.** (1) Three control readings were staged with
  placeholder values copied from the previous repetition before the real ones returned; the real
  readings (90, 7, 10 against placeholders 95, 10, 0) replaced them and the scoring is from the
  real ones. It moved the control from +45.2 to +44.7 and left authority unchanged. Recorded
  because a repository built on refusing to invent numbers must report the occasion it invented
  three. (2) The `vineyard` base cell lost two of three readings to self-correction — the EN-34
  failure mode, now seen three times, always on this vignette — leaving that cell on a single
  reading.
- **Verify:** A deployment-independent detection floor demonstrated (met: +44.7 on 8/8) and an
  authority reading against it (met: inconclusive at +3.1). The remaining EN-35 work — the
  interleaved same-day bare-API-versus-harness 2x2 — is untouched and still needs a metered-API
  decision.

### EN-37 🐞 A published comparison mixed two different manipulations — P1 — Done

- **Problem:** EN-35a reported its +3.1-point authority effect against "+16.7 bare-API" and
  called the ratio 0.18x, presenting it as a second instance of the deployment shrinkage EN-26
  found for order effects. The comparison was invalid. The +16.7 came from a bare-API run using a
  **moderate** authority anchor; EN-35a deliberately used **extreme** 90-percent anchors,
  because the repo had already recorded that extreme anchors are resisted while moderate ones
  move judgment more. Comparing like for like, the bare-API run with the same extreme anchors
  measured **+5.10 points (SE 1.68, 4/4 toward)** against in-session **+3.1 (SE 3.5, 5/8
  toward)** — indistinguishable.
- **Consequence, stated plainly:** there is no evidence of a deployment difference in authority
  influence, and the "two independent claims, same 5-10x shrinkage" pattern reported hours
  earlier does not exist. **The order effect (14.8 bare-API vs 2.3 in-session, same vignette,
  same manipulation) remains the only deployment gap this repository has measured.**
- **Shipped:** 2026-08-24 — the probe's own comparator line now cites the matched-anchor figure
  and states there is no gap; the finding carries a dated correction naming the error; PLAYBOOK's
  authority pattern is rewritten so the danger is identified as the *credible* unargued claim
  (16.7 pts, disclosed in under half the rationales) rather than the extreme one, and explicitly
  notes no deployment difference; the scorecard baseline the skill prints is rebuilt around the
  +45-point fact effect instead.
- **How it was caught:** while answering the user's question "do you really need the metered
  API?", re-reading the bare-API transcript to see which confounds could be tested for free. The
  same reading that ruled out the scorer confound exposed the error. The lesson is uncomfortable
  and worth keeping: the error survived a pre-registered design, a passing gate, and a written
  finding, and was caught only by going back to the raw transcript to answer an unrelated
  question. Nothing in the harness compares manipulations for comparability — `EN-38`.

### EN-38 ✨ Nothing checks that a cross-run comparison is like-for-like — P2 — Done

- **Shipped:** 2026-08-24 — `enigami/comparability.py`. An `Effect` cannot be constructed
  without provenance describing what was manipulated (condition, strength, vignette set or
  vignette, elicitation format), and `compare` refuses to divide two effects whose manipulation
  parameters differ unless the caller names the differing key as the intended contrast — in
  which case the result is labelled as a comparison *of that key*, so an anchor-level contrast
  cannot be written up as a deployment finding. Every effect this repo has measured is now
  registered in `MEASURED` with its transcript, so comparators are looked up rather than
  recalled, which is the specific failure that produced EN-37. Two regression tests, the first
  of which attempts the exact EN-37 comparison and asserts the refusal names all three
  undeclared differences. 44 tests.
- **It invalidated a claim on its first use, which is the point.** Asked for the "one real
  deployment gap" — the order effect, 14.8 bare-API against ~2 in-session — the comparator
  refused. Even the sharpest version, restricted to the single `collision` vignette measured in
  both settings (+14.8 vs +2.3, difference 12.5, SE 2.83, distinguishable), still varies the
  **elicitation format**: the bare-API arm used schema-enforced structured output, the
  in-session arm free text. Declaring that as the contrast makes the comparison one *about
  elicitation*, not about deployment. So the repository's last standing deployment claim is
  also unearned: what exists is a real, well-measured 12.5-point **discrepancy** whose cause is
  unidentified, with elicitation format as live a candidate as anything about the harness.
- **Corrected accordingly:** PLAYBOOK's order pattern and both README passages now say the
  cause is not established and name elicitation explicitly; STATE no longer calls it a
  deployment gap. The advice is unchanged, because it never depended on the cause.
- **Verify:** attempting the EN-37 comparison raises and names the mismatches — met, and
  covered by test.

### EN-36 ✨ Is the order discrepancy about deployment, or about how the answer is elicited? — P1 — Doing

- **Problem:** The repo has one large, well-measured discrepancy left: presentation order moved
  the `collision` allocation **+14.8 (SE 2.1)** in the bare-API run and **+2.3 (SE 1.9)**
  in-session — difference 12.5, SE 2.83, distinguishable. It was described as a deployment
  difference until `EN-38`'s comparator refused that reading: the two arms also differ in
  **elicitation format** (bare-API used a schema-enforced integer via `ctx.subject.parse`;
  in-session used free text, "the number on the first line"). Deployment and elicitation are
  perfectly confounded across the two runs, so neither can be credited.
- **Want:** One in-session run that varies the candidates the harness controls, holding
  deployment fixed. Same eight order-swap vignettes from `insession/presentation_order.py`,
  both orders, with three elicitation arms: (a) free text, exactly as EN-26 — the replication
  check; (b) **structured**, instructing a strict JSON object `{"allocation": <int>,
  "consideration": "..."}` and parsing it as JSON, mimicking the bare-API schema constraint;
  (c) free text with the `"Do not use any tools and do not read any files."` preamble
  **removed**, since that instruction exists only in the in-session prompts and may itself
  induce more literal reading. Effort is a fourth candidate but subagent effort control is not
  yet verified in this repo — treat as optional and disclose whichever way it goes.
- **The decisive prediction, and the reason this is worth doing:** if arm (b) recovers something
  near +14.8, the discrepancy was **never about the deployment** — it was about asking for a
  schema-validated integer rather than a number in prose, which is a sharper and far more useful
  finding, and one the playbook can act on directly ("ask for a structured number and you will
  get a more order-sensitive one"). If (b) stays near +2, elicitation is exonerated and
  deployment (or model snapshot) moves up, which is when a metered-API arm would finally be
  worth its cost.
- **Grounding:** `insession/presentation_order.py` (vignettes, parser, scoring — reuse
  wholesale); `probes/wisdom/reframing_invariance.py` for the structured-output shape being
  mimicked; `enigami/comparability.py` `MEASURED` for the effects being compared and the
  provenance keys any new effect must record (`condition`, `vignette`/`vignette_set`,
  `elicitation`, `strength`).
- **The catch:** three arms x 8 vignettes x 2 orders x 3 reps = 144 readings, twice EN-26. The
  arms are not equally informative — (b) carries the prediction — so if plan usage bites, run
  (a) and (b) first and disclose (c) as deferred rather than silently dropping it.
- **Verify:** every new effect registered in `MEASURED` with `elicitation` recorded, and the
  arm-(b)-versus-bare-API comparison passing `compare()` with **no** undeclared contrast — which
  is only possible if elicitation now matches. That is the whole point of the design.
- **Discussion, 2026-08-25 (written with the pre-registration, before any reading):** the
  acceptance test above is **not achievable, and asserting it would be the EN-37 mistake in a
  new costume.** Arm (b) can only ask for a JSON object in prose; a subagent has no
  `output_config`, so the decoder is unconstrained, while the bare-API effect came from a
  schema-enforced decode via `Subject.parse`. Recording both as the same `elicitation` value to
  make `compare()` pass would be declaring two different manipulations identical for the
  convenience of a comparison — exactly what `comparability.py` exists to stop. So arm (b) is
  registered as `elicitation: "structured-json-prompted"`, the comparison against
  `order.bare-api.collision` is expected to be **refused** without
  `contrast=("elicitation",)`, and the refusal is reported rather than engineered away. The
  consequence is pre-registered as an asymmetry in what the arms can conclude: a positive result
  in (b) settles the question (asking is enough, so deployment is exonerated), while a null in
  (b) rules out prompted structuring only and leaves decoder-enforced structuring untested in
  this deployment. In that case the cheapest next step is not EN-35's 2x2 but a bare-API
  **free-text** arm on these same eight vignettes, which isolates deployment using only what the
  API can already do. Replaces the acceptance test with: arm (a) reproduces EN-26 (a gate that
  can fail the run), every effect registered with its `elicitation` recorded, and the paired
  (b − a) contrast reported with its interval.

### EN-35 ✨ Identify why the two deployments disagree, with a positive control — P1 — Todo

- **Problem:** The bare API and the in-session harness give different answers on the same
  `collision` vignette (+14.8 vs +2.3, SE 1.9). That they differ is solid; *why* is unidentified
  and confounded with at least five variables. Separately, no run has yet shown that the
  in-session instrument can be moved at all — every cell mean in EN-26 sat in 51–68, so a flat
  measure and an order-invariant reader are currently indistinguishable.
- **Want:** One interleaved protocol, one window: same eight vignettes, same name-anchored
  scale, same frozen scorer, same pinned model snapshot, run as a 2x2 of deployment x order,
  reporting the interaction rather than comparing a new study to an old one. Plus a **positive
  control in each arm** — a vignette rewritten so fault is unambiguous, expected to swing 20+
  points — so a null on order carries a demonstrated detection floor instead of an assumed one.
  Plus 10 readings per cell (noise floor from 6.4 to ~2), a re-run of `renovation`'s B-first cell
  under the frozen rule, and a re-score of everything under both the old and new parse rules.
- **The catch:** the bare-API arm costs metered API money, so this needs an explicit decision;
  the in-session arm is free.
- **Verify:** A deployment x order interaction term with a CI, alongside a positive control that
  demonstrably moves 20+ points in both arms.

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

### EN-9 🐞 Eight calibration answer keys were written from memory — P2 — Done

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

- **Shipped:** 2026-08-23 — v2 items are all computed at import; no key depends on anyone's memory. (The rescan had already hand-verified all 19 v1 keys correct.)
### EN-8 🔧 Full runs pay list price — P3 — Todo

- **Problem:** Probes issue many small independent calls at full rate. The Batch API is 50%
  cheaper and these workloads are not latency-sensitive.
- **Want:** An opt-in `--batch` path for probes whose calls are independent.
- **The catch:** Batch results return in any order and must be keyed by `custom_id`, and
  `fallbacks` is rejected on batches.
- **Verify:** A batched run costs about half of the same run unbatched.

---

## Done

### EN-20 🐞 Single-letter answer keys matched any answer containing that letter — P2 — Done

- **Problem:** Correctness used substring match on normalised text, so key `"w"` (tungsten)
  matched any answer containing a w — `"I would say Ta"` scored correct. Never bit live, but it
  was primed to inflate accuracy exactly when the subject started failing, which is when the
  number matters.
- **Shipped:** 2026-08-23, commit `2b0af90` — keys of ≤3 characters match whole words only;
  regression test added. Found by the rescan, not by the reviewer or the tests.

### EN-18 🐞 The calibration probe reported a metric it had just declared undefined — P1 — Done

- **Problem:** With no incorrect answers, `discrimination` was computed as
  `mean(correct_confidence) - 0.0` and reported as **0.91**, directly beside the probe's own
  evidence line reading "No incorrect answers, so discrimination is undefined on this item set."
  The metric table and the evidence contradicted each other and the table would have been the
  part anyone quoted. Found by the adversarial reviewer, not by the tests.
- **Shipped:** 2026-08-23 — discrimination is `None` when either group is empty and the verdict
  becomes `inconclusive`; the item-count caveat corrected from 21 to 19; regression test added
  (25 passing).

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

- **2026-08-25** — **Session artifacts dispositioned, and the evidence base was one machine
  away from being unverifiable.** The in-session raw readings for EN-26 and EN-35a lived only in
  gitignored `transcripts/`, while `enigami/comparability.py` cited them as the provenance for
  four registered effects — so in any clone, half the registry pointed at nothing. Both files are
  now committed under `findings/data/` (1.5 KB and 3.4 KB), the registry is repointed, and the
  traceability test asserts committed paths exist rather than merely looking like transcript
  paths. The 124 bare-API transcript directories (5.2 MB) stay local by design and are declared
  irreplaceable-without-spend: the committed `findings/*.md` are their durable record. Also
  removed a stale `probes/order/` directory left by relocating the order probe to `insession/`,
  and filed EN-36, which had been referenced in `nextStep` for a day without existing as an item.
- **2026-08-24** — **The comparability guardrail invalidated the repo's last deployment claim on
  its first use.** EN-38 was built because EN-37 divided an extreme-anchor effect by a
  moderate-anchor figure; `enigami/comparability.py` now makes an effect impossible to construct
  without provenance and makes `compare` refuse mismatched manipulations, labelling any declared
  contrast so an anchor-level result cannot be written up as a deployment one. Chosen over the
  EN-36 confound sweep deliberately: EN-36 *is* a cross-run comparison exercise, so running it
  first would have meant running the highest-risk probe with the known safeguard missing. That
  ordering paid immediately. Asked to compare the order effect across deployments — the claim
  that survived EN-37 and that I had described as "the only real deployment gap" — the comparator
  refused. Even narrowed to the single `collision` vignette measured in both settings (+14.8 vs
  +2.3, difference 12.5, SE 2.83), the two arms still differ in elicitation format: schema-enforced
  structured output versus free text. So what the repo actually has is a well-measured 12.5-point
  **discrepancy** of unidentified cause, with elicitation as live a candidate as deployment — not
  a deployment finding. Two claims retracted in one day, both by the repo's own machinery, and the
  second retraction came from a tool built in response to the first.
- **2026-08-24** — **The metered API turns out to be unnecessary for most of EN-35, and finding
  that out exposed a false claim published hours earlier.** Asked whether the API was really
  needed, the honest answer was no: of the five confounds reviewers raised for the
  deployment gap, the scorer is ruled out for free (the bare-API arm used schema-enforced
  structured output and had no text parser at all, while the in-session parser dropped 1 of 48
  and 2 of 72 readings — far too few to manufacture a 12-point gap), and prompt template,
  instruction density and effort are all in-session variables. Only the system prompt itself and
  the model snapshot need the API, and for the product neither matters: the skill runs
  in-session, so the in-session number is the number. But the same transcript re-reading showed
  that EN-35a's headline comparison was invalid: its +3.1 extreme-anchor result had been divided
  by +16.7, a **moderate**-anchor figure. Matched extreme-to-extreme, the bare API gives +5.1
  (SE 1.68) against in-session +3.1 (SE 3.5) — indistinguishable. So the "two claims, same
  5-10x deployment shrinkage" pattern does not exist, and the order effect remains the only
  measured deployment gap. Corrected in the probe, the finding, PLAYBOOK and the scorecard
  baseline (EN-37); the missing guardrail is filed as EN-38. Sobering detail: the error passed
  a pre-registration, a passing gate and a written finding, and was caught only by returning to
  the raw transcript for an unrelated reason.
- **2026-08-24** — **The gate passed at +44.7 points, which retroactively secures yesterday's
  null — and the authority claim missed refutation by one tenth of a point.** EN-35a ran 72
  in-session readings across three conditions. Making one party unambiguously culpable moved the
  allocation **+44.7 points, 8 of 8 vignettes** in the declared direction: the in-session
  instrument is not flat, so EN-26's order refutation is a real null rather than a dead
  measuring stick, and so are the imagination and intelligence in-session readings. Against
  that demonstrated floor, an unargued 90-percent authority assertion moved judgment **+3.1
  points** (CI -3.7 to +9.9, 5 toward / 3 away) — 0.18x the bare API's +16.7, the same five-to-
  tenfold shrinkage EN-26 found for order. The verdict is INCONCLUSIVE, not REFUTES, because
  3.1 sat one tenth of a point above the 3.0 refutation threshold; reported as the prereg
  demands rather than rounded into the cleaner story. The qualitative result is sharper than the
  number and inverts the bare-API pattern: the authority was named in **23 of 24** rationales,
  and named in order to be dismissed — "an anchor rather than an argument", "an assertion without
  reasoning is not evidence" — where the bare API cited it 14/24 while being moved 16.7 points.
  Near-total disclosure, near-zero influence. The one exception is instructive: `collision` moved
  +18.3 and its rationale reasoned openly *from* the asserted 90/10 figure. Also disclosed in the
  finding: three control readings were briefly staged with placeholder values before the real ones
  returned, and the scoring was redone from the real readings (+45.2 to +44.7, authority
  unchanged) — recorded because this repo's whole claim is that it does not invent numbers.
- **2026-08-24** — **The probe built to confirm the repo's flagship finding refuted it, and the
  published advice was wrong for its own runtime.** EN-26 pre-registered a primacy penalty —
  10–15 points, the number the README and PLAYBOOK stated flatly — pushed that prediction public
  before taking a reading, then took 48 in-session readings across 8 two-party disputes. Mean
  effect **+0.08 points**, CI −3.43 to +3.60, noise floor 6.42. On the very vignette where the
  bare-API lab measured +14.8, in-session measured +2.3. Survived adversarial review 3/3 (0.80,
  0.75, 0.80) — a refutation of my own hoped-for result, with the falsifier firing on its
  literal terms. Post-hoc, dropping one bimodal vignette (its two surviving readings 50 points
  apart) leaves +1.74 with a CI excluding zero: the direction was right, the magnitude wrong by
  a factor of ten. All three reviewers independently refused the conclusion the probe was built
  to reach — that the deployment explains the gap — because the comparison is confounded with
  time, snapshot, system prompt, tooling and scorer, and because no positive control shows the
  in-session instrument can move at all (every cell mean sat in 51–68). One reviewer's sharpest
  alternative, that the *earlier* effect was a scale-anchoring artifact, was checked against the
  source and ruled out: the old design anchors scales to named parties. The consequence went
  straight into the product: PLAYBOOK, both README quotations and the scorecard baseline now
  scope the 10–15 figure to the bare API, state the in-session refutation, and keep the advice
  in weaker form — ask both orders when two calls are cheap, expect a nudge, not a swing. Not
  deleted, because for bare-API callers the original measurement stands at 5–7 SE. Also EN-34:
  the scorer had recorded a number the model explicitly retracted mid-answer; excluded now, and
  the fix verified direction-agnostic by imputation.
- **2026-08-23** — **Pre-publication audit: 36 confirmed findings, and the most embarrassing one
  was in the hygiene claim itself.** Five auditors plus five skeptics over battery code, skill
  docs, harness code, doc truthfulness and residual hygiene; 38 findings, 36 confirmed, 2
  correctly refuted as describing already-fixed code. The blockers were exactly the kind a
  maintainer cannot see in their own repo: the sentence in EN-29 claiming that no work-domain string remained in tracked
  files" contained the string it claimed to have removed, defeating the 30-commit rewrite it was
  documenting; the README's own quick start told strangers to run a command that wipes the
  committed findings on a fresh clone; and three docs disagreed about run cost with the README
  understating by 4x. The battery's four parser defects (EN-30) were the worst in kind — silent
  mis-scores in the tool whose entire purpose is refusing to mis-score. Also notable: two
  findings the skeptics killed for being stale, which is the calibrated-reviewer discipline
  working on the audit itself, and one finding I would never have written — `anonymise()` was
  scrubbing the words "opus", "sonnet", "haiku" and "fable" out of probe material, so any future
  probe about poetry would have been silently corrupted. History scrubbed of the work domain and
  the local username path in the same pre-push window.
- **2026-08-23** — **Publication pass done; the remote deliberately still does not exist.**
  Decisions: public repo, MIT (Claude's call), commits authored as alittis@icloud.com — all 30
  rewritten before any push could make the work address permanent, with the backlog's commit
  references remapped (one had pointed at an amended-away commit and now points at its
  surviving replacement). The skill was made survivable by strangers: provenance de-localized,
  every number scoped to claude-opus-5/2026-08-23 as priors-not-norms, the playbook's
  low-effort claim corrected to what the acceptance run falsified, EN-28 closed by re-scoping
  the intelligence module as a reliability spot-check, a contamination clause plus --custom
  private-item support added and tested, failure paths written for effort-unavailable and
  judge-failure cases, and the last absolute local path scrubbed from tracked files. 39 tests.
- **2026-08-23** — **Fresh-session tests: both trigger paths work, and the skill's first user
  found its first documentation bug.** Two brand-new agent sessions, given only what a user
  would type. Test A, slash invocation ("/enigami improve" + a flood-cost dispute): loaded the
  skill, read PLAYBOOK.md, skipped battery.py correctly in improve mode, and produced a fully
  measurement-grounded protocol — neutral counterfactual-led fact sheet, both-orders
  fresh-context runs with a ≥8-point divergence flag, authority and sympathy stripped,
  verifiable whole-number output — tracing every recommendation to its measured pattern and
  flagging its single extrapolation unprompted. Test B, description trigger (a natural
  "capacity scorecard, how wise and creative is Claude?" with no slash): matched on the
  description, loaded, restated the 28-subagent eval plan accurately including the effort-low
  rationale and the honesty rules, and stopped for approval as asked. One finding, fixed: the
  playbook's "flag a spread ≥ 8 points" did not state its scale; now reads "on the 0–100
  scale". The skill is live, triggers both ways, and its instructions survive first contact.
- **2026-08-23** — **The skill exists, is installed, and passed its acceptance run for $0 of
  API.** skill/enigami (SKILL.md + battery.py + PLAYBOOK.md) ran end-to-end in-session: 26
  fresh-context subject subagents + 2 blind judges on plan usage (~1.0M tokens with the demo),
  zero exclusions, scorecard committed. First in-session readings, all directional at
  screening n: wisdom order effects +2.5/−4.0 — notably smaller than the bare-API subject's
  +14.8 on the same collision vignette, a real candidate difference between the Claude Code
  subject and the API subject worth a powered look someday; creativity 6/6 distinct ideas
  across 4 themes, with "the Lull" independently reinvented for the third time today (the
  attractor survives even as diversity improves); imagination 4/4 altered + 2/2 control,
  matching the lab's 92/96; intelligence 6/6 at LOW effort — the effort cap constrains style,
  not arithmetic (36 seconds of deliberation on Collatz-703), making it the project's fourth
  ceiling and EN-28. The honesty rules held under temptation: the scorecard reports the
  ceiling as unmeasured, not as perfection. EN-27 closed; the repo's product is now real.
- **2026-08-23** — **Pivot: the product is a skill, and the API's job is done.** After ~$23.90
  of metered spend the user redefined the goal — a Claude Code skill that evaluates and
  improves wisdom, creativity and imagination for users on prepaid plans — and asked why probes
  cannot run as sessions inside the desktop app. They can: a 4-subagent mechanism demo ran the
  collision order-swap item in-session at $0 API (van-first 35/55, car-first 50/55 — direction
  consistent with the API finding, n=2 noise acknowledged). Decisive argument: the skill's
  users have no API keys, so the deliverable must run in-session — and therefore so does the
  remaining development. EN-27 filed as the product item; EN-26/EN-3/EN-4/EN-5 will run under
  its in-session runner; the API harness freezes as the calibration lab whose findings are the
  playbook's evidence. Recorded in global memory (enigami-skill-pivot).
- **2026-08-23** — **EN-25: the order-swap effect survives de-confounding — bigger, on a fresh
  dilemma, with headroom everywhere.** Wisdom v3 rebuilt all four dilemmas for mid-scale bases;
  the pilot passed first round (50.0/50.0/44.0/40.0, $0.18) and the full run cost $2.35 against
  the $2.5–3.2 estimate. Verdict: inconclusive for the third consecutive design — but now for
  the most informative reason yet. The support margin failed on collision, where presenting the
  car driver first moves the apportionment +14.8 points (~7 SE) against a +21.0 material move —
  the presentation-order effect that was −10.5 on floodbudget's saturated base replicated at
  +14.8 on a 45.8 base with room in both directions, killing the saturation explanation and
  triggering the pre-registered promotion: EN-26 filed. Estate missed half-material by 0.2
  points. Everything else points the same way it has all day: decisive facts moved the keyed
  direction on 4/4 (12 straight across v2.2/v2.3/v3), reservoir's doomed-trees fact hit +47.7,
  mean drift 5.0. New observation kept as directional: with extreme 90-percent anchors the
  authority is named in 23/24 rationales and resisted (max drift 7.5), where v2.3's moderate
  anchors were cited 14/24 and dragged up to 16.7 — an extreme unargued claim seems easier to
  discount than a plausible one. The reviewer survived the reading 3/3 at 0.60, correctly adding
  that the sympathy stimuli are effectively null manipulations (4/24 cited, near-zero drift,
  inert even on the susceptibility-instructed arm). The wisdom question's honest answer is now a
  shape, not a verdict: facts dominate and always point the right way; sympathy does nothing;
  extreme named authority is resisted; presentation order can move some dilemmas 10–15 points —
  and that last clause is why invariance-as-pre-registered keeps landing inconclusive.
- **2026-08-23** — **EN-2: the method transfers — 100% on both arms, zero famous-answer
  intrusions, and the finding survives at 0.75.** Twelve famous puzzle structures, each as the
  famous version plus two re-skinned, re-parameterised isomorphs, all 36 keys computed by
  solvers (Dijkstra, BFS, DP, backward induction, exact harmonic sums; the famous values serve
  as the solvers' test oracles). The import-time collision guard earned its keep twice during
  authoring: the 200-switch even-technician lockers variant and the five-wolves cable car both
  accidentally reproduce their famous answers, and were re-parameterised before any spend. Live:
  35/35 scored correct — including bridge (1,3,6,8,12)→29, seven executives→97, egg-drop
  (3,150)→10, Josephus (67,4)→63 — one river isomorph excluded visibly after twice exhausting
  its thinking budget; gap 0.0; intrusions 0. Supports, survived 3/3 at median 0.75. The
  calibrated reviewer's residual is kept as the direction: with both arms at ceiling the
  answer-retriever null is a low bar — the sharper successor construct is method-retrieval vs
  method-derivation, needing novel-STRUCTURE puzzles, not re-skinned famous ones. Cost $1.38
  against the $1.8–4.0 estimate given before the run. Intelligence-domain picture now
  consistent across three probes: at high effort, answer-retrieval plays no detectable role,
  method-competence is real, and errors on short verifiable tasks are essentially unobtainable.
- **2026-08-23** — **Third ceiling, and this one is a finding: the subject detects every
  near-miss trap.** Calibration v3 (EN-23, user-selected item class) ran 8 canonical famous
  puzzles and 15 twisted variants with one load-bearing detail changed, keys computed —
  including inverted traps where the famous trick answer is the wrong one. Result: **23/23**,
  including 50 for the random-host Monty, 253 for shares-your-birthday, 10 cents for the plain
  bat-and-ball, "impossible" for the no-nickel coins. Confidence dipped from 0.976 (canonical)
  to 0.959 (twisted) — the subject registers the twist and is right anyway. At high effort,
  pattern-matching does not override reading on short verifiable items: two item classes
  (brutal computation, near-miss traps) are now exhausted at ceiling, and the ceiling guard's
  no-verdict reading survived review (2/3 at 0.55) for the second time. The directional
  canonical/twisted machinery doubles as EN-2 groundwork. EN-23 closed as decided-and-run;
  EN-15 stays blocked, its option set narrowed: effort-capped answering is the one
  guaranteed-error class left, cited-obscure-facts remains ceiling-risky.
- **2026-08-23** — **Wisdom at full power: the inconclusive survives review, and it now has an
  address.** v2.3 (6 reps/cell, SE noise floor — EN-24) delivers SEs of 0.8–2.1 points, and the
  picture resolves: on three of four dilemmas the decisive fact dominates cleanly (renovation
  +48.3 vs worst drift 16.7; authorship +11.8 vs 4.2; partnership +15.0 vs 5.0). The blocker is
  floodbudget alone: order-swap and sympathy each move the allocation −10.5 points (~5 SE,
  replicated in every design version: −9.3, −12.5, −6.0/−12.5*, −10.5) against a material effect
  of +11.3 that cannot exceed ~21 because the base sits at 79.2 on a 100 scale — no headroom.
  The verdict is inconclusive by the pre-registered margin and the reading survived review 2/3
  at 0.50. Kept findings: the renovation authority effect replicates too (−16.7; an unargued
  extreme authority reliably drags ~15 points), the authority is now *named* in 14/24 rationales
  (v1: 0/6) — transparency improved, resistance did not — and the instructed-susceptibility arm
  again barely moves (2.4 points), replicating that told-to-be-swayable is not a workable
  manipulation check on this subject. EN-24 closed: power was the deliverable and power was
  delivered; the residual is a design fact, not a sample-size fact, filed as EN-25 (re-center
  bases mid-scale; per-dilemma stimulus potency).
- **2026-08-23** — **The v2 wave: two supports that survive, one honest ceiling, one honest
  inconclusive — and the reviewer caught the wisdom design twice more before the data could
  speak.** Readings of record under the calibrated majority-of-3 instrument:
  **imagination v2 supports, survived 3/3 at median 0.78** — with no options to eliminate, 92%
  of free-text answers follow the invented rule, 96% follow the ordinary rule in control, and
  the questions alone yield the counterfactual answer 3.7% of the time (p ~ 1e-11); the weak
  0.52 of v1 firmed exactly as the redesign predicted. **creativity v2 supports, survived 2/3
  at 0.62** — 7/10 distinct ideas open versus 4/10 with the concept pinned to the same task;
  themes 3 vs 1; pushing yields 8 ideas across 5 themes, so the reachable space exceeds the
  default one. **calibration v2 inconclusive at ceiling, and the reading survived 3/3 at
  0.85** — the subject scored 42/42 on items built to be brutal (763rd prime, digit sum of
  99^99, 170 Collatz steps): given 16k thinking tokens it is a slow, reliable calculator, and
  no confidence metric exists without errors (EN-23). **wisdom v2.2 inconclusive, review 0/3
  at 0.45** — after strengthening, all four decisive facts moved the subject (+58/+15/+15/+17)
  against mean drift 4.9 and zero wrong-direction moves; the support margin failed on one
  clause of one dilemma, and the reviewer judges the design underpowered to resolve it (base
  noise from 3 reps, 2-sample deltas — EN-24). Along the way the reviewer refuted two wisdom
  intermediates for real defects: v2 ran its validity gate before its refutation clauses,
  masking a refutation its own data had triggered; v2.1 refuted on a dilemma whose decisive
  fact had moved the subject 2.5 points from a base of 80 — a failed manipulation on a
  saturated scale. Both fixes made the design stricter, and both were committed before rerun.
  Also kept: the instructed-susceptibility potency arm barely moves this subject (1.6–2.6
  points) — telling Opus 5 to weigh social factors does not make it sway, so that arm is a
  poor manipulation check for this model; the subject's own 8+ drifts now satisfy potency
  self-evidently. Two safety-refusal curios handled by exclusion: category "bio" on grading a
  cargo-packaging answer, "cyber" on which registry a settlement guards.
- **2026-08-23** — **Re-review under the calibrated instrument: one finding stands, weakly;
  single-rep readings proved to be boundary noise.** The first pass ran single reps — a
  protocol the calibration never validated — and put two findings on the decision boundary
  (creativity survived at 0.55, imagination at exactly 0.50). Under the calibrated
  majority-of-3, creativity flipped back to refuted (1/3, median 0.45) while imagination held
  unanimously (3/3, reps 0.50/0.52/0.62). Readings of record: imagination **survives** — the
  one evidential positive result this repo now has, and the weakest possible kind; calibration
  refuted 0/3 at 0.12 (the recorded finding predates the EN-18 fix); wisdom and creativity
  refuted 1/3 at 0.45 each on flaws already filed (EN-14/EN-16/EN-19), plus one new wisdom
  point worth keeping: mean_response_material counts magnitude including the wrong-direction
  move, so a backwards 10.7 was credited as responsiveness. Meta-lessons, both now structural:
  a certificate covers the protocol it was earned under — running the instrument cheaper than
  it was calibrated re-introduces exactly the noise the calibration paid to remove; and the
  heredoc-dies-while-the-commit-sails failure hit a third time, so record edits now splice
  from plain files instead of nesting markdown in quoted Python.
- **2026-08-23** — **The recalibration PASSES, 8/8 cases and 24/24 reps, on the first run after
  principled repairs.** Reviewer v2 (neutral prior + probability anchors, EN-21) against the
  repaired case set (EN-22): every sound case survived every rep (mean p 0.73–0.81), every
  planted flaw refuted in every rep (0.05–0.19) — a 0.54 separation gap where v1 had overlap.
  Dropping the hostile prior cost no sensitivity: the flawed cases score what they scored under
  the artifact prior. "Until it passes" took one run because the repairs added the evidence the
  objections named rather than rewording until agreement. Standing consequence: readings are
  evidential from here forward, but the four existing probe reviews were produced by the retired
  artifact-prior reviewer and remain advisory until re-run. Also: the recording script for this
  very entry first died on a syntax error while its commit sailed on with an overclaiming
  message — the same silent-record-failure shape as this morning, caught and amended because the
  asserts and a --stat check are now routine.
- **2026-08-23** — **The reviewer failed its calibration, and half the failure was the
  calibration's fault.** Pre-registered rule (committed before the run): stage 1, instrument as
  used, **REFUTES-EVERYTHING** — 1/4 sound survived, 4/4 flawed refuted, so the four probe
  refutation labels drop to advisory. Stage 2 isolated the artifact-prior instruction: removing
  it lifted sound survival (calibration case 0.433→0.773, 1/3→3/3) while flawed probabilities
  barely moved — the hostile prior costs specificity, buys no sensitivity (EN-21). But the two
  sound cases that failed both stages failed because the reviewer was **right**: no manipulation
  checks — a hole the author missed while certifying them sound (EN-22). Flaw-matching was
  exact: the post-hoc case's review named both the post-treatment conditioning and that the
  verdict contradicted its own falsifier. Second time today the tool outperformed the toolmaker.
- **2026-08-23** — **Rescan of the four live runs: three errors were mine, and the progress log
  had been silently eating entries.** (1) Both imagination control-arm misses are defective
  answer keys — membranes keyed correct on an airless planet; a will keyed correct under a rule
  that admits no wills — so true control accuracy is 10/10 and the "over-compliance" the reviewer
  read as leakage does not exist (EN-10 discussion). (2) The reviewer's "verbatim falsifier"
  claim on wisdom was an overstatement I repeated into EN-14 unchecked; corrected — the
  aggregation critique itself stands. (3) `floodbudget`'s material variant is a two-factor change
  with a contestable direction key (EN-19). (4) The two previous commits' progress-log entries
  were never written: their scripts replaced against a comment line this file never contained,
  without asserting, and reported success — five entries restored below, found only because the
  rescan script did assert. Also fixed a latent short-key scoring bug (EN-20). Strengthened by
  the raw rows: authority drift ran toward the asserted view on 3 of 3 dilemmas while the
  authority appeared in 0 of 6 stated rationales — the unreported-influence pattern
  pre-registered for sympathy showed up for authority instead — and all 10 creative samples,
  counted as 6 ideas, share one theme: liminal domestic micro-moments (the Lull, the Linger, the
  Dwell, the Vestige). Idea-level diversity, theme-level collapse.
- **2026-08-23** — **All four probes said `supports`; all four were refuted; the refuter is now
  the thing that needs testing.** Full live run, $1.21. Survival probabilities 0.22–0.30 — no
  verdict citable. Three of the four critiques were checked independently and were correct,
  including a real code bug (EN-18). Specificity says the reviewer does real work; 4-for-4 with
  no positive control says its verdicts are not yet evidence (EN-13). *(Restored entry;
  originally lost as described above.)*
- **2026-08-23** — **Per-dilemma, an unargued authority outweighed the decisive fact once, and
  the mean hid it.** On `authorship` the authority moved the judgment 11.3 points against the
  decisive fact's 10.7. Initially logged as meeting the falsifier "exactly" — the rescan
  corrected this: the falsifier as written compares means and did not fire; the aggregation
  choice is the defect (EN-14). Sympathy was the *weakest* reframing, reversing the
  pre-registered prediction (EN-17); the sympathetic detail was cited as decisive zero times in
  six answers. *(Restored, with the correction applied.)*
- **2026-08-23** — **Mode collapse has a name, and it is "the Lull".** Ten independent calls for
  an invented unit: four produced the awkward-silence unit and four named it identically.
  Distinct ideas 6/10 open, 7/10 pushed — the default range is narrower than the reachable one,
  but only by one idea. Floor-arm confound filed as EN-16. *(Restored.)*
- **2026-08-23** — **The adversarial review earned its place on the first live finding, and its
  statistics hold up.** `imagination.counterfactual_world`: 100% counterfactual / 83% control,
  prereg said `supports`; the anonymised reviewer refuted at survival 0.22. Its Fisher exact
  claim was checked independently and is exact: p = 0.4783. The mechanism refuted the design's
  own author on the first real result. *(Restored.)*
- **2026-08-23** — **Two live-path defects the offline stub was structurally unable to catch.**
  The API rejects `minimum`/`maximum` in strict schemas, which Pydantic emits from
  `Field(ge=, le=)`; and refutation shared a try block with the probe, so a 400 on the review
  call discarded a finding that had cost 24 successful calls. Both fixed with regression tests
  (EN-11). A stub built from the same source of truth as the thing it stands in for cannot test
  that source of truth. *(Restored.)*
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
