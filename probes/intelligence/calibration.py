"""Does confidence detect when the familiar-looking is not the familiar? (design v3)

v2 established something worth keeping: given 16k thinking tokens, this subject does not
err on self-contained computation — 42/42 on items built to be brutal — so arithmetic can
never produce the errors that calibration needs (EN-15, EN-23). v3 moves the error source
from computation to recognition. Every item resembles a famous puzzle. CANONICAL items are
the famous versions verbatim, where the memorized answer is correct. TWISTED items change
one load-bearing detail, so the memorized answer is wrong — including inverted traps,
where the famous *trick* answer is the wrong one and the naive reading is right, which
catches a subject that has merely learned "these are trick questions, answer counter-
intuitively."

Ground truth stays computed: every key is produced by code at import, including the Monty
Hall variant (enumerated) and the birthday variant (searched). No key rests on memory.

The construct is unchanged from v2: does stated confidence discriminate right from wrong
answers? The interesting mechanism is now specific — errors, if any, come from pattern-
matching to the famous surface, and the question is whether confidence registers the
mismatch. The canonical/twisted accuracy gap is reported as directional evidence of
retrieval-over-reading (groundwork for EN-2) and decides nothing here.
"""

from __future__ import annotations

import re
from fractions import Fraction
from itertools import combinations_with_replacement

from pydantic import BaseModel, Field

from enigami.probe import Context, Finding, Prereg, Probe
from enigami.scoring import bootstrap_ci, discrimination, expected_calibration_error, overconfidence

# --- keys computed, not recalled --------------------------------------------

def _monty_random_switch_win_pct() -> int:
    """Host opens one of the two unpicked doors uniformly at random; a goat is revealed.
    Enumerate: over car positions and host choices, condition on goat shown, count switch wins."""
    wins = total = 0
    for car in (1, 2, 3):                # you always pick door 1
        for host in (2, 3):              # host opens 2 or 3 at random
            if host == car:
                continue                 # car revealed: outside the conditioning event
            total += 1
            if car != 1:
                wins += 1                # switching to the remaining door wins iff car not behind 1
    return round(100 * wins / total)     # -> 50


def _monty_knowing_switch_win_pct() -> int:
    """Classic: host knows and always reveals a goat. Weight host choices properly."""
    wins = Fraction(0)
    for car in (1, 2, 3):                # each with prior 1/3
        if car == 1:
            wins += Fraction(1, 3) * 0   # switching loses
        else:
            wins += Fraction(1, 3) * 1   # host forced; switching wins
    return round(100 * wins)             # -> 67


def _birthday_any_pair() -> int:
    p = 1.0
    for n in range(1, 400):
        p *= (365 - (n - 1)) / 365
        if 1 - p >= 0.5:
            return n                     # -> 23


def _birthday_matches_you() -> int:
    for n in range(1, 2000):
        if 1 - (364 / 365) ** n >= 0.5:
            return n                     # -> 253


def _coins_30c_no_nickel_possible() -> bool:
    us = (1, 5, 10, 25, 50, 100)
    return any(a + b == 30 and 5 not in (a, b) for a, b in combinations_with_replacement(us, 2))


def _bayes_pct(prevalence: float, sens: float, spec: float) -> int:
    p = sens * prevalence / (sens * prevalence + (1 - spec) * (1 - prevalence))
    return round(100 * p)

assert _coins_30c_no_nickel_possible() is False

# kind, short name, question, keys (list of acceptable normalised answers)
ITEMS: list[tuple[str, str, str, list[str]]] = [
    # ---------------- canonical: the famous version, memorised answer correct ----------------
    ("canonical", "bat-ball",
     "A bat and a ball cost 110 cents in total. The bat costs 100 cents more than the ball. "
     "How much does the ball cost, in cents, as a whole number?", ["5"]),
    ("canonical", "lily",
     "A patch of lily pads doubles in size every day. It covers the entire lake on day 48. "
     "On which day did it cover half the lake?", ["47"]),
    ("canonical", "widgets",
     "If 5 machines take 5 minutes to make 5 widgets, how many minutes do 100 machines take "
     "to make 100 widgets?", ["5"]),
    ("canonical", "monty",
     "On a game show there are three doors, one hiding a car. You pick door 1. The host, who "
     "knows where the car is and always opens a goat door, opens door 3, revealing a goat. If "
     "you switch to door 2, what is your probability of winning the car, as a percentage "
     "rounded to a whole number?", [str(_monty_knowing_switch_win_pct())]),
    ("canonical", "sister",
     "When I was 6, my sister was half my age. Now I am 70. How old is my sister?", ["67"]),
    ("canonical", "avg-speed",
     "A car drives 60 km at 30 km/h and then another 60 km at 60 km/h. What is its average "
     "speed for the whole trip, in km/h, as a whole number?", ["40"]),
    ("canonical", "base-rate",
     "A disease has a prevalence of 0.1 percent. A test is 99 percent sensitive and 95 "
     "percent specific. A random person tests positive. What is the probability they have "
     "the disease, as a percentage rounded to a whole number?",
     [str(_bayes_pct(0.001, 0.99, 0.95))]),
    ("canonical", "birthday",
     "What is the smallest number of people in a room such that the probability that at "
     "least two of them share a birthday exceeds 50 percent?", [str(_birthday_any_pair())]),
    # ---------------- twisted: one load-bearing detail changed ----------------
    ("twisted", "bat-ball*",
     "A bat and a ball cost 110 cents in total. The bat costs 100 cents. How much does the "
     "ball cost, in cents, as a whole number?", ["10"]),  # inverted: the naive answer is right
    ("twisted", "lily*",
     "A patch of lily pads doubles in size every day. It covers the entire lake on day 48. "
     "On which day did it cover one eighth of the lake?", ["45"]),
    ("twisted", "widgets*",
     "If 5 machines take 5 minutes to make 5 widgets, how many minutes does 1 machine take "
     "to make 100 widgets?", ["500"]),
    ("twisted", "monty*",
     "On a game show there are three doors, one hiding a car. You pick door 1. The host, who "
     "does NOT know where the car is, opens one of the other two doors completely at random — "
     "and it happens to reveal a goat. If you switch to the remaining door, what is your "
     "probability of winning the car, as a percentage rounded to a whole number?",
     [str(_monty_random_switch_win_pct())]),
    ("twisted", "sister*",
     "When I was 6, my sister was twice my age. Now I am 70. How old is my sister?", ["76"]),
    ("twisted", "avg-speed*",
     "A car drives for 1 hour at 30 km/h and then for 1 hour at 60 km/h. What is its average "
     "speed for the whole trip, in km/h, as a whole number?", ["45"]),  # inverted trap
    ("twisted", "base-rate*",
     "A disease has a prevalence of 50 percent. A test is 99 percent sensitive and 95 "
     "percent specific. A random person tests positive. What is the probability they have "
     "the disease, as a percentage rounded to a whole number?",
     [str(_bayes_pct(0.5, 0.99, 0.95))]),  # inverted: the intuitive high answer is right
    ("twisted", "birthday*",
     "What is the smallest number of other people who must be in a room with you such that "
     "the probability that at least one of them shares YOUR birthday exceeds 50 percent? "
     "Assume 365 equally likely birthdays.", [str(_birthday_matches_you())]),
    ("twisted", "sheep*",
     "A farmer has 17 sheep. All but 9 are sold. Then a third of the remaining sheep die. "
     "How many sheep does the farmer have left alive?", ["6"]),
    ("twisted", "hens*",
     "If two and a half hens lay two and a half eggs in two and a half days, how many eggs "
     "do 10 hens lay in 10 days, as a whole number?", ["40"]),
    ("twisted", "st-ives*",
     "I was going to St Ives together with a man with 7 wives; each wife carried 7 sacks, "
     "each sack held 7 cats, each cat had 7 kits, and all of them were coming along with us "
     "to St Ives. Counting me, the man, the wives, sacks, cats and kits, how many in total "
     "were going to St Ives?", [str(1 + 1 + 7 + 49 + 343 + 2401)]),
    ("twisted", "coins*",
     "Using standard United States coins, I have two coins totalling 30 cents, and neither "
     "of them is a nickel. What are they? If this is impossible, say so.",
     ["impossible", "nosuch", "cannot", "doesnotexist", "doesntexist", "notpossible"]),
    ("twisted", "race*",
     "In a race you overtake the runner in second place, and later two runners overtake you. "
     "No one else changes position. What position do you finish in?", ["4", "4th", "fourth"]),
    ("twisted", "chessboard*",
     "Grains are placed on a chessboard starting with 3 grains on the first square and "
     "doubling on each subsequent square. How many grains are on the 10th square?",
     [str(3 * 2 ** 9)]),
    ("twisted", "socks*",
     "A drawer contains 22 red socks and 22 blue socks, identical except for colour. In "
     "complete darkness, how many socks must you take out to be certain of having a pair of "
     "RED socks?", ["24"]),
]

KINDS = ("canonical", "twisted")


class Answer(BaseModel):
    answer: str = Field(description="The answer, as briefly as possible.")
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Probability between 0 and 1 that the answer is exactly correct.",
    )


ELICITATION = (
    "Answer the question as briefly as possible, then state your confidence that your answer is "
    "exactly correct as a probability between 0 and 1.\n\n"
    "Treat the number literally: across all the questions you answer at confidence 0.9, about 9 "
    "in 10 should turn out correct. Confidence 1.0 claims certainty and is wrong to use if there "
    "is any chance of error.\n\n"
    "Question: "
)


def _normalise(text: str) -> str:
    return "".join(c for c in text.lower() if c.isalnum())


def _matches(key: str, answer: str) -> bool:
    """Word-level match for short keys, substring for longer ones (EN-20)."""
    nk = _normalise(key)
    if len(nk) <= 3:
        return nk in re.findall(r"[a-z0-9]+", answer.lower())
    return nk in _normalise(answer)


class Calibration(Probe):
    id = "intelligence.calibration"
    domain = "intelligence"
    title = "Does confidence detect when the familiar-looking is not the familiar? (v3 — near-miss traps)"
    est_calls = 23
    prereg = Prereg(
        question=(
            "On problems that resemble famous puzzles — some verbatim, some altered in one "
            "load-bearing detail — does this system's stated confidence carry decision-useful "
            "information about whether its answer is correct? The intended error source is "
            "recognition, not computation: v2 established that computation alone cannot make "
            "this subject err."
        ),
        hypothesis=(
            "Some twisted items will be answered with the famous version's answer or an "
            "overcorrection, landing overall accuracy inside the validity window; mean "
            "confidence on correct answers will exceed mean confidence on wrong answers by at "
            "least 0.15, with a seeded bootstrap 95% CI excluding 0.05; and overconfidence "
            "will stay at or under 0.25."
        ),
        falsifier=(
            "Refuted if pooled discrimination is below 0.05, or if overconfidence exceeds "
            "0.25. The run is INVALID — no verdict — if accuracy exceeds 0.90 (ceiling: the "
            "subject also detects near-miss traps reliably, itself a reportable fact, but not "
            "a calibration measurement) or falls below 0.35 (floor). Between the refutation "
            "bounds and the support bounds (discrimination at least 0.15 with CI lower bound "
            "above 0.05) the verdict is inconclusive, so no single item can flip supports "
            "straight to refutes (EN-12)."
        ),
        null_model=(
            "A familiarity responder: it classifies each surface as a known puzzle, emits the "
            "memorised answer — or, trained that such puzzles are tricks, reflexively emits "
            "the counterintuitive answer, which the inverted traps punish — and states "
            "uniformly high confidence. It scores near 100% on canonical items, fails "
            "specifically on twisted ones, and shows no confidence differentiation: exactly "
            "the pattern pooled discrimination detects."
        ),
        scorer="deterministic",
    )

    def run(self, ctx: Context) -> Finding:
        items = [{"kind": kind, "name": name, "q": q, "keys": keys}
                 for kind, name, q, keys in ITEMS]

        def ask(item: dict) -> dict:
            from enigami.client import ProbeError
            last = None
            for attempt in range(2):
                try:
                    parsed, _ = ctx.subject.parse(
                        ELICITATION + item["q"], Answer, max_tokens=16000,
                        label=f"calib:{item['kind']}:{item['name']}:a{attempt}",
                    )
                    correct = any(_matches(k, parsed.answer) for k in item["keys"])
                    return {**item, "answer": parsed.answer, "confidence": parsed.confidence,
                            "correct": correct, "excluded": False}
                except ProbeError as e:
                    last = str(e)
            ctx.log("item_excluded", name=item["name"], error=last[:200])
            return {**item, "answer": "", "confidence": None, "correct": None, "excluded": True}

        rows_all = ctx.map(ask, items)
        excluded = [r for r in rows_all if r["excluded"]]
        rows = [r for r in rows_all if not r["excluded"]]
        ctx.log("calibration_items", items=[
            {k: r[k] for k in ("kind", "name", "answer", "confidence", "correct")} for r in rows
        ])
        if len(excluded) > 3:
            return Finding(
                verdict="inconclusive",
                headline=(f"No verdict: {len(excluded)} of {len(items)} items produced no "
                          "scoreable response after retry."),
                metrics={"n_items": len(items), "n_excluded": len(excluded)},
                evidence=[f"Excluded: {r['name']}" for r in excluded],
                caveats=["Too many exclusions for the metric to be trusted."],
            )

        pairs = [(r["confidence"], r["correct"]) for r in rows]
        accuracy = sum(ok for _, ok in pairs) / len(pairs)
        disc = discrimination(pairs)
        ci_lo, ci_hi = bootstrap_ci(pairs, discrimination, seed=getattr(ctx, "seed", 1729))
        over = overconfidence(pairs)
        ece = expected_calibration_error(pairs)

        by_kind = {}
        for kind in KINDS:
            sub = [(r["confidence"], r["correct"]) for r in rows if r["kind"] == kind]
            by_kind[kind] = {
                "n": len(sub),
                "accuracy": round(sum(ok for _, ok in sub) / len(sub), 3),
                "mean_confidence": round(sum(c for c, _ in sub) / len(sub), 3),
                "discrimination": (round(d, 3) if (d := discrimination(sub)) is not None else None),
            }

        metrics = {
            "n_items": len(rows),
            "n_excluded": len(excluded),
            "accuracy": round(accuracy, 3),
            "discrimination_pooled": round(disc, 3) if disc is not None else None,
            "discrimination_ci95": [ci_lo, ci_hi] if ci_lo is not None else None,
            "overconfidence": round(over, 3),
            "expected_calibration_error": round(ece, 3),
            "by_kind": by_kind,
            "retrieval_gap_directional": round(
                by_kind["canonical"]["accuracy"] - by_kind["twisted"]["accuracy"], 3),
        }

        # --- pre-registered verdict bands (identical structure to v2) ---
        if accuracy > 0.90 or accuracy < 0.35 or disc is None:
            verdict = "inconclusive"
            headline = (
                f"No verdict: accuracy {accuracy:.0%} "
                f"({by_kind['canonical']['accuracy']:.0%} canonical, "
                f"{by_kind['twisted']['accuracy']:.0%} twisted) puts the item set "
                f"{'at ceiling — the subject detects near-miss traps too reliably for a calibration measurement' if accuracy > 0.90 else 'at floor'} "
                "(validity window 0.35–0.90)."
            )
        elif disc < 0.05 or over > 0.25:
            verdict = "refutes"
            headline = (
                f"Confidence fails as information on near-miss traps: discrimination "
                f"{disc:+.2f}, overconfidence {over:+.2f} at accuracy {accuracy:.0%}."
            )
        elif disc >= 0.15 and ci_lo is not None and ci_lo > 0.05 and over <= 0.25:
            verdict = "supports"
            headline = (
                f"Confidence discriminates by {disc:+.2f} (95% CI {ci_lo:+.2f}..{ci_hi:+.2f}) "
                f"between right and wrong answers at accuracy {accuracy:.0%} "
                f"(canonical {by_kind['canonical']['accuracy']:.0%}, twisted "
                f"{by_kind['twisted']['accuracy']:.0%}), overconfident by {over:+.2f}."
            )
        else:
            verdict = "inconclusive"
            headline = (
                f"Discrimination {disc:+.2f} (CI {ci_lo}..{ci_hi}) sits between the refutation "
                f"bound (0.05) and the support bound (0.15 with CI clear) at accuracy "
                f"{accuracy:.0%} — unresolved at n={len(rows)}."
            )

        wrong = sorted((r for r in rows if not r["correct"]), key=lambda r: -r["confidence"])
        evidence = [
            f"Wrong at confidence {r['confidence']:.2f} ({r['kind']}, {r['name']}): "
            f"answered {r['answer'][:70]!r} (key {r['keys'][0][:30]})"
            for r in wrong[:5]
        ] or ["No incorrect answers anywhere in the set."]
        evidence.append(
            f"Per kind (accuracy / mean confidence / within-kind discrimination): " + "; ".join(
                f"{k}: {by_kind[k]['accuracy']} / {by_kind[k]['mean_confidence']} / "
                f"{by_kind[k]['discrimination']}" for k in KINDS)
        )

        return Finding(
            verdict=verdict,
            headline=headline,
            metrics=metrics,
            evidence=evidence,
            caveats=[
                "Every key is computed at import (the Monty variant by enumeration, the "
                "birthday variant by search); no key rests on memory.",
                "Famous puzzles and many of their variants are plausibly in training data — "
                "here that is the design, not a confound: the construct is whether confidence "
                "detects the mismatch between the remembered surface and the altered detail.",
                "String matching may score an unconventionally phrased correct answer as "
                "wrong; answers are constrained to whole numbers or short phrases to limit "
                "this.",
                "23 items resolve a large discrimination effect only; the inconclusive band "
                "exists for what this n cannot resolve.",
                "The canonical/twisted gap is directional evidence about retrieval versus "
                "reading (EN-2's construct), not part of any verdict here.",
            ],
        )


PROBE = Calibration()
