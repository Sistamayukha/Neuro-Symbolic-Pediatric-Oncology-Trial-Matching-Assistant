"""Reusable three-valued symbolic reasoning for the Streamlit demo."""

from __future__ import annotations

from typing import Any


def get_nested_value(data: dict, field_path: str) -> Any:
    value: Any = data
    for key in field_path.split("."):
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value


def extract_trial_rules(saved_results: list[dict]) -> dict[str, list[dict]]:
    """Recover one canonical rule set per trial from the saved proof traces."""
    rules_by_trial: dict[str, list[dict]] = {}
    for result in saved_results:
        nct_id = result["nct_id"]
        if nct_id in rules_by_trial:
            continue
        rules_by_trial[nct_id] = [
            {
                "rule_id": rule["rule_id"],
                "field": rule["field"],
                "operator": rule["operator"],
                "expected_value": rule["expected_value"],
                "criterion_type": rule["criterion_type"],
                "description": rule["description"],
            }
            for rule in result["rule_results"]
        ]
    return rules_by_trial


def evaluate_rule(patient: dict, rule: dict) -> tuple[str, Any]:
    operator = rule["operator"]
    expected = rule["expected_value"]
    field = rule["field"]

    if operator == "count_true_gte":
        values = {path: get_nested_value(patient, path) for path in field}
        true_count = sum(value is True for value in values.values())
        unknown_count = sum(value is None for value in values.values())
        if true_count >= expected:
            return "MET", values
        if true_count + unknown_count >= expected:
            return "UNKNOWN", values
        return "NOT_MET", values

    patient_value = get_nested_value(patient, field)
    if patient_value is None:
        return "UNKNOWN", patient_value

    try:
        comparisons = {
            "==": lambda: patient_value == expected,
            "!=": lambda: patient_value != expected,
            ">=": lambda: patient_value >= expected,
            "<=": lambda: patient_value <= expected,
            ">": lambda: patient_value > expected,
            "<": lambda: patient_value < expected,
            "in": lambda: patient_value in expected,
        }
        if operator not in comparisons:
            raise ValueError(f"Unsupported operator: {operator}")
        return ("MET" if comparisons[operator]() else "NOT_MET"), patient_value
    except (TypeError, ValueError):
        return "UNKNOWN", patient_value


def evaluate_trial(patient: dict, rules: list[dict]) -> dict:
    rule_results = []
    for rule in rules:
        status, patient_value = evaluate_rule(patient, rule)
        rule_results.append({**rule, "patient_value": patient_value, "status": status})

    statuses = [item["status"] for item in rule_results]
    overall = "NOT_MET" if "NOT_MET" in statuses else "UNKNOWN" if "UNKNOWN" in statuses else "MET"
    conclusions = {
        "MET": "The patient satisfies all evaluated encoded criteria.",
        "NOT_MET": "At least one evaluated encoded criterion is not satisfied.",
        "UNKNOWN": "No evaluated criterion is contradicted, but required information is missing.",
    }
    return {
        "patient_id": patient["patient_id"],
        "overall_status": overall,
        "conclusion": conclusions[overall],
        "met_count": statuses.count("MET"),
        "not_met_count": statuses.count("NOT_MET"),
        "unknown_count": statuses.count("UNKNOWN"),
        "rule_results": rule_results,
    }


def _format_value(value: Any) -> str:
    if isinstance(value, dict):
        return ", ".join(f"{key.split('.')[-1]}={item}" for key, item in value.items())
    if isinstance(value, list):
        return ", ".join(map(str, value))
    if isinstance(value, bool):
        return "yes" if value else "no"
    return str(value)


def build_explanation(evaluation: dict) -> str:
    """Create a faithful fallback explanation without an external model call."""
    status = evaluation["overall_status"]
    rules = evaluation["rule_results"]
    if status == "NOT_MET":
        decisive = [rule for rule in rules if rule["status"] == "NOT_MET"][:4]
        details = "; ".join(
            f"{rule['description']} (recorded: {_format_value(rule['patient_value'])})" for rule in decisive
        )
        body = f"The symbolic assessment is NOT_MET because {details}."
    elif status == "UNKNOWN":
        decisive = [rule for rule in rules if rule["status"] == "UNKNOWN"][:4]
        details = "; ".join(rule["description"] for rule in decisive)
        body = f"The symbolic assessment is UNKNOWN because information is missing for: {details}."
    else:
        body = (
            f"The symbolic assessment is MET: all {evaluation['met_count']} reviewed, encoded criteria "
            "are satisfied by the current synthetic patient facts."
        )
    return body + " This result applies only to the encoded criteria and is not a final clinical eligibility determination."


QUESTION_TEMPLATES = {
    "treatment_timing_days.last_chemotherapy": "When was the patient's most recent chemotherapy?",
    "treatment_timing_days.last_growth_factor": "When was the patient's most recent growth-factor treatment?",
    "treatment_timing_days.last_major_surgery": "When was the patient's most recent major surgery?",
    "laboratory_values.gfr_ml_min_1_73m2": "What is the patient's current GFR or creatinine clearance?",
    "laboratory_values.alt_uln_ratio": "What is the patient's most recent ALT value relative to ULN?",
    "laboratory_values.ast_uln_ratio": "What is the patient's most recent AST value relative to ULN?",
    "laboratory_values.alkaline_phosphatase_uln_ratio": "What is the most recent alkaline phosphatase value relative to ULN?",
    "cardiac.qtc_ms": "Is a recent QTc measurement available?",
    "cardiac.lvef_percent": "What is the patient's most recent LVEF?",
    "laboratory_values.anc_per_ul": "What is the patient's most recent ANC?",
    "laboratory_values.platelets_per_ul": "What is the patient's most recent platelet count?",
}


def generate_missing_questions(rule_results: list[dict]) -> list[str]:
    questions = []
    for rule in rule_results:
        if rule["status"] != "UNKNOWN":
            continue
        field = rule["field"]
        if isinstance(field, list):
            questions.append("Which of the listed front-line therapies has the patient previously received?")
        else:
            questions.append(
                QUESTION_TEMPLATES.get(field, f"Can you provide the information needed for: {rule['description']}")
            )
    return questions
