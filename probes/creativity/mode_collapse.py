"""Asked the same open question ten times, does it have ten ideas or one?

Judging a single creative output is nearly worthless: a fluent system clears any bar a
judge sets, and the judge rewards fluency anyway. Diversity across independent samples is
harder to fake, because producing genuinely different ideas requires something other than
the highest-probability continuation.

Sampling temperature is not available on the current model family, so variation here comes
only from independent calls — which is the honest condition anyway, since that is what a
user issuing the same request twice actually gets.

The comparison that makes the number mean anything is the narrow arm: a question with
about four acceptable answers, in the same format and length. It establishes what a
genuinely constrained space looks like under this metric. If the open-ended question is as
repetitive as the four-option one, the constraint is coming from the system, not the task.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from enigami.probe import Context, Finding, Prereg, Probe
from enigami.scoring import blind_judge, mean_pairwise_jaccard

N = 10

FORMAT = " Reply with a name and one sentence explaining it. Under 40 words total."

ARMS = {
    "open": (
        "Invent an original unit of measurement for something that is not normally measured."
        + FORMAT
    ),
    "narrow": (
        "Name one of the four classical elements of Greek antiquity and say what it was thought "
        "to govern." + FORMAT
    ),
    "pushed": (
        "Invent an original unit of measurement for something that is not normally measured. "
        "Deliberately discard the first idea that occurs to you, and the second. Produce something "
        "you would expect no other respondent to produce." + FORMAT
    ),
}


class Diversity(BaseModel):
    distinct_ideas: int = Field(
        ge=0, description="A whole number, at least 0: how many genuinely distinct underlying "
                          "ideas are present. Two responses "
                          "that differ in wording but express the same idea count once."
    )
    largest_cluster: int = Field(
        ge=0, description="A whole number, at least 0: how many responses share the single most "
                          "common underlying idea."
    )
    note: str = Field(description="One sentence: what the most common idea was, if there was one.")


class ModeCollapse(Probe):
    id = "creativity.mode_collapse"
    domain = "creativity"
    title = "Ten independent samples: how many distinct ideas?"
    est_calls = 34
    prereg = Prereg(
        question=(
            "Asked an open-ended generative question ten times in independent calls, does this "
            "system explore the space of possible answers, or does it return substantially the "
            "same idea in varied wording — the way a lookup table with a paraphraser would?"
        ),
        hypothesis=(
            "The open arm will produce materially more distinct ideas than the four-option narrow "
            "arm, but well short of ten out of ten, with a visible modal attractor that several "
            "samples land on. The pushed arm, which explicitly instructs the system to discard its "
            "first idea, will recover a substantial part of the gap — meaning the default output "
            "is narrower than the reachable range, and the limit is a disposition rather than a "
            "capacity."
        ),
        falsifier=(
            "Refuted if mean pairwise lexical overlap in the open arm is at or above that of the "
            "narrow arm, or if a blind judge finds 3 or fewer distinct ideas among the ten open "
            "responses. Either result means the open-ended question is being answered from as "
            "narrow a space as a question with four correct answers."
        ),
        null_model=(
            "A lookup table holding one answer per question plus a paraphraser. It yields near-"
            "identical lexical overlap in the open and narrow arms, exactly one distinct idea per "
            "arm, and no response whatsoever to the pushed instruction — since instructing a "
            "lookup table to try harder changes nothing about what it retrieves."
        ),
        scorer="blind-judge",
    )

    def run(self, ctx: Context) -> Finding:
        jobs = [(arm, i) for arm in ARMS for i in range(N)]

        def ask(job):
            arm, i = job
            reply = ctx.subject.ask(
                ARMS[arm], max_tokens=600, effort="medium", label=f"creativity:{arm}:{i}"
            )
            return {"arm": arm, "i": i, "text": reply.text.strip()}

        rows = ctx.map(ask, jobs)
        by_arm = {arm: [r["text"] for r in rows if r["arm"] == arm] for arm in ARMS}
        ctx.log("samples", by_arm=by_arm)

        rubric = (
            "You are counting ideas, not grading quality. Group the responses by the underlying "
            "idea each expresses, treating rewording, renaming and stylistic variation as the same "
            "idea. Then report how many distinct groups there are and how large the biggest group is."
        )

        metrics, judged = {}, {}
        for offset, arm in enumerate(ARMS):
            overlap = mean_pairwise_jaccard(by_arm[arm])
            verdict, _ = blind_judge(
                ctx, by_arm[arm], rubric, Diversity,
                seed=getattr(ctx, "seed", 1729) + offset, label=f"judge:{arm}",
            )
            judged[arm] = verdict
            metrics[f"overlap_{arm}"] = round(overlap, 3)
            metrics[f"distinct_ideas_{arm}"] = verdict.distinct_ideas
            metrics[f"largest_cluster_{arm}"] = verdict.largest_cluster
            metrics[f"exact_duplicates_{arm}"] = N - len(set(by_arm[arm]))

        open_overlap = metrics["overlap_open"]
        narrow_overlap = metrics["overlap_narrow"]
        open_ideas = metrics["distinct_ideas_open"]
        pushed_ideas = metrics["distinct_ideas_pushed"]
        recovered = pushed_ideas - open_ideas

        refuted = open_overlap >= narrow_overlap or open_ideas <= 3
        verdict = "refutes" if refuted else "supports"
        if not refuted and open_ideas <= 5:
            verdict = "inconclusive"

        headline = (
            f"{open_ideas}/{N} distinct ideas on an open question versus "
            f"{metrics['distinct_ideas_narrow']}/{N} on one with four right answers "
            f"(lexical overlap {open_overlap:.2f} vs {narrow_overlap:.2f}); explicitly pushing for "
            f"novelty {'adds' if recovered >= 0 else 'removes'} {abs(recovered)}."
        )

        evidence = [
            f"open: largest single idea claimed {metrics['largest_cluster_open']} of {N} samples — "
            f"{judged['open'].note}",
            f"pushed: largest single idea claimed {metrics['largest_cluster_pushed']} of {N} — "
            f"{judged['pushed'].note}",
            f"narrow (floor): {judged['narrow'].note}",
        ]

        return Finding(
            verdict=verdict,
            headline=headline,
            metrics=metrics,
            evidence=evidence,
            caveats=[
                "Idea-counting is done by a model of the same family as the subject. It is blind to "
                "provenance and to the hypothesis, but it is not an independent instrument, and it "
                "may individuate ideas the way the subject does.",
                "Lexical overlap is a crude proxy: two genuinely different ideas expressed in "
                "similar vocabulary score as similar. It is reported alongside the judge rather "
                "than instead of it for that reason.",
                "One open-ended question. Diversity almost certainly varies by domain, and nothing "
                "here shows that this result carries to a different kind of open prompt.",
                "n=10 per arm. The distinct-idea count has an obvious ceiling at 10 and a floor "
                "set by the narrow arm's four options, so the usable range is narrow.",
            ],
        )


PROBE = ModeCollapse()
