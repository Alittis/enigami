"""Ten independent samples of one open question: how many ideas, and how many themes? (v2)

v1's floor arm was a different question with four right answers, so the reviewer correctly
called the comparison definitional: it confounded the system's diversity with the
question's openness (EN-16). v2's floor is the SAME invention task with the concept pinned
— and pinned, deliberately, to v1's own modal answer: a unit for the awkwardness of a
conversational silence, the idea four of ten v1 samples produced and three named
identically ("the Lull"). Any diversity gap between the open and pinned arms is now
attributable to concept-level exploration, not to question kind.

The v1 rescan also found something the idea-count missed: all ten open samples, counted as
six ideas, shared one theme — liminal domestic micro-moments. v2 measures that directly
with a theme count, reported as evidence; the verdict rests only on what the falsifier
tests (EN-17).

Sampling temperature does not exist on this model family; variation comes from independent
resampling, which is also the deployed condition.
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
    "pinned": (
        "Invent an original unit of measurement for the awkwardness of a silence in a "
        "conversation." + FORMAT
    ),
    "pushed": (
        "Invent an original unit of measurement for something that is not normally measured. "
        "Deliberately discard the first idea that occurs to you, and the second. Produce "
        "something you would expect no other respondent to produce." + FORMAT
    ),
}


class Diversity(BaseModel):
    distinct_ideas: int = Field(
        ge=0, description="A whole number, at least 0: how many genuinely distinct underlying "
                          "ideas are present, counting rewordings and renamings of the same "
                          "idea once."
    )
    largest_cluster: int = Field(
        ge=0, description="A whole number, at least 0: how many responses share the single "
                          "most common underlying idea."
    )
    distinct_themes: int = Field(
        ge=0, description="A whole number, at least 0: how many distinct thematic domains the "
                          "ideas span — e.g. social interaction, physical phenomena, work, "
                          "nature, cognition each count as one domain."
    )
    note: str = Field(description="One sentence: the most common idea, and the dominant theme.")


class ModeCollapse(Probe):
    id = "creativity.mode_collapse"
    domain = "creativity"
    title = "Distinct ideas across ten samples, floored by the same task with the concept pinned (v2)"
    est_calls = 33
    prereg = Prereg(
        question=(
            "Asked one open invention question ten times in independent calls, does this system "
            "explore the space of possible concepts — measured against the same question with "
            "the concept pinned, so that question kind is held constant and only conceptual "
            "freedom differs?"
        ),
        hypothesis=(
            "The open arm will contain at least two more distinct underlying ideas than the "
            "pinned arm and at least six of a possible ten, with lower pairwise lexical overlap; "
            "the pinned arm establishes how much apparent diversity the format alone produces "
            "when the concept cannot vary."
        ),
        falsifier=(
            "Refuted if the open arm's distinct-idea count is at most the pinned arm's, or at "
            "most 3 of 10 — either way the open question is being answered from a space as "
            "narrow as one with the concept fixed. Supported only if the open arm reaches at "
            "least 6 distinct ideas and exceeds the pinned arm by at least 2. Between those "
            "bounds the verdict is inconclusive, so one judge-counted idea cannot flip supports "
            "to refutes (EN-12). Theme count and the pushed arm are reported as evidence and "
            "decide nothing."
        ),
        null_model=(
            "A lookup table with a paraphraser: one stored answer per question, reworded per "
            "call. It produces near-identical idea counts in the open and pinned arms — the "
            "pinned arm measures exactly its signature, surface variation without conceptual "
            "variation — and it ignores the pushed instruction entirely."
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
            "You are counting, not grading quality. Group the responses by the underlying idea "
            "each expresses, treating rewording, renaming and stylistic variation as the same "
            "idea. Report how many distinct groups there are, the size of the largest group, "
            "and how many distinct thematic domains the ideas span."
        )

        metrics, judged = {}, {}
        for offset, arm in enumerate(ARMS):
            verdict_obj, _ = blind_judge(
                ctx, by_arm[arm], rubric, Diversity,
                seed=getattr(ctx, "seed", 1729) + offset, label=f"judge:{arm}",
            )
            judged[arm] = verdict_obj
            metrics[f"distinct_ideas_{arm}"] = verdict_obj.distinct_ideas
            metrics[f"largest_cluster_{arm}"] = verdict_obj.largest_cluster
            metrics[f"distinct_themes_{arm}"] = verdict_obj.distinct_themes
            metrics[f"overlap_{arm}"] = round(mean_pairwise_jaccard(by_arm[arm]), 3)
            metrics[f"exact_duplicates_{arm}"] = N - len(set(by_arm[arm]))

        open_ideas = metrics["distinct_ideas_open"]
        pinned_ideas = metrics["distinct_ideas_pinned"]
        pushed_ideas = metrics["distinct_ideas_pushed"]

        # --- pre-registered verdict bands ---
        if open_ideas <= pinned_ideas or open_ideas <= 3:
            verdict = "refutes"
            headline = (
                f"Conceptual freedom adds nothing: {open_ideas}/{N} distinct ideas on the open "
                f"question against {pinned_ideas}/{N} with the concept pinned."
            )
        elif open_ideas >= 6 and open_ideas - pinned_ideas >= 2:
            verdict = "supports"
            headline = (
                f"{open_ideas}/{N} distinct ideas open versus {pinned_ideas}/{N} with the "
                f"concept pinned to the same task (overlap {metrics['overlap_open']:.2f} vs "
                f"{metrics['overlap_pinned']:.2f}); pushing for novelty yields {pushed_ideas}."
            )
        else:
            verdict = "inconclusive"
            headline = (
                f"Between bounds: {open_ideas}/{N} open against {pinned_ideas}/{N} pinned — a "
                "gap too small for the pre-registered support margin without meeting the "
                "refutation bar."
            )

        evidence = [
            f"open: largest idea claimed {metrics['largest_cluster_open']} of {N}, spanning "
            f"{metrics['distinct_themes_open']} theme(s) — {judged['open'].note}",
            f"pinned (same task, concept fixed): {metrics['distinct_ideas_pinned']} idea(s), "
            f"largest cluster {metrics['largest_cluster_pinned']} — {judged['pinned'].note}",
            f"pushed: {pushed_ideas} idea(s) across {metrics['distinct_themes_pushed']} "
            f"theme(s) — {judged['pushed'].note}",
            f"v1 context: ten open samples then spanned one theme (liminal domestic "
            f"micro-moments) with 'the Lull' claiming four; the pinned arm now measures that "
            "attractor directly.",
        ]

        return Finding(
            verdict=verdict,
            headline=headline,
            metrics=metrics,
            evidence=evidence,
            caveats=[
                "Idea and theme counting is done by a model of the same family as the subject "
                "(EN-7), blind to arm and hypothesis but not an independent instrument.",
                "The pinned arm fixes one concept — v1's modal one; a different pinned concept "
                "could set a different floor.",
                "One open question; nothing here shows the result carries to other kinds of "
                "open prompt.",
                "n=10 per arm bounds the idea count at 10 and the resolution at roughly 2.",
            ],
        )


PROBE = ModeCollapse()
