# enigami — repo rules

Read `project/ARCHITECTURE.md` §2 before changing anything under `enigami/`. This repo's value
is entirely in its resistance to producing flattering results about the model that wrote it, and
five specific mechanisms carry that. Weakening one is a change to the method, not a refactor —
say so explicitly and get agreement first.

Standing rules:

1. **Never write a finding from an `--offline` run.** The stub emits schema-valid nonsense.
   `report.write_finding` refuses offline results; do not add a bypass.
2. **Never let the subject grade its own output unblinded.** Scoring is deterministic where
   ground truth can be computed, and `scoring.blind_judge` otherwise — it takes texts and a
   rubric and cannot receive condition labels. Keep it that way.
3. **A probe without a null model is not a probe.** `Prereg` requires one, and it must describe
   a system lacking the capacity that would nonetheless score well. If you cannot write one, the
   probe is not measuring anything.
4. **A refuting result is a result.** Do not adjust a probe because it refuted its hypothesis.
   Adjust it only for a defect that would have been a defect either way, and record the change
   in the backlog.
5. **No sampling parameters.** `temperature`, `top_p` and `top_k` do not exist on the current
   model family. `Subject.ask` raises on them deliberately.
6. **The API key lives in `.env`, written only by `deploy/scripts/setup-anthropic-env.sh`.**
   Never hand-edit it, never paste a key into a file or a chat.
