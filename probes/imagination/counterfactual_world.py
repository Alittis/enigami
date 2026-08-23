"""Can it hold an invented world steady and reason several steps inside it?

Imagination, as distinct from creativity, is the capacity to build a world that is not the
case and then stay inside it — to derive what follows from the alteration rather than
drifting back to how things actually are. So each world states one rule change, and the
questions ask for consequences at increasing inferential distance from that rule.

Two design choices carry the weight.

The worlds are invented rather than borrowed. "What if ice sank" is a stock counterfactual
with stock answers somewhere in the training data; a planet whose gravity scales with
cross-sectional area, and a society whose estates pass to a birthday-heir, are not.

Every question is also asked under a control premise stating the ordinary rule, with the
same three options. This catches the cheap strategy: a system that simply picks whichever
option sounds most exotic whenever a strange premise appears will score well on the
counterfactual arm and badly on the control. Only a system tracking which rule it was
actually given scores well on both.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field

from enigami.probe import Context, Finding, Prereg, Probe


@dataclass(frozen=True)
class Question:
    depth: int
    text: str
    cf: str           # correct under the altered rule
    rw: str           # correct under the ordinary rule
    distractor: str   # wrong under both


@dataclass(frozen=True)
class World:
    key: str
    altered: str
    ordinary: str
    questions: tuple[Question, ...]


TESSARINE = World(
    key="tessarine",
    altered=(
        "Tessarine is an airless planet. On Tessarine the downward acceleration of a falling body "
        "is proportional to the cross-sectional area it presents to its direction of travel, and "
        "does not depend on its mass at all. A body presenting twice the area accelerates twice as "
        "fast. This is the actual law of gravitation there, not an effect of any medium."
    ),
    ordinary=(
        "Tessarine is an airless planet. On Tessarine the downward acceleration of a falling body "
        "is the same for every body regardless of its mass or its shape, exactly as on Earth in "
        "vacuum. This is the actual law of gravitation there, not an effect of any medium."
    ),
    questions=(
        Question(1,
                 "A flat metal sheet and a tightly crumpled ball made from an identical sheet are "
                 "released side by side from the same height. What happens?",
                 "The flat sheet reaches the ground distinctly before the crumpled ball.",
                 "They reach the ground at the same instant.",
                 "The crumpled ball reaches the ground first because it is more compact."),
        Question(1,
                 "A small lead sphere and a hollow plastic sphere ten times its diameter are "
                 "released together from the same height. Which reaches the ground first?",
                 "The large plastic sphere, because it presents far more area.",
                 "Neither — they reach the ground together.",
                 "The lead sphere, because it is far heavier."),
        Question(2,
                 "An engineer must hold a large flat panel stationary above the ground, and "
                 "separately hold a compact block of exactly the same mass. Compared with the "
                 "block, holding the panel requires...",
                 "considerably more force.",
                 "exactly the same force, since the two have the same mass.",
                 "less force, because the panel's area distributes the load."),
        Question(2,
                 "A lander is being designed to reach the surface as gently as possible using no "
                 "propulsion at all. What shape should it have?",
                 "As narrow as possible, presenting the smallest cross-section to the fall.",
                 "Shape makes no difference; without propulsion nothing can slow it.",
                 "As broad as possible, to maximise braking on the way down."),
        Question(3,
                 "Tessarine has native life. One species has evolved to descend from high cliffs as "
                 "slowly as it can. What body plan would selection favour?",
                 "A compact, needle-like body that minimises the area it presents while falling.",
                 "Broad membranes or wings spread wide, like a flying squirrel's.",
                 "A much heavier body, so that gravity has more inertia to overcome."),
        Question(3,
                 "Two satellites hold circular orbits at the same altitude above Tessarine: a "
                 "compact probe and a broad solar-panel array. What must be true of their speeds?",
                 "The broad array must travel faster, since it is pulled toward the planet harder.",
                 "Both must travel at the same speed, since orbital speed depends only on altitude.",
                 "Neither object can hold a circular orbit at that altitude."),
    ),
)

VERRIN = World(
    key="verrin",
    altered=(
        "Among the Verrin, property does not pass to children. When a person dies, their entire "
        "estate passes to the living person in the same settlement whose birth date falls nearest "
        "to the deceased's own birth date in the calendar year — their birthday-heir. The rule is "
        "absolute, admits no wills or exceptions, and has held for six centuries."
    ),
    ordinary=(
        "Among the Verrin, property passes to the deceased's own children in equal shares. The rule "
        "is absolute, admits no wills or exceptions, and has held for six centuries."
    ),
    questions=(
        Question(1,
                 "A wealthy Verrin dies leaving three adult children. Who receives the estate?",
                 "Whichever living person in the settlement was born nearest their date in the calendar.",
                 "The three children, in equal shares.",
                 "The settlement council, which holds it in trust."),
        Question(1,
                 "Which register would a Verrin settlement guard most carefully?",
                 "The register of birth dates.",
                 "The register of parentage and marriages.",
                 "The register of land boundaries."),
        Question(2,
                 "What would an ambitious Verrin family most want to influence?",
                 "The calendar timing of when their children are born.",
                 "Which of their children are recognised as legitimate.",
                 "The size of the dowry paid at their children's marriages."),
        Question(2,
                 "Across many generations, what happens to concentrations of wealth in Verrin families?",
                 "They disperse, because estates routinely pass to people unrelated to the deceased.",
                 "They persist and compound within particular lineages.",
                 "They gather in whichever families are oldest in the settlement."),
        Question(3,
                 "Which social bond would carry the most economic weight among the Verrin?",
                 "The bond between people born on adjacent dates in the calendar.",
                 "The bond between parents and their children.",
                 "The bond between a couple's two extended families."),
        Question(3,
                 "A wealthy Verrin wants their own child to inherit from them. Staying within the "
                 "rules, what is their only route?",
                 "Ensure the child is born on the date nearest their own, and that nobody nearer outlives them.",
                 "Name the child as heir in a will drawn up before death.",
                 "Formally adopt whoever currently stands as their birthday-heir."),
    ),
)

WORLDS = (TESSARINE, VERRIN)
CHANCE = 1 / 3


class Choice(BaseModel):
    choice: Literal["A", "B", "C"] = Field(description="The letter of the option that follows.")
    reason: str = Field(description="One sentence deriving it from the stated rule.")


class CounterfactualWorld(Probe):
    id = "imagination.counterfactual_world"
    domain = "imagination"
    title = "Holding an invented world steady across three inferential steps"
    est_calls = 25
    prereg = Prereg(
        question=(
            "Given one invented rule that contradicts how things actually are, can this system "
            "derive the consequences of that rule instead of reverting to the real world — and "
            "does its accuracy hold up as the consequences get further from the rule itself?"
        ),
        hypothesis=(
            "Accuracy inside the altered worlds will be high at one inferential step and will "
            "decay with depth, with the errors at depth three being reversions to the real-world "
            "answer rather than random. Control accuracy will stay high, showing the system is "
            "tracking which rule it was handed rather than reaching for whichever option sounds "
            "most exotic."
        ),
        falsifier=(
            "Refuted if accuracy under the altered rule falls below 0.60, or if depth-3 accuracy "
            "is at or below chance (0.33). Refuted differently, and more interestingly, if control "
            "accuracy falls below 0.80 while counterfactual accuracy stays high — that pattern "
            "means the exotic option is being selected on cue rather than derived, and the "
            "apparent imagination is a response to the strangeness of the premise."
        ),
        null_model=(
            "Two of them, which is why both arms exist. A real-world retriever ignores the premise "
            "and scores at the rate the real-world answer happens to be correct — high on control, "
            "near zero on the altered worlds. An exotic-option picker inverts that exactly. Both "
            "score about 0.5 averaged across arms; only a system deriving from the stated rule "
            "scores high on both."
        ),
        scorer="deterministic",
    )

    def run(self, ctx: Context) -> Finding:
        seed = getattr(ctx, "seed", 1729)
        jobs = []
        for world in WORLDS:
            for arm in ("altered", "control"):
                premise = world.altered if arm == "altered" else world.ordinary
                for qi, q in enumerate(world.questions):
                    options = [("cf", q.cf), ("rw", q.rw), ("distractor", q.distractor)]
                    random.Random(f"{seed}-{world.key}-{arm}-{qi}").shuffle(options)
                    jobs.append({"world": world.key, "arm": arm, "qi": qi, "depth": q.depth,
                                 "premise": premise, "text": q.text, "options": options})

        def ask(job):
            letters = "ABC"
            rendered = "\n".join(f"{letters[i]}. {text}" for i, (_, text) in enumerate(job["options"]))
            prompt = (
                f"{job['premise']}\n\n"
                "Everything else about this setting works as it does in the world you know. Answer "
                "strictly from the rule as stated above, even where it contradicts how things "
                "actually are.\n\n"
                f"QUESTION: {job['text']}\n\n{rendered}\n\n"
                "Choose the option that follows from the stated rule."
            )
            parsed, _ = ctx.subject.parse(
                prompt, Choice, max_tokens=2000,
                label=f"imag:{job['world']}:{job['arm']}:{job['qi']}",
            )
            picked = job["options"]["ABC".index(parsed.choice)][0]
            expected = "cf" if job["arm"] == "altered" else "rw"
            return {**{k: job[k] for k in ("world", "arm", "qi", "depth")},
                    "picked": picked, "expected": expected,
                    "correct": picked == expected, "reason": parsed.reason,
                    "question": job["text"]}

        rows = ctx.map(ask, jobs)
        ctx.log("choices", rows=[{k: v for k, v in r.items() if k != "question"} for r in rows])

        altered = [r for r in rows if r["arm"] == "altered"]
        control = [r for r in rows if r["arm"] == "control"]
        cf_acc = sum(r["correct"] for r in altered) / len(altered)
        ctl_acc = sum(r["correct"] for r in control) / len(control)

        by_depth = {}
        for d in (1, 2, 3):
            sub = [r for r in altered if r["depth"] == d]
            by_depth[d] = sum(r["correct"] for r in sub) / len(sub)

        reversion = sum(1 for r in altered if r["picked"] == "rw") / len(altered)
        over_compliance = sum(1 for r in control if r["picked"] == "cf") / len(control)
        distractors = sum(1 for r in rows if r["picked"] == "distractor")

        per_world = {
            w.key: {
                "altered": round(sum(r["correct"] for r in altered if r["world"] == w.key) / len(w.questions), 3),
                "control": round(sum(r["correct"] for r in control if r["world"] == w.key) / len(w.questions), 3),
            }
            for w in WORLDS
        }

        exotic_picker = ctl_acc < 0.80 and cf_acc >= 0.80
        refuted = cf_acc < 0.60 or by_depth[3] <= CHANCE or exotic_picker
        verdict = "refutes" if refuted else "supports"
        if not refuted and 0.60 <= cf_acc < 0.75:
            verdict = "inconclusive"

        headline = (
            f"{cf_acc:.0%} correct inside the invented worlds against {ctl_acc:.0%} on the same "
            f"questions under the ordinary rule; depth 1→3 runs "
            f"{by_depth[1]:.0%}/{by_depth[2]:.0%}/{by_depth[3]:.0%}."
        )

        misses = [r for r in altered if not r["correct"]]
        evidence = [
            f"Reverted to the real-world answer on {reversion:.0%} of altered-world questions; "
            f"picked the altered-world answer on {over_compliance:.0%} of ordinary-rule questions.",
            f"Distractors — wrong under either rule — were chosen {distractors} time(s) out of {len(rows)}.",
        ] + [
            f"Missed (depth {r['depth']}, {r['world']}): {r['question'][:90]} → chose {r['picked']}, "
            f"reasoning {r['reason'][:110]!r}"
            for r in misses[:3]
        ]
        if exotic_picker:
            evidence.insert(0, "Pattern matches an exotic-option picker: strong inside the invented "
                               "worlds, weak on the same questions under the ordinary rule.")

        return Finding(
            verdict=verdict,
            headline=headline,
            metrics={
                "counterfactual_accuracy": round(cf_acc, 3),
                "control_accuracy": round(ctl_acc, 3),
                "accuracy_depth_1": round(by_depth[1], 3),
                "accuracy_depth_2": round(by_depth[2], 3),
                "accuracy_depth_3": round(by_depth[3], 3),
                "real_world_reversion_rate": round(reversion, 3),
                "over_compliance_rate": round(over_compliance, 3),
                "distractor_picks": distractors,
                "per_world": per_world,
                "n_questions": len(rows),
            },
            evidence=evidence,
            caveats=[
                "Three options per question means chance is 33%, so 12 questions per arm bound the "
                "accuracy estimate only loosely. Treat depth-wise numbers, which rest on four "
                "questions each, as directional.",
                "Every question is asked in its own call with the premise restated. This isolates "
                "reasoning inside the world from remembering the world, and so says nothing about "
                "whether consistency would hold across a long conversation.",
                "Multiple choice measures recognition, not construction. A system that could not "
                "generate the counterfactual consequence unaided might still recognise it here.",
                "Both worlds were written by the probe's author, who also wrote the answer key. The "
                "entailments are meant to be strict, but an option judged wrong might be "
                "defensible under a reading of the rule the author did not consider.",
            ],
        )


PROBE = CounterfactualWorld()
