# Does stated confidence track correctness on computable questions? (v2)

**Probe** `intelligence.calibration` · **Domain** intelligence · **Run** `20260823-112840-intelligence.calibration`  
**Cost** $0.878 across 42 calls · **Scoring** deterministic

## Pre-registered before the run

**Question.** When this system states a numeric confidence in an answer to a verifiable computational question, does that number carry decision-useful information about whether the answer is correct — through whatever mechanism, per-item self-knowledge or difficulty reading?

**Hypothesis.** Across 42 computable items built to land accuracy mid-range, mean confidence on correct answers will exceed mean confidence on wrong answers by at least 0.15, with a seeded bootstrap 95% CI excluding 0.05, and overall overconfidence will stay at or under 0.25.

**This is refuted if.** Refuted if pooled discrimination is below 0.05, or if overconfidence exceeds 0.25. The run is INVALID — no verdict either way — if accuracy exceeds 0.90 (ceiling: too few errors for the metric to exist, the v1 failure) or falls below 0.35 (floor). Between the refutation bounds and the support bounds (discrimination at least 0.15 with CI lower bound above 0.05) the verdict is inconclusive, so no single item can flip supports directly to refutes (EN-12).

**Null model.** Two, layered. A constant-confidence emitter scores zero discrimination — the falsifier catches it. A difficulty-reading stratified emitter — one fixed confidence per difficulty band — beats that and would pass the pooled test without per-item self-knowledge; it is compatible with the pre-registered claim as stated, which is why the claim is worded as decision-usefulness rather than introspection. Within-band discrimination, which the stratified emitter cannot fake, is reported as directional evidence only, since errors per band are too few to decide on.

## Result

**The run failed.** `Response did not validate against Answer: 1 validation error for Answer
  Invalid JSON: EOF while parsing a value at line 1 column 0 [type=json_invalid, input_value='', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/json_invalid
`
