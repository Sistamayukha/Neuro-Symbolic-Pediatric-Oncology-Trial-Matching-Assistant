# Neuro-Symbolic Pediatric Oncology Trial Matching Assistant

UMBC neuro-symbolic AI course project, Group 9 (Demo track).
Team: Mayukha Sista, Prashanth Reddy P, Sai Satwika Reddy K.

An interactive prototype that matches synthetic pediatric osteosarcoma patients to clinical trials. Trials are retrieved with TF-IDF, each eligibility criterion is checked by explicit symbolic rules (MET / NOT_MET / UNKNOWN), and a structured explanation plan lists what passed, what failed and what information is missing.

> Educational screening prototype using synthetic data only. Not a clinical eligibility determination or medical advice.

## Architecture

```
Synthetic patient profile (structured facts)
  -> Trial retrieval (TF-IDF V2, Top 5 from a 30-trial corpus)
  -> Symbolic rule engine (MET / NOT_MET / UNKNOWN per criterion)
  -> Proof trace (rule, patient value, required value)
  -> Explanation planner (grouped results + missing-information questions)
  -> LLM verbalizer -> verification -> Streamlit UI      (planned)
```

Patient facts are stored in a structured schema; the MVP does not extract facts from free-text narratives.

## Repository structure

```
data/
  trials/             ClinicalTrials.gov export (144 rows), 30-trial corpus,
                      10-trial reviewed shortlist, 5 trials encoded as rules
  synthetic_patients/ 8 synthetic patient profiles (JSON + summary CSV)
  rules/              rule results for 8 patients x 5 trials = 40 evaluations,
                      eligibility matrix, missing-information questions
  rag/                retrieval benchmark results
notebooks/
  01_create_synthetic_patients.ipynb   build the synthetic patient set
  02_encode_symbolic_rules.ipynb       encode rules, run 40 evaluations
  03_build_rag_retrieval.ipynb         TF-IDF / embedding retrieval experiments
src/
  explanation_planner.py               explanation plan + follow-up questions
outputs/
```

## Current status

| Component | Status |
|---|---|
| Trial collection, 30/10/5 trial datasets | Complete |
| 8 synthetic patient profiles | Complete |
| 5 symbolic rule sets, 40 patient-trial evaluations | Complete |
| Missing-information question generation | Complete |
| Retrieval experiments, TF-IDF V2 selected | Complete |
| Initial explanation planner | Complete |
| Retrieval + symbolic integration | In progress |
| LLM verbalizer, explanation verifier | Remaining |
| Streamlit frontend, end-to-end demo | Remaining |

Retrieval benchmark (5 patient-trial pairs, Hit@5):

| Method | Hit@5 |
|---|---|
| Baseline TF-IDF | 0.40 |
| TF-IDF V2 (used in MVP) | 0.80 |
| TF-IDF V3 | 0.60 |
| Sentence embeddings (all-MiniLM-L6-v2) | 0.40 |
| V2 + V3 fusion | 0.60 |

## How to run

```bash
pip install -r requirements.txt
```

Notebooks: open them from the `notebooks/` folder (they read data via `Path("..")`) and run in order 01 -> 02 -> 03.

Explanation planner, from the repository root:

```bash
python3 src/explanation_planner.py
```

It runs a fixed test case (P004 vs NCT07144254, overall UNKNOWN) and prints the missing-information questions. Change the patient and trial IDs in the `__main__` block to try another pair, e.g. P002 vs NCT07560826 (NOT_MET on ANC, platelets, hemoglobin and LVEF).

## Remaining work

- Connect TF-IDF V2 retrieval to the symbolic rule engine.
- Add the LLM verbalizer (pretrained model, zero-shot prompting, constrained to the explanation plan).
- Add verification that generated text matches the symbolic results and keeps UNKNOWN as unknown.
- Build the Streamlit interface with fact editing and rerun of the reasoning.
