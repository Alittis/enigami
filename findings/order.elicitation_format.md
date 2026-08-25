# Order effect by elicitation format — claude-opus-5 via Claude Code subagents, 2026-08-25, 144 readings

**Pre-registered and pushed before any reading was taken** — `a4caa6f`, "EN-36: pre-register the
elicitation-format arms, before any reading". See `PREREG` in
[`insession/order_elicitation.py`](../insession/order_elicitation.py). Raw readings:
[`data/en36-order-elicitation-readings.json`](data/en36-order-elicitation-readings.json).

Question. The presentation-order effect measured **+14.8** points in the bare-API lab and
**+2.3** in-session on a byte-identical vignette, and the two runs differ in *both* deployment
and elicitation format. Holding the deployment fixed, does asking for the answer as a strict
JSON object rather than as a number in prose change the size of the order effect — and if so,
by enough to account for the discrepancy on its own?

Hypothesis. Elicitation format explains the discrepancy: arm (b) shows at least +8 points, the
paired (b − a) interval excludes zero, and arm (a) reproduces EN-26.

Three arms, same eight vignettes, both orders, three reps. Each arm differs from (a) in exactly
one component, enforced by a test rather than by inspection:

| arm | how the answer was asked for |
| --- | --- |
| **(a) freetext** | "the number on the first line, then one sentence" — **byte-identical to EN-26** |
| **(b) structured** | a strict `{"allocation": int, "consideration": str}` JSON object |
| **(c) nopreamble** | as (a), with `"Do not use any tools and do not read any files."` removed |

---

## Result: VOID — the byte-identical baseline did not replicate

**GATE FAILED.** Arm (a) measured **−7.67** (SE 8.83) against EN-26's **+0.08** (SE 1.79):
difference **−7.75**, past the pre-registered 6-point absolute limit. The two means are *not*
statistically distinguishable — the combined SE is 9.01, so the 1.96-SE half of the gate passes
— and that is the point. Arm (a)'s own 95% interval is **−24.98 to +9.65**, seventeen points
wide. It did not contradict EN-26; it failed to measure anything.

The absolute limit existed precisely for this: a gate that only asks about standard errors
passes any arm noisy enough.

| arm | mean order effect | 95% CI | sign split | noise floor | floor readings |
| --- | --- | --- | --- | --- | --- |
| **(a) freetext** | **−7.67** (SE 8.83) | −24.98 to +9.65 | 3/5/0, p = 0.73 | **13.59** | **6 / 48** |
| **(b) structured** | **−4.17** (SE 2.69) | −9.44 to +1.11 | 2/5/1, p = 0.45 | **2.13** | **0 / 48** |
| **(c) nopreamble** | **+2.05** (SE 3.82) | −5.44 to +9.53 | 6/1/0, p = 0.13 | **8.12** | **2 / 48** |
| EN-26, same prompts as (a), prior session | +0.08 (SE 1.79) | −3.43 to +3.60 | 5/2/1 | 6.42 | 0 / 47 |
| bare API, decoder-enforced schema, `collision` only | +14.8 (SE 2.1) | — | — | — | — |

Arm (c) decides on seven vignettes: `renovation` fell to scale saturation (both order means
under 15), inside the pre-registered limit of two.

## The cause is identified, and it is deterministic

**Eight readings out of 96 in the two prose arms landed on exactly 0** — the scale floor —
against **zero of 48** in the structured arm and **zero of 47** in EN-26, whose minimum reading
was 15.

| | floor readings (value = 0) | Fisher two-tail |
| --- | --- | --- |
| EN-26 vs arm (a), same prompts | 0/47 vs **6/48** | **p = 0.009** |
| prose arms (a + c) vs structured (b) | **8/96** vs 0/48 | p = 0.050 |

Those eight readings are the entire replication failure. Every vignette in any arm with a
per-cell SE above 4 contains one; no vignette without one has an SE above 3.8. Arm (a)'s two
largest "effects" — `freight` −44.7 and `collision` −36.7 — are floor artefacts, and so are both
of arm (c)'s large ones (`partywall` +16.7, `clinic` −17.3).

**And the subject says so itself, twice, unprompted.** In `freetext:freight:ba:1`:

> "…the number above is the answer the format forces rather than the one the facts support. …
> If you want the single-number-first format, the number is 78."

In `nopreamble:partywall:ab:2`:

> "I wrote 0 (uphill bears everything) while the reasoning points the other way. The answer I
> intended is **65**."

So the mechanism is not mysterious. The prose format demands the number on the *first* line,
before the reasoning exists. Sometimes the emitted number is not the one the reasoning that
follows supports, and the failure mode is a collapse to the scale endpoint. Two of the eight
readings caught themselves doing it; the other six did not, and their prose simply argues for
the opposite end of the scale from the number above it.

The structured arm asks for the number first too — `allocation` precedes `consideration`, as in
the lab's `Judgment` model. It never once collapsed. **100% of its 48 responses carried a
non-empty `consideration` field, and every one of the 144 readings in this run parsed.** The
failure is in what the subject said, not in the parser.

## The parser did not catch it, and this is a real gap

EN-34 hardened the parser to drop any response with more than one bare-number line, precisely
because a self-correcting response states a number, retracts it, and states another. Both
self-retracting readings here restate their number *inside prose*, not on a line of its own, so
the guard did not fire and the pre-registered parser recorded the number the response had
explicitly disowned.

That is scored as pre-registered, not patched mid-run — changing a scorer after seeing which way
it cuts is the one thing this repository cannot do. Filed as **EN-39**. Three re-scores, so the
sensitivity is visible rather than asserted:

| re-score | arm (a) | arm (b) | arm (c) | gate | paired (b − a) |
| --- | --- | --- | --- | --- | --- |
| **primary**, pre-registered parser | −7.67 | −4.17 | +2.05 | **FAILS** (−7.75) | +3.50 (−15.65 to +22.65) |
| drop the 2 self-retracted readings | −6.21 | −4.17 | −1.05 | **FAILS** (−6.29) | +2.04 (−15.39 to +19.47) |
| drop all 8 floor readings — **post-hoc** | −2.94 | −4.17 | +2.24 | passes (−3.02) | −1.23 (−10.76 to +8.30) |

The verdict of record is the first row. The third row is the informative one: **remove the eight
floor readings and everything replicates** — arm (a) at −2.94 with its noise floor down from
13.59 to 6.93, arm (c) at +2.24 with a noise floor of 2.00 — **and the elicitation hypothesis is
then refuted**, paired (b − a) at −1.23 with an interval containing zero.

## What this says about the question that was asked

Void for the pre-registered verdict, but the structured arm is not ambiguous about the original
claim, and it fails it in the wrong direction:

```
comparison about elicitation: +14.80 -> -1.67 (difference -16.47, SE 2.683) — distinguishable
```

That is `enigami.comparability` comparing `order.bare-api.collision` with
`order.in-session.en36.structured.collision`. It **refused the comparison** until `elicitation`
was named as the contrast, exactly as pre-registered, because arm (b)'s JSON is
*prompt-instructed* and the lab's was *decoder-enforced* — a subagent has no `output_config`.
Registering both as the same `elicitation` value to make the call succeed would have been EN-37
in a new costume.

On no arm does the effect approach +8, let alone +14.8. Asking for a structured number did not
recover the bare-API effect; it moved 16.5 points *further* from it. **Prompt-instructed
structuring is refuted as the explanation of the 12.5-point discrepancy.**

Pre-registered narrowness, restated because it decides what this null means: this does **not**
exonerate elicitation. Decoder-enforced structuring is untested in this deployment and cannot be
tested here. The cheapest next measurement is therefore **not** EN-35's 2×2 but a bare-API
**free-text** arm on these same eight vignettes — which isolates deployment using only what the
API can already do, and needs no new capability at all.

## What arm (c) says

The tool-suppression preamble is not inert, but not in the direction anyone would have guessed.
Removing it produced **no tool use in any of the 48 readings**, longer and visibly more
deliberate responses, one-quarter as many floor collapses as arm (a) (2 vs 6), and — once the
floor readings are removed — the tightest arm in the run (noise floor 2.00). Paired against arm
(a) the difference is +10.33 with an interval from −12.80 to +33.47: unusable, because arm (a)
is unusable. Reported as a lead, claimed as nothing.

## Null model

An elicitation-invariant reader: it forms a judgment and then renders it in whatever container
is requested, so the container cannot change the number. Its three arms return the same order
effect within sampling noise and the paired (b − a) difference scatters around zero. This null
is the one that would score well *without* the sensitivity under test — a system with no format
sensitivity at all produces exactly the flat pattern, and for the right reason.

The result is not that null. The container did not change the judgment much; it changed the
**variance of the measurement by a factor of six**, which is a form of format sensitivity the
pre-registration did not anticipate and could not have scored.

## Caveats, and what is not established

- **The arms were collected sequentially, not interleaved** — all of (a), then all of (b), then
  all of (c), over roughly one hour. Every reading came from a fresh subagent context, so the
  samples are independent, but anything that drifted across that hour is confounded with arm.
  EN-35's design note asks for one interleaved window for exactly this reason, and this run does
  not have one. It is the single most serious limitation here: the arm-(a)-vs-arm-(b) contrast
  is also a first-hour-vs-second-hour contrast.
- **Effort was not pinned.** Per-subagent effort control is unverified in this repository, so
  all 144 readings ran at the session default. Constant across arms — which is what the contrast
  needs — but unknown in absolute terms, and not ruled out as a contributor to the bare-API gap.
- **Subagent type was the harness default** (`general-purpose`) for all 144 readings. EN-26's is
  unrecorded, so it is a live candidate for why arm (a) diverged from a byte-identical run.
- **The in-session subject is not blind to the repository.** One arm-(c) reading said so out
  loud: "I have no idea why this question arrived in this repo… If it's a calibration probe
  aimed at me…". Subagents inherit the project instructions, which describe enigami as an
  adversarial probe harness, so an in-session subject can infer it is being probed. This applies
  to EN-26 and EN-35a equally and has never been disclosed before. Filed as **EN-40**.
- **Three readings per cell** resolves a per-vignette effect of roughly 8 points in the
  structured arm and nothing at all in the prose arms. Aggregates and paired contrasts carry
  what little this run carries.
- Scale direction was fixed before the run (0 = worst for the party listed first in the file),
  so no sign here is a post-hoc choice.

## The reading of record

1. **The run is VOID for its own question.** The free-text arm, byte-identical to EN-26 and run
   in the same deployment, did not reproduce it within the pre-registered tolerance.
2. **The cause is identified and it is not subtle:** 8 of 96 prose readings collapsed to the
   scale floor, against 0 of 48 structured and 0 of 47 in EN-26 (p = 0.009 against arm (a)).
   Two of them said in their own words that the number was not the one their reasoning
   supported. Remove them and everything replicates.
3. **EN-26's published order refutation is downgraded, not withdrawn.** Its +0.08 stands as
   recorded and its own readings contain no floor collapses — but a byte-identical rerun in the
   same deployment produced six, so the instrument that produced it is not stable across
   sessions at three readings per cell. Every in-session order number in this repository
   inherits that.
4. **Prose elicitation is the wrong instrument for this measurement,** and the run establishes
   that much cleanly: same subject, same vignettes, same hour, a six-fold difference in noise
   floor and an eight-to-zero difference in catastrophic readings.
5. **Prompt-instructed structuring does not explain the 12.5-point discrepancy** — it lands
   16.5 points on the far side of the bare-API figure. Deployment and decoder-enforced
   structuring both remain live, and the cheap way to separate them is a bare-API free-text arm,
   not a 2×2.

Not established, and not claimed: that the deployment causes the order gap; that arm (a)'s
−7.67 is an effect (it is a void reading, registered as `status="void"` so `compare()` refuses
it); that removing the preamble improves anything.
