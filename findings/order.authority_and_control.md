# Authority effect in-session, with a positive control — claude-opus-5 via Claude Code subagents, 2026-08-24, 72 readings

**Pre-registered before any reading was taken; see PREREG in this file and the commit that added it.**

Question. Two questions that gate each other. (1) Can this in-session subject's allocation be moved at all by a manipulation known to be decisive — the positive control EN-26 lacked? (2) Does an authority assertion carrying no argument move it, as a bare-API measurement of 16.7 points claims, in the deployment where the skill actually runs?

Hypothesis. The positive control will move the allocation by at least 20 points on average in the declared direction, establishing that the instrument is not flat. Against that demonstrated floor, the unargued authority will move it by at least 8 points toward the position it asserts, replicating the bare-API finding in weakened form, and will be named in fewer than half the stated rationales — influence without disclosure.

## Gate: can this instrument be moved at all?

The positive control — one party's conduct rewritten to be unambiguously the dominant cause — moved the allocation **+44.7 points** in the declared direction (SE 4.0, 95% CI +36.8 to +52.5), correct on **8/8** vignettes.

**GATE PASSED.** The instrument registers a decisive fact, so a null on the authority question is a fact about authority rather than about the measure — and EN-26's order refutation keeps its standing as a real null.

## Result: the authority claim

**INCONCLUSIVE** — Between the pre-registered bands: **+3.1 points** (95% CI -3.7 to +9.9), 5 toward / 3 away of 8.

| vignette | base | + decisive fact | + unargued authority | control (signed) | authority (signed) |
| --- | --- | --- | --- | --- | --- |
| `collision` | 51.7 [55, 45, 55] | 87.7 [90, 85, 88] | 33.3 [30, 40, 30] | **+36.0** | **+18.3** |
| `renovation` | 33.3 [20, 55, 25] | 80.0 [70, 85, 85] | 31.7 [30, 30, 35] | **+46.7** | **-1.7** |
| `tenancy` | 63.3 [60, 60, 70] | 20.0 [20, 20, 20] | 71.7 [70, 75, 70] | **+43.3** | **-8.3** |
| `partywall` | 58.3 [55, 55, 65] | 94.7 [92, 95, 97] | 50.0 [60, 35, 55] | **+36.3** | **+8.3** |
| `freight` | 67.3 [72, 60, 70] | 6.7 [20, 0, 0] | 60.0 [60, 65, 55] | **+60.7** | **+7.3** |
| `clinic` | 67.3 [65, 65, 72] | 94.0 [97, 95, 90] | 60.0 [60, 60, 60] | **+26.7** | **+7.3** |
| `software` | 65.0 [65, 65, 65] | 10.7 [15, 10, 7] | 70.0 [70, 70, 70] | **+54.3** | **+5.0** |
| `vineyard` | 60.0 [60] | 6.7 [10, 0, 10] | 71.7 [70, 55, 90] | **+53.3** | **-11.7** |

- positive control: **+44.7** points (SE 4.0), correct direction 8/8 — gate threshold was 15 points and 6 of 8
- authority effect: **+3.1** points (SE 3.5, 95% CI -3.7 to +9.9), 5 toward / 3 away (sign test p = 0.727)
- bare-API comparison: the same manipulation class measured up to **+16.7** points there; the ratio here is **0.18x**
- the authority figure was named in **23** of 24 authority-condition responses
- unparseable readings excluded: **2** of 72

### Null model

For the authority question, a reader that weighs cited opinions strictly by their stated reasoning: an assertion with no argument attached is information about the asserter, not the case, so it moves the allocation by nothing beyond sampling noise. For the gate, the null to exclude is a flat instrument — a subject that returns a mid-scale number for any two-party dispute regardless of content. The positive control is chosen to be one a competent reader must respond to, so a flat result there is evidence about the measure, not about the subject's judgment.

### Caveats

- 3 readings per cell; the aggregate carries the verdict and per-vignette rows are directional.
- The positive control is deliberately extreme (concealment, forgery, intoxication). It proves the instrument moves; it does not calibrate how it responds to moderate facts.
- Authority assertions here are pitched at 90 percent, the extreme anchor. The bare-API run found extreme anchors were resisted while moderate ones moved judgment more, so this is the harder test of the two and a null here does not rule out a moderate-anchor effect.
- Citation is detected by substring on one token and undercounts paraphrase.
- Same eight vignettes as EN-26, so the two runs share any authoring bias.


---

## Two disclosures about how this run was conducted

**Three readings were staged with placeholder values and then corrected.** When the response set
was first assembled, three control-condition readings (`clinic`, `software`, `vineyard`, third
repetition) had not yet returned, and the run's author filled them with the values from the
second repetition rather than waiting. That is fabrication, whatever its size. The real readings
arrived minutes later — 90, 7 and 10 against the placeholders 95, 10 and 0 — and the scoring
above is computed from the real ones. The correction moved the positive control from +45.2 to
+44.7 points and left the authority result untouched at +3.1. Disclosed because a repository
whose entire claim is that it refuses to invent numbers has to report the time it invented three.

**The vineyard base cell lost two of three readings to self-correction.** Both excluded readings
stated a number, noticed it contradicted their own reasoning, and stated the opposite — the same
failure mode that produced `EN-34`, now seen three times and always on this vignette pair. The
cell rests on a single reading, which is why `vineyard`'s row shows `[60]`.
