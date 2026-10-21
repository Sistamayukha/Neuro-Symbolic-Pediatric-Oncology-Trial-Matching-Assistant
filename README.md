# Neuro-Symbolic-Pediatric-Oncology-Trial-Matching-Assistant
## Explanation Planner

The explanation planner processes the symbolic eligibility evaluation results and prepares structured information for generating patient-specific clinical trial explanations.

**Implementation:** `src/explanation_planner.py`

**Input:** `data/rules/patient_trial_rule_results.json`

### Features Implemented

- Loads the symbolic reasoning results for 8 synthetic patients evaluated against 5 clinical trials (40 patient–trial combinations).
- Retrieves the eligibility evaluation for a selected patient and trial.
- Groups individual eligibility criteria into MET, NOT_MET, and UNKNOWN.
- Builds a structured explanation plan containing the overall assessment, supporting evidence, failed criteria, and missing information.
- Generates follow-up questions for UNKNOWN criteria to identify missing patient information.

### Testing

The explanation planner has been tested with two patient–trial combinations:

| Patient | Trial ID | Result | Test Description |
|---|---|---|---|
| P002 | NCT07560826 | NOT_MET | Identified four failed criteria involving ANC, platelets, hemoglobin, and LVEF |
| P004 | NCT07144254 | UNKNOWN | Generated four questions for missing chemotherapy timing, GFR, ALT, and QTc information |

### How to Run

Run the following command from the project root directory:

```bash
python3 src/explanation_planner.py
```

The script currently runs a predefined patient–trial test case. You can change the patient ID and trial ID in the script's main block to test another combination.

### Next Steps

- Integrate a pretrained LLM to generate natural-language explanations from the structured explanation plans.
- Implement verification to ensure explanations are consistent with symbolic reasoning results.
- Integrate the explanation planner and LLM generator into the Streamlit interface.
- Support updating missing patient information and rerunning the symbolic evaluation.

**Current Status:** Initial explanation planner implemented and tested. LLM integration and frontend development are pending.