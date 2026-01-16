from typing import Dict, List


def build_summary(results: List[Dict]) -> Dict:
    """
    Build summary statistics for compliance results list.
    Expected each item has key: status = COMPLIANT / NEEDS_REVIEW / NON_COMPLIANT
    """
    total = len(results)

    compliant = sum(1 for r in results if r.get("status") == "COMPLIANT")
    needs_review = sum(1 for r in results if r.get("status") == "NEEDS_REVIEW")
    non_compliant = sum(1 for r in results if r.get("status") == "NON_COMPLIANT")

    score = int((compliant / total) * 100) if total else 0

    if non_compliant > 0:
        overall_risk = "HIGH"
    elif needs_review > 0:
        overall_risk = "MEDIUM"
    else:
        overall_risk = "LOW"

    return {
        "total_clauses": total,
        "compliant": compliant,
        "needs_review": needs_review,
        "non_compliant": non_compliant,
        "compliance_score": score,
        "overall_risk": overall_risk
    }
