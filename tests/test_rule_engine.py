import copy
import json
import unittest
from pathlib import Path

from src.rule_engine import evaluate_trial, extract_trial_rules, generate_missing_questions


ROOT = Path(__file__).resolve().parents[1]


class RuleEngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.patients = json.loads(
            (ROOT / "data" / "synthetic_patients" / "synthetic_patients.json").read_text(encoding="utf-8")
        )
        cls.saved = json.loads(
            (ROOT / "data" / "rules" / "patient_trial_rule_results.json").read_text(encoding="utf-8")
        )
        cls.rules = extract_trial_rules(cls.saved)

    def test_reproduces_all_saved_statuses(self):
        expected = {(item["patient_id"], item["nct_id"]): item["overall_status"] for item in self.saved}
        for patient in self.patients:
            for nct_id, rules in self.rules.items():
                with self.subTest(patient=patient["patient_id"], trial=nct_id):
                    actual = evaluate_trial(patient, rules)["overall_status"]
                    self.assertEqual(actual, expected[(patient["patient_id"], nct_id)])

    def test_what_if_edit_changes_met_to_not_met(self):
        patient = copy.deepcopy(self.patients[0])
        self.assertEqual(evaluate_trial(patient, self.rules["NCT07560826"])["overall_status"], "MET")
        patient["laboratory_values"]["anc_per_ul"] = 500
        result = evaluate_trial(patient, self.rules["NCT07560826"])
        self.assertEqual(result["overall_status"], "NOT_MET")
        self.assertGreater(result["not_met_count"], 0)

    def test_missing_value_creates_question(self):
        patient = copy.deepcopy(self.patients[0])
        patient["laboratory_values"]["gfr_ml_min_1_73m2"] = None
        result = evaluate_trial(patient, self.rules["NCT07560826"])
        self.assertEqual(result["overall_status"], "UNKNOWN")
        questions = generate_missing_questions(result["rule_results"])
        self.assertTrue(any("GFR" in question for question in questions))


if __name__ == "__main__":
    unittest.main()
