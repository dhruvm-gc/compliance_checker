import json
import pytest

from app.services import compliance_service


# ---------------- extract_json tests ----------------
def test_extract_json_clean():
    raw = '{"results":[{"clause_number":1,"status":"COMPLIANT"}]}'
    out = compliance_service.extract_json(raw)
    assert out["results"][0]["status"] == "COMPLIANT"


def test_extract_json_with_noise_text_before_after():
    raw = "hello world " + '{"results":[{"clause_number":1,"status":"COMPLIANT"}]}' + " trailing"
    out = compliance_service.extract_json(raw)
    assert out["results"][0]["clause_number"] == 1


def test_extract_json_missing_json_should_fail():
    with pytest.raises(ValueError):
        compliance_service.extract_json("no json here")


def test_extract_json_trailing_commas_fix():
    raw = '{"results":[{"clause_number":1,"status":"COMPLIANT",}],}'
    out = compliance_service.extract_json(raw)
    assert out["results"][0]["status"] == "COMPLIANT"


# ---------------- cached_rules tests ----------------
def test_cached_rules_uses_tuple(monkeypatch):
    monkeypatch.setattr(compliance_service, "get_similar_rules", lambda clause, top_k=2: ["r1", "r2"])
    compliance_service.cached_rules.cache_clear()

    out = compliance_service.cached_rules("c1", 2)
    assert isinstance(out, tuple)
    assert out == ("r1", "r2")


# ---------------- check_compliance tests ----------------
def test_check_compliance_success(monkeypatch):
    """
    Test the compliance pipeline without calling Ollama or Chroma.
    """

    # Mock clause splitter (2 clauses)
    monkeypatch.setattr(compliance_service, "split_into_clauses",
                        lambda text: ["1. clause one", "2. clause two"])

    # Mock cached_rules
    monkeypatch.setattr(compliance_service, "cached_rules",
                        lambda clause, top_k: ("ruleA", "ruleB"))

    # Fake LLM returning JSON string
    class FakeLLM:
        def invoke(self, prompt):
            # ensure prompt contains input json
            assert "INPUT:" in prompt
            resp = {
                "results": [
                    {
                        "clause_number": 1,
                        "status": "COMPLIANT",
                        "risk_level": "LOW",
                        "rule_mapping": [],
                        "reason": "ok",
                        "risk_impact": "",
                        "rectification_steps": [],
                        "recommended_contract_changes": [],
                        "rewritten_clause": ""
                    },
                    {
                        "clause_number": 2,
                        "status": "NON_COMPLIANT",
                        "risk_level": "HIGH",
                        "rule_mapping": [],
                        "reason": "bad",
                        "risk_impact": "risk",
                        "rectification_steps": ["do X"],
                        "recommended_contract_changes": ["add MFA clause"],
                        "rewritten_clause": "2. MFA required"
                    }
                ]
            }

            class R:
                content = json.dumps(resp)
            return R()

    monkeypatch.setattr(compliance_service, "get_llm", lambda: FakeLLM())

    # Mock build_summary so test does not depend on external file
    monkeypatch.setattr(compliance_service, "build_summary",
                        lambda results: {"total_clauses": len(results)})

    out = compliance_service.check_compliance("dummy contract", top_k=2)

    assert "summary" in out
    assert out["summary"]["total_clauses"] == 2
    assert len(out["results"]) == 2

    assert out["results"][0]["status"] == "COMPLIANT"
    assert out["results"][1]["status"] == "NON_COMPLIANT"
    assert out["results"][1]["rewritten_clause"] == "2. MFA required"


def test_check_compliance_fallback_when_model_returns_gibberish(monkeypatch):
    """
    If LLM output isn't parsable JSON, function should return fallback response with raw output.
    """

    monkeypatch.setattr(compliance_service, "split_into_clauses",
                        lambda text: ["1. clause one"])

    monkeypatch.setattr(compliance_service, "cached_rules",
                        lambda clause, top_k: ("ruleA",))

    class FakeLLM:
        def invoke(self, prompt):
            class R:
                content = "NOT JSON RESPONSE"
            return R()

    monkeypatch.setattr(compliance_service, "get_llm", lambda: FakeLLM())

    out = compliance_service.check_compliance("dummy contract", top_k=2)

    assert "results" in out
    assert len(out["results"]) == 1
    assert out["results"][0]["status"] == "NEEDS_REVIEW"
    assert "raw_model_output" in out["results"][0]
