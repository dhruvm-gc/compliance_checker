from app.services.report_builder import build_summary

def test_build_summary_basic():
    results = [
        {"status": "COMPLIANT"},
        {"status": "NON_COMPLIANT"},
        {"status": "NEEDS_REVIEW"},
        {"status": "COMPLIANT"},
    ]
    summary = build_summary(results)

    assert summary["total_clauses"] == 4
    assert summary["compliant"] == 2
    assert summary["non_compliant"] == 1
    assert summary["needs_review"] == 1
    assert summary["overall_risk"] == "HIGH"
