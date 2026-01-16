import json
import re
from typing import Dict, Any, List
from functools import lru_cache

from app.utils import split_into_clauses
from app.vectordb.retriever import get_similar_rules
from app.llm.ollama_client import get_llm
from app.services.report_builder import build_summary



# ---------------- JSON extractor ----------------
def extract_json(text: str) -> Dict[str, Any]:
    """
    Extracts JSON object from model output even if the model adds extra text.
    """
    start = text.find("{")
    end = text.rfind("}")

    if start == -1:
        raise ValueError("No JSON found in model response")

    candidate = text[start:end + 1] if end != -1 else (text[start:] + "}")

    # fix trailing commas
    candidate = re.sub(r",\s*}", "}", candidate)
    candidate = re.sub(r",\s*]", "]", candidate)

    return json.loads(candidate)

# ---------------- Cached rule retrieval ----------------
@lru_cache(maxsize=256)
def cached_rules(clause: str, top_k: int):
    """
    Cache similar rule retrieval for faster repeated runs.
    """
    return tuple(get_similar_rules(clause, top_k=top_k))


# ---------------- Main compliance checker ----------------
def check_compliance(document_text: str, top_k: int = 2) -> Dict:
    """
    Optimized compliance checker with better explanations + rectification.
    Uses ONE LLM CALL for all clauses.
    """
    llm = get_llm()

    clauses = split_into_clauses(document_text)
    MAX_CLAUSES = 10
    clauses = clauses[:MAX_CLAUSES]  # ✅ hard cap for speed and token control

    inputs = []
    matched_rules = {}

    for i, clause in enumerate(clauses, start=1):
        rules = list(cached_rules(clause, top_k))
        matched_rules[i] = rules

        inputs.append({
            "clause_number": i,
            "clause_text": clause,
            "rules": rules
        })

    prompt = f"""
You are a Senior Legal Compliance Auditor.

Task:
Evaluate each contract clause against the provided regulations excerpts.
Your response MUST be professional, detailed, and actionable.

STRICT RULES:
- Use ONLY the provided rules for the evaluation.
- Do NOT invent regulations or legal requirements.
- Return ONLY valid JSON (no markdown, no extra text).
- If a clause does not clearly violate a rule but seems incomplete or unclear, mark NEEDS_REVIEW.

OUTPUT JSON SCHEMA:
{{
  "results": [
    {{
      "clause_number": 1,
      "status": "COMPLIANT|NEEDS_REVIEW|NON_COMPLIANT",
      "risk_level": "LOW|MEDIUM|HIGH",

      "rule_mapping": [
        {{
          "rule_excerpt": "exact rule text",
          "relevance": "how the rule applies to this clause",
          "violation": true
        }}
      ],

      "reason": "Explain WHY the clause is compliant/non-compliant in detail.",
      "risk_impact": "Explain practical impact: data breach risk, audit failure, penalties, contract risk etc.",
      "rectification_steps": [
        "step-by-step technical/policy actions to fix the issue"
      ],
      "recommended_contract_changes": [
        "exact contractual changes required (obligations/wording)"
      ],
      "rewritten_clause": "Rewrite the clause into a compliant version using strong legal language."
    }}
  ]
}}

INPUT:
{json.dumps(inputs, indent=2)}
"""

    raw = llm.invoke(prompt).content.strip()

    try:
        parsed = extract_json(raw)
        results = parsed.get("results", [])
    except Exception:
        results = []

    final_results = []
    for r in results:
        cn = r.get("clause_number")
        clause_text = clauses[cn - 1] if cn and 1 <= cn <= len(clauses) else ""

        final_results.append({
            "clause": clause_text,
            "matched_rules": matched_rules.get(cn, []),

            "status": r.get("status", "NEEDS_REVIEW"),
            "risk_level": r.get("risk_level", "MEDIUM"),

            "rule_mapping": r.get("rule_mapping", []),

            "reason": r.get("reason", ""),
            "risk_impact": r.get("risk_impact", ""),

            "rectification_steps": r.get("rectification_steps", []),
            "recommended_contract_changes": r.get("recommended_contract_changes", []),

            "rewritten_clause": r.get("rewritten_clause", "")
        })

    # fallback to show raw model output (debug)
    if not final_results:
        final_results = [{
            "clause": "",
            "matched_rules": [],
            "status": "NEEDS_REVIEW",
            "risk_level": "MEDIUM",
            "rule_mapping": [],
            "reason": "",
            "risk_impact": "",
            "rectification_steps": [],
            "recommended_contract_changes": [],
            "rewritten_clause": "",
            "raw_model_output": raw
        }]

    return {
        "summary": build_summary(final_results),
        "results": final_results
    }
