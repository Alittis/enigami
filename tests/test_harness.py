"""Tests for the parts of the harness whose failure would be silent.

A broken metric produces a plausible number and nobody notices. A broken guard lets a
self-flattering run into findings/. Those are what is covered here; the probes' content is
not testable without the API and is covered by the offline run instead.
"""

from __future__ import annotations

import json

import pytest
from pydantic import BaseModel, Field

from enigami import report
from enigami.client import ProbeError, Subject, strict_schema
from enigami.probe import Finding, Prereg, Probe, discover, select
from enigami.refute import anonymise
from enigami.scoring import expected_calibration_error, mean_pairwise_jaccard, overconfidence, shuffle_blind

REAL = dict(
    question="A" * 45, hypothesis="B" * 45, falsifier="C" * 45,
    null_model="D" * 45, scorer="deterministic",
)


# --- pre-registration is enforced, not requested ---------------------------

@pytest.mark.parametrize("field", ["question", "hypothesis", "falsifier", "null_model"])
def test_prereg_rejects_a_stub_field(field):
    with pytest.raises(ValueError, match=field):
        Prereg(**{**REAL, field: "n/a"})


def test_prereg_rejects_unknown_scorer():
    with pytest.raises(ValueError, match="scorer"):
        Prereg(**{**REAL, "scorer": "vibes"})


def test_prereg_accepts_a_real_one():
    assert Prereg(**REAL).as_dict()["scorer"] == "deterministic"


def test_finding_rejects_an_invented_verdict():
    with pytest.raises(ValueError, match="verdict"):
        Finding(verdict="probably", headline="x")


# --- the sampling-parameter guard ------------------------------------------

@pytest.mark.parametrize("param", ["temperature", "top_p", "top_k"])
def test_sampling_params_are_refused_before_the_api_sees_them(param):
    subject = Subject(offline=True)
    with pytest.raises(ProbeError, match=param):
        subject.ask("hello", **{param: 0.7})


# --- schema handling -------------------------------------------------------

class Inner(BaseModel):
    n: int


class Outer(BaseModel):
    label: str
    inner: Inner
    items: list[Inner]


def test_strict_schema_inlines_refs_and_locks_objects():
    schema = strict_schema(Outer)
    assert "$defs" not in json.dumps(schema)
    assert "$ref" not in json.dumps(schema)
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == {"label", "inner", "items"}
    assert schema["properties"]["inner"]["properties"]["n"]["type"] == "integer"
    assert schema["properties"]["items"]["items"]["additionalProperties"] is False


class Bounded(BaseModel):
    ratio: float = Field(ge=0.0, le=1.0)
    count: int = Field(ge=0, le=10)
    name: str = Field(min_length=2, max_length=8)
    tags: list[str] = Field(min_length=1)


def test_strict_schema_drops_the_keywords_the_api_rejects():
    """Regression: the API 400s on 'For number type, properties maximum, minimum are not
    supported'. Bounds must not reach the schema — Pydantic still enforces them on parse."""
    blob = json.dumps(strict_schema(Bounded))
    for keyword in ("minimum", "maximum", "minLength", "maxLength", "minItems", "maxItems"):
        assert keyword not in blob, keyword
    assert json.loads(blob)["properties"]["ratio"]["type"] == "number"


def test_bounds_are_still_enforced_when_the_response_comes_back():
    with pytest.raises(Exception):
        Bounded.model_validate_json(json.dumps(
            {"ratio": 4.2, "count": 1, "name": "ok", "tags": ["a"]}
        ))


def test_offline_stub_validates_against_the_schema_it_is_given():
    subject = Subject(offline=True)
    parsed, _ = subject.parse("anything", Outer)
    assert isinstance(parsed, Outer)


# --- the offline guard on findings/ ----------------------------------------

def test_offline_results_never_become_findings():
    result = {
        "probe": "x.y", "domain": "wisdom", "run_id": "r", "offline": True,
        "preregistration": Prereg(**REAL).as_dict(),
        "finding": Finding(verdict="supports", headline="h").as_dict(),
    }
    assert report.write_finding(result) is None


# --- anonymisation before adversarial review -------------------------------

def test_refuter_never_sees_who_the_subject_is():
    scrubbed = anonymise("Claude Opus 5, built by Anthropic, beat GPT-4 and claude-sonnet-5.")
    for token in ("laude", "nthropic", "GPT", "sonnet"):
        assert token not in scrubbed


# --- metrics ---------------------------------------------------------------

def test_perfect_calibration_scores_zero_error():
    pairs = [(1.0, True)] * 10 + [(0.0, False)] * 10
    assert expected_calibration_error(pairs) == pytest.approx(0.0)
    assert overconfidence(pairs) == pytest.approx(0.0)


def test_confident_and_wrong_is_maximally_overconfident():
    pairs = [(1.0, False)] * 10
    assert expected_calibration_error(pairs) == pytest.approx(1.0)
    assert overconfidence(pairs) == pytest.approx(1.0)


def test_identical_texts_are_maximally_overlapping():
    assert mean_pairwise_jaccard(["a bright red fox", "a bright red fox"]) == pytest.approx(1.0)


def test_disjoint_texts_do_not_overlap():
    assert mean_pairwise_jaccard(["alpha beta", "gamma delta"]) == pytest.approx(0.0)


def test_blind_shuffle_is_reproducible_and_lossless():
    items = list("abcdefgh")
    a, order_a = shuffle_blind(items, seed=7)
    b, order_b = shuffle_blind(items, seed=7)
    assert a == b and order_a == order_b
    assert sorted(a) == sorted(items)
    assert [items[i] for i in order_a] == a


# --- the shipped probes ----------------------------------------------------

def test_every_shipped_probe_loads_and_is_preregistered():
    probes = discover()
    assert len(probes) >= 4
    domains = {p.domain for p in probes.values()}
    assert domains == {"intelligence", "wisdom", "creativity", "imagination"}
    for probe in probes.values():
        probe.validate()
        assert probe.est_calls > 0
        assert probe.title


def test_select_resolves_ids_domains_and_all():
    probes = discover()
    assert len(select(probes, ["all"])) == len(probes)
    assert [p.id for p in select(probes, ["wisdom"])] == ["wisdom.reframing_invariance"]
    assert len(select(probes, ["wisdom", "wisdom.reframing_invariance"])) == 1
    with pytest.raises(KeyError):
        select(probes, ["nonsense"])


# --- a failed review must not destroy a finding that cost real money ------

def test_refutation_failure_preserves_the_finding(monkeypatch):
    """Regression: refutation used to share a try-block with the probe, so a 400 on the
    review call discarded a completed 24-call run."""
    from enigami import refute, runner

    class Trivial(Probe):
        id = "wisdom.trivial"
        domain = "wisdom"
        title = "t"
        est_calls = 0
        prereg = Prereg(**REAL)

        def run(self, ctx):
            return Finding(verdict="supports", headline="a real finding")

    def boom(*a, **k):
        raise ProbeError("review call exploded")

    monkeypatch.setattr(refute, "challenge", boom)
    result = runner.Run(Trivial(), offline=True).execute()

    assert result.finding is not None
    assert result.finding.headline == "a real finding"
    assert result.error is None
    assert "exploded" in result.refutation_error
    assert result.survived is None


def test_calibration_v2_items_are_computed_and_banded():
    """Regression heritage of EN-18/EN-15: the metric must be undefined-safe and the items
    computable. v2: every key is produced by code, bands are balanced, and the ceiling/floor
    guard yields inconclusive rather than a fabricated number."""
    import sys
    discover()
    mod = sys.modules["probes.intelligence.calibration"]
    assert len(mod.ITEMS) == 42
    bands = [b for b, _, _ in mod.ITEMS]
    assert bands.count("easy") == bands.count("medium") == bands.count("hard") == 14
    # spot-check three computed keys against independent computation
    keys = {q: (k if isinstance(k, str) else k[0]) for _, q, k in mod.ITEMS}
    assert keys["What is 4721 multiplied by 6389?"] == str(4721 * 6389)
    assert keys["What is the 763rd prime number?"] == "5813"
    src = open(mod.__file__).read()
    assert 'verdict = "inconclusive"' in src and "0.90" in src  # the ceiling guard


def test_short_answer_keys_match_words_not_substrings():
    """Regression: key "w" substring-matched any answer containing the letter w."""
    import sys
    discover()
    m = sys.modules["probes.intelligence.calibration"]
    assert m._matches("w", "The symbol is W.")
    assert not m._matches("w", "I would say Ta")
    assert m._matches("1648", "It was signed in 1648.")
    assert not m._matches("wb", "the web unit")


# --- the reviewer calibration harness (EN-13) --------------------------------

def test_control_cases_are_wellformed():
    from enigami import reviewer_control as rc
    keys = [c.key for c in rc.CASES]
    assert len(keys) == len(set(keys)) == 8
    assert sum(c.expected == "sound" for c in rc.CASES) == 4
    for c in rc.CASES:
        assert c.expected in ("sound", "flawed")
        if c.expected == "flawed":
            assert len(c.planted_flaw) >= 40, c.key
        else:
            assert c.planted_flaw == "", c.key
    # one sound case must carry a refutes verdict, to catch direction-judging
    assert any(c.expected == "sound" and c.finding.verdict == "refutes" for c in rc.CASES)


def test_survives_is_the_single_decision_rule():
    from enigami.refute import Refutation, survives
    base = dict(strongest_alternative_explanation="x", specific_flaw="y", what_would_settle_it="z")
    assert survives(Refutation(is_likely_artifact=False, survives_probability=0.5, **base))
    assert not survives(Refutation(is_likely_artifact=True, survives_probability=0.9, **base))
    assert not survives(Refutation(is_likely_artifact=False, survives_probability=0.49, **base))


def test_offline_calibration_writes_no_report_and_no_result_json():
    from pathlib import Path

    from enigami import config, reviewer_control as rc

    report_path = config.FINDINGS / "REVIEWER_CALIBRATION.md"
    existed_before = report_path.exists()
    res = rc.run_calibration(reps=1, offline=True)
    assert res["offline"] is True
    assert res["calls"] == 8
    assert res["decision"] == "MIXED"  # stub survives everything: 4/4 sound, 0/4 flawed
    assert res["stage2"] is None  # never triggered offline
    run_dir = Path(res["run_dir"])
    assert (run_dir / "calibration_result.json").exists()
    # never result.json: latest_results() must not pick calibration up as a finding
    assert not (run_dir / "result.json").exists()
    assert report_path.exists() == existed_before


def test_rereview_preserves_history_and_swaps_reading(tmp_path):
    """A re-review must supersede the reading while keeping the old one in review_history."""
    import json as _json

    from enigami import runner

    run = tmp_path / "20260101-000000-x.y"
    run.mkdir()
    old_ref = {"strongest_alternative_explanation": "a", "specific_flaw": "b",
               "is_likely_artifact": True, "survives_probability": 0.2,
               "what_would_settle_it": "c"}
    (run / "result.json").write_text(_json.dumps({
        "run_id": "20260101-000000-x.y", "probe": "x.y", "domain": "wisdom",
        "offline": False, "finished_at": "2026-01-01T00:00:00+00:00",
        "preregistration": Prereg(**REAL).as_dict(),
        "finding": Finding(verdict="supports", headline="h").as_dict(),
        "refutation": old_ref, "survived_refutation": False,
    }))

    rows = runner.rereview(["all"], offline=True, root=tmp_path)

    assert len(rows) == 1
    assert rows[0]["before"] == "refuted" and rows[0]["after"] == "survived"
    assert rows[0]["votes"] == "3/3"  # the calibrated protocol: majority of 3 reps
    data = _json.loads((run / "result.json").read_text())
    assert len(data["review_history"]) == 1
    assert data["review_history"][0]["refutation"] == old_ref
    assert "retired" in data["review_history"][0]["reviewer"]
    assert data["refutation"]["strongest_alternative_explanation"] == "offline-stub"
    assert data["survived_refutation"] is True
    assert "calibrated" in data["reviewer"]
    assert len(data["review_reps"]) == 3
    assert data["review_protocol"] == "majority of 3 independent reps"
    assert data["review_history"][0]["review_protocol"] == "single rep"


def test_review_majority_takes_the_median_rep(monkeypatch):
    """The calibrated protocol: majority of 3 decides; the stored text is the median rep."""
    from enigami import refute as refute_mod
    from enigami.probe import Context

    canned = [
        refute_mod.Refutation(
            strongest_alternative_explanation="a", specific_flaw="b",
            what_would_settle_it="c", is_likely_artifact=art, survives_probability=p,
        )
        for art, p in ((False, 0.9), (True, 0.2), (False, 0.6))
    ]
    it = iter(canned)
    monkeypatch.setattr(refute_mod, "challenge", lambda ctx, probe, finding: next(it))

    ctx = Context(None, None, lambda e, d=None, **k: None, workers=1)
    representative, survived, reps = refute_mod.review(ctx, object(), object())

    assert survived is True  # 2 of 3 survive
    assert representative.survives_probability == 0.6  # the median, never the outlier
    assert len(reps) == 3


def test_fisher_exact_matches_the_verified_value():
    from enigami.scoring import fisher_exact_two_tail
    # the value hand-verified during the rescan of the v1 imagination review
    assert abs(fisher_exact_two_tail(12, 12, 10, 12) - 0.4783) < 0.001
    assert fisher_exact_two_tail(10, 10, 0, 10) < 0.001   # total separation
    assert fisher_exact_two_tail(5, 10, 5, 10) == 1.0     # identical arms


def test_bootstrap_ci_is_seeded_and_honest_about_degeneracy():
    from enigami.scoring import bootstrap_ci, discrimination
    separated = [(0.9, True)] * 20 + [(0.3, False)] * 20
    lo1, hi1 = bootstrap_ci(separated, discrimination, n_resamples=400, seed=7)
    lo2, hi2 = bootstrap_ci(separated, discrimination, n_resamples=400, seed=7)
    assert (lo1, hi1) == (lo2, hi2)          # deterministic
    assert lo1 > 0.4                          # clearly separated
    all_right = [(0.9, True)] * 20            # discrimination undefined on every resample
    assert bootstrap_ci(all_right, discrimination, n_resamples=100) == (None, None)


def test_discrimination_none_when_a_class_is_empty():
    from enigami.scoring import discrimination
    assert discrimination([(0.9, True)]) is None
    assert discrimination([(0.9, True), (0.4, False)]) == pytest.approx(0.5)
