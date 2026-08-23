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


def test_calibration_refuses_to_report_discrimination_at_ceiling():
    """Regression: with no wrong answers the probe printed discrimination 0.91 beside its own
    evidence line saying the quantity was undefined."""
    import sys
    discover()
    mod = sys.modules["probes.intelligence.calibration"]
    n = len(mod.COMPUTED) + len(mod.FACTUAL) + len(mod.FALSE_PREMISE)
    assert n == 19, "item count changed; the caveat text states 19"
    src = (mod.__file__ and open(mod.__file__).read()) or ""
    assert "if right and wrong else None" in src
    assert 'verdict = "inconclusive"' in src
