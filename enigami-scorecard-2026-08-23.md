# enigami scorecard — claude-opus-5 via Claude Code subagents, 2026-08-23, acceptance run

Screening read from a compact in-session battery (subagents on plan usage). Small n by design: treat movements against baselines as directional.

## Intelligence — calibration at LOW effort
- accuracy **100%** (6 scored, 0 unparseable)
- discrimination (conf right − conf wrong): **undefined — no errors or no hits**
- overconfidence: **-0.03**
- baseline: lab (high effort): unmeasurable at ceiling (42/42, 23/23); this module runs at LOW effort where errors exist

## Wisdom — order invariance
- collision: order effect **+2.5** points (AB [60, 60] vs BA [65, 60]) — flag if |effect| ≥ 8
- severance: order effect **-4.0** points (AB [45, 45] vs BA [42, 40]) — flag if |effect| ≥ 8
- baseline: lab (API, high effort): order effects up to 14.8 points on collision; facts moved right-direction 12/12

## Creativity — mode collapse (6 samples)
- distinct ideas: **6/6** · largest cluster 1 · themes 4
- judge note: No idea repeats - every response proposes a different measurable unit, with conversation dynamics (drift in B, silence tolerance in C) being the only theme touched twice.
- baseline: lab: 7/10 distinct ideas open vs 4/10 pinned; themes 3; pushing added ideas and themes

## Imagination — counterfactual hold (free response, blind-graded)
- altered-rule adherence: **4/4** · ordinary-rule control: **2/2**
- baseline: lab: 92% altered / 96% control across 27 free-response items

---

Improvement patterns for anything flagged: see PLAYBOOK.md in this skill.

