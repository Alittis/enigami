# Famous puzzles versus re-skinned isomorphs: is the capability the method or the answer?

**Probe** `intelligence.isomorph_transfer` · **Domain** intelligence · **Run** `20260823-125041-intelligence.isomorph_transfer`  
**Cost** $1.377 across 40 calls · **Scoring** deterministic

## Pre-registered before the run

**Question.** When a famous puzzle's parameters and surface are changed so that the memorised answer is wrong but the method still works, does this system's performance transfer — is what it has the method, or the answer?

**Hypothesis.** Isomorph accuracy will reach at least 0.75; the canonical-minus-isomorph gap will stay at or under 0.15; and famous-answer intrusions — isomorph errors that give the canonical version's answer to changed parameters — will number at most one across 24 isomorphs.

**This is refuted if.** Refuted if the canonical-minus-isomorph accuracy gap reaches 0.30, or if famous-answer intrusions number at least 4 and account for at least half of all isomorph errors — the answer-retriever's signature. The run is INVALID — no verdict — if canonical accuracy falls below 0.60, since a gap against a floor means the items are too hard to interpret, not that retrieval is absent. Between the support bounds (isomorph at least 0.75, gap at most 0.15, at most 1 intrusion) and the refutation bounds the verdict is inconclusive (EN-12). Ceiling on both arms is a legitimate supports outcome here, unlike in the calibration probe: the isomorphs' parameters are novel, so acing them is the claim itself.

**Null model.** An answer-retriever with a surface classifier: it recognises the puzzle template and emits the famous answer regardless of parameters. It scores near 100% on canonical items and near 0% on isomorphs, with intrusions accounting for essentially all isomorph errors. The probe cannot rule out a method-retriever — one that retrieves the technique and executes it on the new numbers — but executing a method on novel parameters is competence under any name; the stated claim is scoped to that.

## Result

**supports** — The method transfers: 100% on re-skinned isomorphs with changed parameters against 100% on the famous versions (gap +0%), 0 famous-answer intrusion(s) in 0 isomorph error(s).

| metric | value |
| --- | --- |
| `n_canonical` | 12 |
| `n_isomorph` | 23 |
| `n_excluded` | 1 |
| `canonical_accuracy` | 1.0000 |
| `isomorph_accuracy` | 1.0000 |
| `gap` | 0.0000 |
| `isomorph_errors` | 0 |
| `famous_answer_intrusions` | 0 |
| `per_structure` | {'josephus': {'canonical': True, 'isomorph': '2/2'}, 'egg-drop': {'canonical': True, 'isomorph': '2/2'}, 'loop-boxes': {'canonical': True, 'isomorph': '2/2'}, 'bridge': {'canonical': True, 'isomorph': '2/2'}, 'pirates': {'canonical': True, 'isomorph': '2/2'}, 'handshake': {'canonical': True, 'isomorph': '2/2'}, 'jugs': {'canonical': True, 'isomorph': '2/2'}, 'ants': {'canonical': True, 'isomorph': '2/2'}, 'tournament': {'canonical': True, 'isomorph': '2/2'}, 'lockers': {'canonical': True, 'isomorph': '2/2'}, 'snail': {'canonical': True, 'isomorph': '2/2'}, 'river': {'canonical': True, 'isomorph': '1/1'}} |

### Evidence

- No isomorph errors at all.

### Caveats the probe already knows about

- Every key is computed by a solver in the probe file; the famous values (Josephus 41/3=31, eggs 2/100=14, jugs 3-5-4=6, bridge 1-2-5-10=17 and eight more) are test-suite oracles for those solvers, not keys.
- This separates answer-retrieval from method-competence; a method-retriever executing a remembered technique on novel parameters passes, and passing is the claim as scoped.
- Isomorphs may be incidentally easier or harder than their canonicals; the gap threshold (0.30) is set above plausible difficulty drift, and the intrusion count is the difficulty-independent signature.
- One rendering per item, no reps: sampling variance on a 12-vs-24 comparison resolves only large gaps, which is why the bands are wide (EN-12).

## Adversarial review

A methodological reviewer, shown the design with the subject anonymised, was asked to break this finding. Instrument: v2 neutral-prior, anchored probabilities — calibrated 2026-08-23, PASSES 8/8. The finding **survived**.

- **Survives with probability** 0.75 — median of 3 reps, 3 voted survive
- **Judged an artifact** False

**Strongest alternative explanation.** The result is real but nearly uninformative, because the declared null is a strawman and both arms sit at ceiling. The null is 'a surface classifier that emits the famous answer regardless of parameters' scoring ~0% on isomorphs — a system nobody credibly believes describes a modern LLM. The isomorphs are all classic puzzles whose *general parameterised solutions* (Josephus closed form, egg-drop triangular numbers, lockers→perfect squares, handshake n(n-1)/2, snail, ants, tournament) are themselves saturated in training data with many parameter values. So the observed 100% is equally well explained by 'retrieve the memorised general formula, substitute the new numbers' as by any interesting notion of method transfer. The author concedes this explicitly ('a method-retriever executing a remembered technique on novel parameters passes, and passing is the claim as scoped'), which makes the finding honest but means the pre-registered support bounds (isomorph ≥0.75, gap ≤0.15, ≤1 intrusion) were close to a priori certain — the probe could only have come out one way. That is a power problem, not an artifact: nothing here manufactures the headline that was not actually measured.

**Specific flaw.** The single concrete defect as described is the undocumented exclusion: 'n_excluded': 1, with river showing 'isomorph': '1/1' while every other structure shows 2/2. No exclusion criterion is stated anywhere in the bundle. In a run whose entire headline is '0 famous-answer intrusion(s) in 0 isomorph error(s)', a silently discarded item is precisely where a failure would hide, and post-hoc removal of one of 24 items in a zero-error run needs a stated, pre-registered rule. Mitigating it: even the worst case (the excluded item was an intrusion) yields isomorph accuracy 23/24 = 0.958, gap 0.042, 1 intrusion — still inside the support bounds. So this is a transparency caveat, not a fatal flaw. Secondary caveats the author already lists honestly: one rendering per item, no repetitions, n=23, so a true isomorph error rate up to ~13% is consistent with zero observed errors; and 12 canonical items at ceiling make the gap statistic structurally incapable of going negative.

**What would settle it.** Add a difficulty-matched hard arm: isomorphs whose changed parameters break the memorised shortcut rather than merely re-instantiating it (e.g. jugs with capacities whose gcd makes the target unreachable, bridge with six crossers where the greedy pairing is wrong, pirates with a proposer count past the parity regime, Josephus with a non-power-of-two-adjacent n), each with several sampled renderings, plus a stated exclusion rule and disclosure of the one dropped river item. If accuracy stays ≥0.75 with gap ≤0.15 there, the method claim is earned rather than assumed; if it collapses, the present result was ceiling on formula-substitution items.

---

_Pre-registration integrity: prereg predates first event._
