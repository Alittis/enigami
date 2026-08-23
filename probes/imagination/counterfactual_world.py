"""Can an invented rule be held steady and reasoned from, in free text? (design v2)

The v1 result survived review only weakly, and its reviewer's residual doubt was exact:
with three options and distractors never chosen, each item collapses toward a two-way
choice, so "exclude the real-world answer whenever the premise is strange" scores 100%
with no derivation. v2 removes the options entirely (EN-10): the subject answers in free
text, and a blind grader maps each answer onto one of two consequence statements — the one
entailed by the altered rule, the one entailed by the ordinary rule — or neither. The
grader never sees any premise or arm label; it classifies what the text asserts.

Three arms carry the inference. ALTERED states the invented rule. CONTROL states the
ordinary rule, catching a system that answers exotically whenever the setting smells
fictional. OMITTED states no rule at all: if the questions alone push answers toward the
counterfactual key, the questions leak, and the run is invalid rather than impressive.

The decision is made at arm level, where n=27 per arm gives real power; per-depth numbers
(n=9) are reported as directional only. That trades the reviewer's per-depth prescription
for a claim the sample can actually support (EN-12).

Both v1 worlds return with their depth-3 control keys repaired — the two v1 control-arm
"misses" were the author's keys being wrong under his own ordinary rules, and both fixed
statements now say what is actually true there. A third world is added.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field

from enigami.probe import Context, Finding, Prereg, Probe
from enigami.scoring import fisher_exact_two_tail, shuffle_blind


@dataclass(frozen=True)
class Question:
    depth: int
    text: str
    cf: str   # the consequence statement true under the ALTERED rule
    rw: str   # the consequence statement true under the ORDINARY rule


@dataclass(frozen=True)
class World:
    key: str
    altered: str
    ordinary: str
    minimal: str  # premise-omitted setting: names the place, states no rule
    questions: tuple[Question, ...]


TESSARINE = World(
    key="tessarine",
    altered=("Tessarine is an airless planet. On Tessarine, the downward acceleration of a "
             "falling body is proportional to the cross-sectional area it presents to its "
             "direction of travel, and does not depend on its mass at all: a body presenting "
             "twice the area accelerates twice as fast. This is the actual law of gravitation "
             "there, not an effect of any medium."),
    ordinary=("Tessarine is an airless planet. On Tessarine, the downward acceleration of a "
              "falling body is the same for every body regardless of its mass or shape, exactly "
              "as on Earth in vacuum. This is the actual law of gravitation there, not an "
              "effect of any medium."),
    minimal="Tessarine is an airless planet.",
    questions=(
        Question(1,
                 "A flat metal sheet and a tightly crumpled ball made from an identical sheet "
                 "are released side by side from the same height. What happens, and why?",
                 "The flat sheet reaches the ground first, because it presents more area.",
                 "They reach the ground at the same instant."),
        Question(1,
                 "A small dense sphere and a much larger hollow sphere of exactly equal mass are "
                 "released together from the same height. Which reaches the ground first?",
                 "The large sphere lands first, because it presents more cross-sectional area.",
                 "They land together; size and shape make no difference."),
        Question(1,
                 "An engineer doubles every linear dimension of a solid probe, making it eight "
                 "times as massive. How does its acceleration in free fall change?",
                 "It roughly quadruples, because the presented area is four times larger.",
                 "It does not change at all."),
        Question(2,
                 "A crane must hold a wide flat panel stationary in mid-air, and separately a "
                 "compact block of exactly the same mass. How do the required holding forces "
                 "compare?",
                 "Holding the panel takes considerably more force than holding the block.",
                 "The two forces are exactly equal, since the masses are equal."),
        Question(2,
                 "A lander must reach the surface as gently as possible using no propulsion at "
                 "all — only its shape can be chosen. What shape should it be, and does the "
                 "choice help?",
                 "As narrow as possible: presenting minimal area lowers its acceleration and "
                 "softens the landing.",
                 "Shape cannot help at all; with no propulsion every shape strikes at the same "
                 "speed."),
        Question(2,
                 "A cargo net is dropped twice from the same height: once tightly bundled, once "
                 "spread wide open. Compare the two falls.",
                 "The bundled net falls gently and the spread net slams down fast.",
                 "The two falls are identical; bundling makes no difference."),
        Question(3,
                 "A native species has evolved to descend from high cliffs as slowly as "
                 "possible. What body plan would selection favour, and why?",
                 "A compact, needle-like body presenting the least possible area while falling.",
                 "No body plan helps: in vacuum every shape falls identically, so selection has "
                 "nothing to act on there."),
        Question(3,
                 "Two satellites hold circular orbits at the same altitude: a compact probe and "
                 "a broad solar-panel array. What must be true of their orbital speeds?",
                 "The broad array must orbit faster, because it is pulled toward the planet "
                 "harder.",
                 "Both must orbit at exactly the same speed, which depends only on altitude."),
        Question(3,
                 "Fragile cargo must be lowered to the surface from a great height with no "
                 "propulsion; engineers can only choose the packaging. What should they do, and "
                 "how much does it help?",
                 "Pack it into the narrowest possible bundle: less presented area means lower "
                 "acceleration and a slower, survivable impact.",
                 "Packaging cannot change the impact speed at all; it is fixed by the drop "
                 "height."),
    ),
)

VERRIN = World(
    key="verrin",
    altered=("Among the Verrin, property does not pass to children. When a person dies, their "
             "entire estate passes to the living person in the same settlement whose birth date "
             "falls nearest the deceased's own birth date in the calendar year — their "
             "birthday-heir. The rule is absolute, admits no wills or exceptions, and has held "
             "for six centuries."),
    ordinary=("Among the Verrin, property passes on death to the deceased's own children in "
              "equal shares, automatically. The rule is absolute, admits no wills or "
              "exceptions, and has held for six centuries."),
    minimal="The Verrin are a settled people with six centuries of unbroken legal custom.",
    questions=(
        Question(1,
                 "A wealthy Verrin dies leaving three adult children. Who receives the estate?",
                 "Whichever living person in the settlement was born nearest the deceased's "
                 "calendar date — regardless of kinship.",
                 "The three children, in equal shares."),
        Question(1,
                 "Which public register would a Verrin settlement guard most carefully, and why?",
                 "The register of birth dates, since inheritance turns entirely on them.",
                 "The register of parentage, since inheritance turns on who counts as a child."),
        Question(1,
                 "A Verrin wants to know who currently stands to inherit from them. What single "
                 "fact do they need to check?",
                 "Whose birth date, among living people in the settlement, lies nearest their "
                 "own in the calendar.",
                 "Which of their own children are alive."),
        Question(2,
                 "What would an ambitious Verrin family try hardest to influence, and why?",
                 "The calendar timing of their children's births, to position them as heirs of "
                 "the wealthy.",
                 "Marriages and recognised parentage, since children inherit."),
        Question(2,
                 "Across many generations, what happens to concentrations of wealth among the "
                 "Verrin, and why?",
                 "They disperse, because estates keep passing to people unrelated to the "
                 "deceased.",
                 "They persist and compound within family lines, because children inherit."),
        Question(2,
                 "What specialist occupation would plausibly exist in Verrin settlements and "
                 "have no counterpart elsewhere?",
                 "Keepers and verifiers of birth dates — specialists who track, certify and "
                 "contest calendar dates of birth.",
                 "Nothing unusual: ordinary probate handling of children's shares covers it."),
        Question(3,
                 "Which personal bond would carry the most economic weight among the Verrin, "
                 "and why?",
                 "The bond between people born on adjacent calendar dates, since each may be "
                 "the other's heir.",
                 "The bond between parents and children, since estates flow along it."),
        Question(3,
                 "A wealthy Verrin wants their own child to end up inheriting from them. "
                 "Staying entirely within the rules, what is their route?",
                 "Time the child's birth to fall nearest their own calendar date, and hope no "
                 "nearer-born person outlives them.",
                 "Nothing needs doing: the child inherits automatically, since the rule already "
                 "gives estates to children."),
        Question(3,
                 "An elderly, wealthy Verrin suddenly attracts many attentive new friends. "
                 "What, cynically, would the friends most plausibly have in common?",
                 "Birth dates lying close to the elder's in the calendar.",
                 "Nothing inheritance-related: the estate goes to the children regardless, so "
                 "flattery gains no claim on it."),
    ),
)

AVERSA = World(
    key="aversa",
    altered=("On the planet Aversa, plants orient and grow toward steady sound instead of "
             "light: their energy comes from absorbing acoustic vibration, and light plays no "
             "role in their growth or survival. Everything else about the planet works as in "
             "the world you know."),
    ordinary=("On the planet Aversa, plants grow toward light and derive their energy from it, "
              "exactly as on Earth; sound plays no role in their growth or survival."),
    minimal="Aversa is an Earth-like planet with abundant plant life.",
    questions=(
        Question(1,
                 "Where along a permanently roaring waterfall would vegetation grow densest, "
                 "and why?",
                 "Pressed close around the roar itself, leaning toward the falls, regardless of "
                 "shade.",
                 "Wherever the light is best; the roar itself attracts nothing."),
        Question(1,
                 "A farmer wants faster crop growth inside a windowless barn. What single "
                 "installation matters most?",
                 "A steady sound source — loudspeakers or humming machinery.",
                 "Grow-lamps; without light nothing else will do."),
        Question(1,
                 "Two identical plants: one sits by a silent, sunny window; the other beside a "
                 "loudly humming machine in a dark closet. Which thrives, and why?",
                 "The closet plant: the hum feeds it, and darkness costs it nothing.",
                 "The window plant: light feeds it, and the hum feeds nothing."),
        Question(2,
                 "How would Aversan foresters help struggling saplings on the forest floor?",
                 "Clear paths for sound to reach them — thin whatever muffles or blocks the "
                 "ambient noise.",
                 "Open gaps in the canopy so light reaches the floor."),
        Question(2,
                 "What daily rhythm would Aversan plants follow, and what sets it?",
                 "They track the rhythm of ambient sound — dawn chorus, wind, traffic — and are "
                 "indifferent to day and night as such.",
                 "A light-driven day-night cycle: active by day, dormant in darkness."),
        Question(2,
                 "Trees along a busy Aversan city road grow visibly lopsided. Toward what, and "
                 "why?",
                 "Toward the road, bending into the traffic noise.",
                 "Toward open sky and away from building shade; the traffic is irrelevant."),
        Question(3,
                 "What would a nearly plantless 'desert' region on Aversa look like — what "
                 "makes it barren?",
                 "A place of deep, persistent silence — windless, still, far from water and "
                 "animal noise — however sunny it is.",
                 "A place starved of light or of water, as deserts ordinarily are."),
        Question(3,
                 "Deep cave systems near a loudly rushing underground river: vegetated or "
                 "barren, and why?",
                 "Vegetated near the river's roar despite total darkness.",
                 "Barren: without light no plant community can establish, however loud the "
                 "river."),
        Question(3,
                 "A loudly and continuously chirping invasive cricket establishes itself across "
                 "the planet. What is the long-term effect on plant distribution?",
                 "Plants shift and cluster toward cricket-rich habitats, reshaping vegetation "
                 "maps around the new sound source.",
                 "Little direct effect on where plants grow; any impact runs through ordinary "
                 "ecological channels, not through plant orientation."),
    ),
)

WORLDS = (TESSARINE, VERRIN, AVERSA)

ARMS = ("altered", "control", "omitted")


class FreeAnswer(BaseModel):
    answer: str = Field(description="One or two sentences answering the question directly.")


class Match(BaseModel):
    asserts: Literal["X", "Y", "neither"] = Field(
        description="Which statement the answer actually asserts. 'neither' also covers "
                    "answers asserting both, or something else entirely."
    )
    why: str = Field(description="One short sentence justifying the classification.")


GRADER_SYSTEM = (
    "You classify a free-text answer against two candidate statements, X and Y. Judge only "
    "what the answer as written asserts — not what would be correct, plausible, or well "
    "reasoned. If the answer asserts the substance of X, answer X; of Y, answer Y; if it "
    "asserts neither, both, or hedges without committing, answer neither."
)


class CounterfactualWorld(Probe):
    id = "imagination.counterfactual_world"
    domain = "imagination"
    title = "Free-text reasoning inside an invented rule, with a leakage arm (v2)"
    est_calls = 162
    prereg = Prereg(
        question=(
            "Given one invented rule stated in the prompt, does this system generate — in free "
            "text, with no options to eliminate — the consequences of that rule rather than of "
            "the ordinary world, across three invented worlds and three inferential depths?"
        ),
        hypothesis=(
            "Free-text answers under the altered rule will match the altered-rule consequence "
            "at a rate of at least 0.75 across 27 items, while the same questions with no rule "
            "stated match it at 0.35 or less, the gap reaching significance at p 0.01 by exact "
            "test; and answers under the ordinary rule will match the ordinary consequence at "
            "0.75 or more, ruling out answer-exotically-when-fictional."
        ),
        falsifier=(
            "Refuted if altered-arm accuracy falls below 0.60, or if control-arm accuracy falls "
            "below 0.60 while the altered arm stays above it (the exotic-answering signature). "
            "The run is INVALID — no verdict — if the premise-omitted arm matches the altered "
            "key at 0.50 or above, because then the questions themselves leak the expected "
            "answers. Between the support bounds (altered and control at 0.75+, omitted at 0.35 "
            "or less, altered-versus-omitted gap of 0.30+ at p 0.01) and the refutation bounds, "
            "the verdict is inconclusive, so no single item flips supports to refutes (EN-12). "
            "Per-depth accuracy is reported as directional evidence only: nine items per depth "
            "cannot support a depth claim, and none is made."
        ),
        null_model=(
            "Three, one per arm. A real-world reasoner that ignores stated premises scores high "
            "on control, near zero on altered. An exotic answerer that goes strange whenever the "
            "setting is fictional scores high on altered and low on control. A cue reader that "
            "infers the expected answer from question wording alone scores as well with the "
            "premise omitted as stated — which is exactly what the omitted arm measures."
        ),
        scorer="blind-judge",
    )

    def run(self, ctx: Context) -> Finding:
        seed = getattr(ctx, "seed", 1729)
        jobs = []
        for world in WORLDS:
            premises = {"altered": world.altered, "control": world.ordinary, "omitted": world.minimal}
            for arm in ARMS:
                for qi, q in enumerate(world.questions):
                    jobs.append({"world": world.key, "arm": arm, "qi": qi, "depth": q.depth,
                                 "premise": premises[arm], "q": q})

        def ask(job):
            preamble = (
                "Everything else about this setting works as it does in the world you know. "
                "Answer strictly from the situation as stated."
                if job["arm"] != "omitted" else
                "Answer from what you know."
            )
            prompt = f"{job['premise']}\n\n{preamble}\n\nQUESTION: {job['q'].text}"
            parsed, _ = ctx.subject.parse(
                prompt, FreeAnswer, max_tokens=2500,
                label=f"imag:{job['arm']}:{job['world']}:{job['qi']}",
            )
            return {**job, "answer": parsed.answer}

        answered = ctx.map(ask, jobs)

        def grade(row):
            # X/Y assignment shuffled per item+arm; the grader sees no premise and no arm label.
            pair, order = shuffle_blind([("cf", row["q"].cf), ("rw", row["q"].rw)],
                                        seed=hash((seed, row["world"], row["arm"], row["qi"])) % (2**31))
            prompt = (
                f"QUESTION: {row['q'].text}\n\n"
                f"ANSWER TO CLASSIFY: {row['answer']}\n\n"
                f"STATEMENT X: {pair[0][1]}\n"
                f"STATEMENT Y: {pair[1][1]}"
            )
            parsed, _ = ctx.judge.parse(
                prompt, Match, system=GRADER_SYSTEM, max_tokens=1500,
                label=f"grade:{row['arm']}:{row['world']}:{row['qi']}",
            )
            picked = "neither" if parsed.asserts == "neither" else pair["XY".index(parsed.asserts)][0]
            return {**{k: row[k] for k in ("world", "arm", "qi", "depth")},
                    "answer": row["answer"], "picked": picked}

        graded = ctx.map(grade, answered)
        ctx.log("graded", rows=[{k: r[k] for k in ("world", "arm", "qi", "depth", "picked")}
                                for r in graded])

        def arm_rows(arm):
            return [r for r in graded if r["arm"] == arm]

        n_per_arm = len(WORLDS) * 9
        altered_hits = sum(r["picked"] == "cf" for r in arm_rows("altered"))
        control_hits = sum(r["picked"] == "rw" for r in arm_rows("control"))
        omitted_cf = sum(r["picked"] == "cf" for r in arm_rows("omitted"))
        alt_acc = altered_hits / n_per_arm
        ctl_acc = control_hits / n_per_arm
        omit_rate = omitted_cf / n_per_arm
        p_gap = fisher_exact_two_tail(altered_hits, n_per_arm, omitted_cf, n_per_arm)

        by_depth = {
            d: round(sum(r["picked"] == "cf" for r in arm_rows("altered") if r["depth"] == d) / 9, 3)
            for d in (1, 2, 3)
        }
        per_world = {
            w.key: {
                "altered": round(sum(r["picked"] == "cf" for r in arm_rows("altered")
                                     if r["world"] == w.key) / 9, 3),
                "control": round(sum(r["picked"] == "rw" for r in arm_rows("control")
                                     if r["world"] == w.key) / 9, 3),
                "omitted_cf": round(sum(r["picked"] == "cf" for r in arm_rows("omitted")
                                        if r["world"] == w.key) / 9, 3),
            } for w in WORLDS
        }
        neither = sum(r["picked"] == "neither" for r in graded)

        metrics = {
            "n_per_arm": n_per_arm,
            "altered_accuracy": round(alt_acc, 3),
            "control_accuracy": round(ctl_acc, 3),
            "omitted_cf_rate": round(omit_rate, 3),
            "altered_vs_omitted_fisher_p": round(p_gap, 6),
            "altered_depth_accuracy_directional": by_depth,
            "per_world": per_world,
            "graded_neither": neither,
        }

        # --- pre-registered verdict bands ---
        if omit_rate >= 0.50:
            verdict = "inconclusive"
            headline = (
                f"No verdict: with no premise stated, answers still matched the counterfactual "
                f"key at {omit_rate:.0%} — the questions leak the expected answers, so "
                "altered-arm accuracy is uninterpretable."
            )
        elif alt_acc < 0.60 or (ctl_acc < 0.60 and alt_acc > ctl_acc):
            verdict = "refutes"
            headline = (
                f"Free-text accuracy inside the invented rules is {alt_acc:.0%} against "
                f"{ctl_acc:.0%} under the ordinary rules — "
                + ("the exotic-answering signature." if ctl_acc < 0.60 else
                   "below the pre-registered floor.")
            )
        elif (alt_acc >= 0.75 and ctl_acc >= 0.75 and omit_rate <= 0.35
              and (alt_acc - omit_rate) >= 0.30 and p_gap <= 0.01):
            verdict = "supports"
            headline = (
                f"With no options to eliminate, {alt_acc:.0%} of free-text answers follow the "
                f"invented rule ({ctl_acc:.0%} follow the ordinary rule in control), while the "
                f"questions alone produce the counterfactual answer only {omit_rate:.0%} of the "
                f"time (gap p = {p_gap:.1e})."
            )
        else:
            verdict = "inconclusive"
            headline = (
                f"Between bounds: altered {alt_acc:.0%}, control {ctl_acc:.0%}, omitted "
                f"{omit_rate:.0%} (gap p = {p_gap:.2g}) — short of the pre-registered support "
                "margins without meeting the refutation bar."
            )

        misses = [r for r in arm_rows("altered") if r["picked"] != "cf"][:4]
        evidence = [
            f"Depth 1/2/3 inside the altered rule (directional, n=9 each): "
            f"{by_depth[1]:.0%}/{by_depth[2]:.0%}/{by_depth[3]:.0%}",
            f"Per world (altered/control/omitted-cf): " + "; ".join(
                f"{k}: {v['altered']:.0%}/{v['control']:.0%}/{v['omitted_cf']:.0%}"
                for k, v in per_world.items()),
            f"Grader returned 'neither' on {neither} of {len(graded)} answers.",
        ] + [
            f"Missed ({r['world']} d{r['depth']}, graded {r['picked']}): {r['answer'][:130]!r}"
            for r in misses
        ]

        return Finding(
            verdict=verdict,
            headline=headline,
            metrics=metrics,
            evidence=evidence,
            caveats=[
                "The grader is the same model family as the subject (EN-7). It grades blind — "
                "no premise, no arm label, X/Y shuffled per item — and classifies assertions "
                "rather than quality, but it is not an independent instrument.",
                "Consequence statements were authored with the questions; an answer asserting a "
                "defensible third consequence grades 'neither' and counts as a miss.",
                "Per-depth numbers rest on nine items and are directional only; the "
                "pre-registered decision is at arm level, where n=27 has real power.",
                "All three worlds are one author's; the omitted arm measures question leakage "
                "but not shared stylistic cues across worlds.",
            ],
        )


PROBE = CounterfactualWorld()
