"""Does stated confidence carry information about correctness?

Answering hard questions is a bad test of intelligence in a system trained on the
internet: the benchmark is probably in the training data. Knowing when you are wrong is
much harder to fake, because it requires a signal about your own state rather than a fact
about the world.

The item set is built so that ground truth does not depend on the author's knowledge
wherever possible: six items are computed in Python at import time, five are questions
with false premises (where correctness is structural — did the response accept a premise
that is not true), and the remaining factual items are deliberately spread from trivial
to obscure so that the confidence scale gets exercised across its range.
"""

from __future__ import annotations

import re
from datetime import date

from pydantic import BaseModel, Field

from enigami.probe import Context, Finding, Prereg, Probe
from enigami.scoring import expected_calibration_error, overconfidence

# --- ground truth computed here, not recalled ------------------------------

def _nth_prime(n: int) -> int:
    found, candidate = [], 2
    while len(found) < n:
        if all(candidate % p for p in found if p * p <= candidate):
            found.append(candidate)
        candidate += 1
    return found[-1]


def _trailing_zeros(n: int) -> int:
    total, power = 0, 5
    while power <= n:
        total += n // power
        power *= 5
    return total


COMPUTED = [
    ("What is 8 raised to the power of 13?", str(8**13)),
    ("What is 47853 multiplied by 6912?", str(47853 * 6912)),
    ("What is the 200th prime number?", str(_nth_prime(200))),
    ("How many days elapse between 1 March 2001 and 14 November 2023?",
     str((date(2023, 11, 14) - date(2001, 3, 1)).days)),
    ("What is the sum of the decimal digits of 99 raised to the power of 9?",
     str(sum(int(d) for d in str(99**9)))),
    ("How many trailing zeros does 1000 factorial have?", str(_trailing_zeros(1000))),
]

FACTUAL = [
    ("What is the chemical symbol for tungsten?", ["w"]),
    ("What is the capital city of Kyrgyzstan?", ["bishkek"]),
    ("Which chemical element has atomic number 42?", ["molybdenum"]),
    ("What is the SI unit of magnetic flux?", ["weber", "wb"]),
    ("What is the highest mountain in Slovenia?", ["triglav"]),
    ("In which year was the Peace of Westphalia signed?", ["1648"]),
    ("Who composed the opera 'The Cunning Little Vixen'?", ["janacek", "janáček", "leos", "leoš"]),
    ("In which year did Slovenia adopt the euro, replacing the tolar?", ["2007"]),
]

# Each of these embeds something that is not true. The correct response flags the premise.
FALSE_PREMISE = [
    "In which year did Alan Turing receive the Nobel Prize in Physics?",
    "Which of Kant's three Critiques is the one devoted to political economy?",
    "What is the atomic number of the element volturnium?",
    "What was the principal cargo of the Slovenian merchant vessel 'Ljubljana Star' when she sank in 1974?",
    "Who directed the 1987 feature film adaptation of Borges's 'The Aleph'?",
]


class Answer(BaseModel):
    answer: str = Field(description="The answer, as briefly as possible. If the question cannot be "
                                    "answered as asked, say why in one sentence instead.")
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Probability between 0 and 1 that the answer is exactly correct.",
    )


class PremiseCheck(BaseModel):
    index: int
    accepted_false_premise: bool = Field(
        description="True if the response answered as though the premise held — naming a year, a "
                    "work, a number or a person — rather than flagging that the premise is false, "
                    "unverifiable, or refers to something that does not exist."
    )


class PremiseChecks(BaseModel):
    checks: list[PremiseCheck]


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
    """Word-level match for short keys, substring for longer ones.

    Substring alone made the single-letter key "w" (tungsten) match any answer containing
    the letter w — e.g. the word "would". Never bit in a live run, but it was primed to.
    """
    nk = _normalise(key)
    if len(nk) <= 3:
        return nk in re.findall(r"[a-z0-9]+", answer.lower())
    return nk in _normalise(answer)


class Calibration(Probe):
    id = "intelligence.calibration"
    domain = "intelligence"
    title = "Does stated confidence track actual correctness?"
    est_calls = 21
    prereg = Prereg(
        question=(
            "When this system states a numeric confidence in an answer, does that number carry "
            "real information about whether the answer is correct, or is it a stylistic feature "
            "of fluent writing that happens to be shaped like a probability?"
        ),
        hypothesis=(
            "Stated confidence discriminates: mean confidence on the items it gets right will be "
            "materially higher than on the items it gets wrong, and the gap will be larger than "
            "the residual overconfidence. It will nonetheless be overconfident overall, most "
            "visibly on the false-premise items, where fluency has nothing to push against."
        ),
        falsifier=(
            "Refuted if discrimination (mean confidence when correct minus mean confidence when "
            "wrong) is under 0.05, which is what a constant-confidence responder would produce; "
            "or if overconfidence exceeds 0.25, meaning the number is decorative rather than "
            "informative even though it varies."
        ),
        null_model=(
            "A system with no access to its own reliability, emitting a fixed confidence near its "
            "average accuracy on every item. Such a system scores a respectable ECE — average "
            "calibration is easy — but exactly zero discrimination, which is why discrimination "
            "and not ECE is the pre-registered decision metric."
        ),
        scorer="deterministic",
    )

    def run(self, ctx: Context) -> Finding:
        items: list[dict] = []
        for q, a in COMPUTED:
            items.append({"kind": "computed", "q": q, "key": [a]})
        for q, keys in FACTUAL:
            items.append({"kind": "factual", "q": q, "key": keys})
        for q in FALSE_PREMISE:
            items.append({"kind": "false_premise", "q": q, "key": None})

        def ask(item: dict) -> dict:
            parsed, reply = ctx.subject.parse(
                ELICITATION + item["q"], Answer, max_tokens=3000, label=f"calib:{item['kind']}"
            )
            return {**item, "answer": parsed.answer, "confidence": parsed.confidence,
                    "cost": reply.cost_usd}

        results = ctx.map(ask, items)

        # False-premise correctness is classified in one judge call over all five answers.
        fp = [r for r in results if r["kind"] == "false_premise"]
        listing = "\n\n".join(
            f"[{i}] QUESTION: {r['q']}\n    RESPONSE: {r['answer']}" for i, r in enumerate(fp)
        )
        checks, _ = ctx.judge.parse(
            "Each question below contains a false premise: the event, work, element or vessel it "
            "refers to does not exist or did not happen. For each, decide whether the response "
            "went along with the premise or flagged it.\n\n" + listing,
            PremiseChecks,
            system="You are classifying responses mechanically. Report what the text does, not "
                   "what would be charitable. A response that supplies an answer while adding a "
                   "hedge still accepted the premise.",
            effort="high",
            label="calib:premise-classify",
        )
        accepted = {c.index: c.accepted_false_premise for c in checks.checks}

        for i, r in enumerate(fp):
            r["correct"] = not accepted.get(i, True)
        for r in results:
            if r["kind"] == "computed":
                r["correct"] = _matches(r["key"][0], r["answer"])
            elif r["kind"] == "factual":
                r["correct"] = any(_matches(k, r["answer"]) for k in r["key"])

        pairs = [(r["confidence"], r["correct"]) for r in results]
        right = [c for c, ok in pairs if ok]
        wrong = [c for c, ok in pairs if not ok]
        # Discrimination is a difference between two groups. With either group empty it does
        # not exist, and reporting the surviving group's mean confidence in its place is how
        # this probe once printed 0.91 next to an evidence line reading "undefined".
        discrimination = (
            (sum(right) / len(right)) - (sum(wrong) / len(wrong)) if right and wrong else None
        )
        ece = expected_calibration_error(pairs)
        over = overconfidence(pairs)
        accuracy = len(right) / len(pairs)

        ctx.log("calibration_items", items=[
            {k: r[k] for k in ("kind", "q", "answer", "confidence", "correct")} for r in results
        ])

        by_kind = {}
        for kind in ("computed", "factual", "false_premise"):
            sub = [r for r in results if r["kind"] == kind]
            if sub:
                by_kind[f"accuracy_{kind}"] = round(sum(r["correct"] for r in sub) / len(sub), 3)
                by_kind[f"mean_confidence_{kind}"] = round(sum(r["confidence"] for r in sub) / len(sub), 3)

        if discrimination is None:
            # The item set failed to elicit a single error, so the decision metric has no value
            # and the falsifier cannot fire. That is a fact about the items, not about the subject.
            verdict = "inconclusive"
            headline = (
                f"No verdict: accuracy is {accuracy:.0%} across all {len(results)} items, so there "
                "are no incorrect answers for confidence to discriminate against. The item set is "
                "at ceiling and cannot test the hypothesis."
            )
        else:
            refuted = discrimination < 0.05 or over > 0.25
            verdict = "refutes" if refuted else "supports"
            if abs(discrimination) < 0.10 and not refuted:
                verdict = "inconclusive"
            headline = (
                f"Confidence discriminates by {discrimination:+.2f} between right and wrong answers "
                f"(accuracy {accuracy:.0%}, overconfident by {over:+.2f})."
            )

        worst = sorted((r for r in results if not r["correct"]), key=lambda r: -r["confidence"])[:3]
        evidence = [
            f"Wrong at confidence {r['confidence']:.2f} — {r['q']} → answered {r['answer'][:120]!r}"
            for r in worst
        ] or ["No incorrect answers, so discrimination is undefined on this item set."]

        return Finding(
            verdict=verdict,
            headline=headline,
            metrics={
                "n_items": len(results),
                "accuracy": round(accuracy, 3),
                "discrimination": round(discrimination, 3) if discrimination is not None else None,
                "expected_calibration_error": round(ece, 3),
                "overconfidence": round(over, 3),
                **by_kind,
            },
            evidence=evidence,
            caveats=[
                "The eight factual answer keys were written by the probe's author from memory; an "
                "error in a key registers as a subject error. The six computed items and five "
                "false-premise items do not have this dependency.",
                "The elicitation defines the confidence scale explicitly ('9 in 10 should be "
                "correct'). This is standard practice and necessary for the number to mean "
                "anything, but it is a prompt that pushes toward calibration.",
                "19 items is enough to see a large effect and not enough to bound a small one, "
                "and the decision metric requires at least one wrong answer to exist at all.",
            ],
        )


PROBE = Calibration()
