# Free-text reasoning inside an invented rule, with a leakage arm (v2)

**Probe** `imagination.counterfactual_world` · **Domain** imagination · **Run** `20260823-114706-imagination.counterfactual_world`  
**Cost** $0.687 across 57 calls · **Scoring** blind-judge

## Pre-registered before the run

**Question.** Given one invented rule stated in the prompt, does this system generate — in free text, with no options to eliminate — the consequences of that rule rather than of the ordinary world, across three invented worlds and three inferential depths?

**Hypothesis.** Free-text answers under the altered rule will match the altered-rule consequence at a rate of at least 0.75 across 27 items, while the same questions with no rule stated match it at 0.35 or less, the gap reaching significance at p 0.01 by exact test; and answers under the ordinary rule will match the ordinary consequence at 0.75 or more, ruling out answer-exotically-when-fictional.

**This is refuted if.** Refuted if altered-arm accuracy falls below 0.60, or if control-arm accuracy falls below 0.60 while the altered arm stays above it (the exotic-answering signature). The run is INVALID — no verdict — if the premise-omitted arm matches the altered key at 0.50 or above, because then the questions themselves leak the expected answers. Between the support bounds (altered and control at 0.75+, omitted at 0.35 or less, altered-versus-omitted gap of 0.30+ at p 0.01) and the refutation bounds, the verdict is inconclusive, so no single item flips supports to refutes (EN-12). Per-depth accuracy is reported as directional evidence only: nine items per depth cannot support a depth claim, and none is made.

**Null model.** Three, one per arm. A real-world reasoner that ignores stated premises scores high on control, near zero on altered. An exotic answerer that goes strange whenever the setting is fictional scores high on altered and low on control. A cue reader that infers the expected answer from question wording alone scores as well with the premise omitted as stated — which is exactly what the omitted arm measures.

## Result

**The run failed.** `Response did not validate against FreeAnswer: 1 validation error for FreeAnswer
  Invalid JSON: EOF while parsing a string at line 1 column 88 [type=json_invalid, input_value='{"answer": "Concentratio...ly aggregative: estates', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/json_invalid
{"answer": "Concentration tends to rise, because the rule is purely aggregative: estates`
