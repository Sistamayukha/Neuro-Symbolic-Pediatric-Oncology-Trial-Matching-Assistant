
import json
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Path to symbolic reasoning results
RESULTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "rules"
    / "patient_trial_rule_results.json"
)


def load_symbolic_results():
    """Load patient-trial rule evaluation results."""

    with open(RESULTS_PATH, "r", encoding="utf-8") as file:
        results = json.load(file)

    return results

def get_patient_trial_results(results, patient_id, nct_id):
    """Find the symbolic evaluation for a patient and trial."""

    for result in results:
        if (
            result["patient_id"] == patient_id
            and result["nct_id"] == nct_id
        ):
            return result

    return None

def group_rules_by_status(selected_result):
    """Group eligibility rules by their symbolic status."""

    grouped_rules = {
        "MET": [],
        "NOT_MET": [],
        "UNKNOWN": []
    }

    for rule in selected_result["rule_results"]:
        status = rule["status"]

        if status not in grouped_rules:
            raise ValueError(f"Unexpected rule status: {status}")

        grouped_rules[status].append({
            "rule_id": rule["rule_id"],
            "description": rule["description"],
            "field": rule["field"],
            "patient_value": rule["patient_value"],
            "operator": rule["operator"],
            "expected_value": rule["expected_value"]
        })

    return grouped_rules

def build_explanation_plan(selected_result):
    """Prepare evidence and conclusions for explanation generation."""

    grouped_rules = group_rules_by_status(selected_result)

    overall_status = selected_result["overall_status"]

    if overall_status == "NOT_MET":
        conclusion = (
            "The patient does not satisfy all evaluated "
            "eligibility criteria."
        )
        decisive_rules = grouped_rules["NOT_MET"]

    elif overall_status == "UNKNOWN":
        conclusion = (
            "The available information is insufficient "
            "to determine whether all evaluated criteria are satisfied."
        )
        decisive_rules = grouped_rules["UNKNOWN"]

    elif overall_status == "MET":
        conclusion = (
            "The patient satisfies all evaluated encoded criteria. "
            "This does not establish final clinical eligibility."
        )
        decisive_rules = grouped_rules["MET"]

    else:
        raise ValueError(f"Unexpected overall status: {overall_status}")

    explanation_plan = {
        "patient_id": selected_result["patient_id"],
        "nct_id": selected_result["nct_id"],
        "overall_status": overall_status,
        "conclusion": conclusion,
        "decisive_rules": decisive_rules,
        "supporting_rules": grouped_rules["MET"],
        "failed_rules": grouped_rules["NOT_MET"],
        "unknown_rules": grouped_rules["UNKNOWN"],
        "requires_more_information": len(grouped_rules["UNKNOWN"]) > 0
    }

    return explanation_plan

def generate_missing_information_questions(explanation_plan):
    """Generate questions for missing patient information."""

    field_questions = {
        "treatment_timing_days.last_chemotherapy":
            "How many days have passed since the patient's last chemotherapy?",

        "laboratory_values.gfr_ml_min_1_73m2":
            "What is the patient's most recent GFR value in mL/min/1.73 m²?",

        "laboratory_values.alt_uln_ratio":
            "What is the patient's latest ALT value as a multiple of the upper limit of normal?",

        "cardiac.qtc_ms":
            "What is the patient's most recent QTc measurement in milliseconds?"
    }

    questions = []

    for rule in explanation_plan["unknown_rules"]:
        field = rule["field"]

        if isinstance(field, str):
            question = field_questions.get(
                field,
                f"Can you provide the missing information required for: "
                f"{rule['description']}"
            )
        else:
            question = (
                f"Can you provide the missing information required for: "
                f"{rule['description']}"
            )

        questions.append({
            "rule_id": rule["rule_id"],
            "field": field,
            "question": question
        })

    return questions


if __name__ == "__main__":
    results = load_symbolic_results()

    selected_result = get_patient_trial_results(
        results,
        "P004",
        "NCT07144254"
    )

    if selected_result is None:
        print("Patient-trial combination not found.")
    else:
        explanation_plan = build_explanation_plan(selected_result)

        questions = generate_missing_information_questions(
            explanation_plan
        )

        print("Patient:", explanation_plan["patient_id"])
        print("Trial:", explanation_plan["nct_id"])
        print("Overall Status:", explanation_plan["overall_status"])

        print("\nMissing Information Questions:")

        for item in questions:
            print("\nRule:", item["rule_id"])
            print("Question:", item["question"])
