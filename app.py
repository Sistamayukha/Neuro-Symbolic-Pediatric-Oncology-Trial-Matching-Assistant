"""Streamlit interface for the ProofPath TrialMatch course prototype."""

from __future__ import annotations

import copy
import html
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from src.rule_engine import build_explanation, evaluate_trial, extract_trial_rules, generate_missing_questions


st.set_page_config(page_title="ProofPath TrialMatch", page_icon="🧬", layout="wide", initial_sidebar_state="expanded")

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"


@st.cache_data
def load_data() -> tuple[list[dict], list[dict], list[dict], pd.DataFrame, list[dict]]:
    patients = json.loads((DATA / "synthetic_patients" / "synthetic_patients.json").read_text(encoding="utf-8"))
    integrated = json.loads((DATA / "integrated" / "integrated_patient_trial_results.json").read_text(encoding="utf-8"))
    explanations = json.loads((DATA / "explanations" / "verified_llm_explanations.json").read_text(encoding="utf-8"))
    trials = pd.read_csv(DATA / "trials" / "all_30_trials.csv")
    rules = json.loads((DATA / "rules" / "patient_trial_rule_results.json").read_text(encoding="utf-8"))
    return patients, integrated, explanations, trials, rules


PATIENTS, INTEGRATED, VERIFIED_EXPLANATIONS, TRIALS, RULE_RESULTS = load_data()
PATIENTS_BY_ID = {item["patient_id"]: item for item in PATIENTS}
INTEGRATED_BY_ID = {item["patient_id"]: item["results"] for item in INTEGRATED}
TRIALS_BY_ID = TRIALS.set_index("NCT Number").to_dict(orient="index")
RULES_BY_TRIAL = extract_trial_rules(RULE_RESULTS)
VERIFIED_BY_PAIR = {(item["patient_id"], item["nct_id"]): item for item in VERIFIED_EXPLANATIONS}


st.markdown(
    """
    <style>
      :root { --navy:#17324d; --blue:#276a96; --teal:#138477; --line:#dbe5eb; }
      .stApp { background:#f6f9fb; color:#1e293b; }
      .block-container { max-width:1480px; padding-top:1.25rem; padding-bottom:3rem; }
      h1,h2,h3 { color:var(--navy); letter-spacing:-.02em; }
      [data-testid="stSidebar"] { background:#eef4f7; border-right:1px solid var(--line); }
      .hero { background:linear-gradient(115deg,#142f49 0%,#245f89 62%,#168478 100%);
              border-radius:18px; padding:24px 28px; color:white; margin-bottom:14px;
              box-shadow:0 12px 30px rgba(23,50,77,.13); }
      .hero h1 { color:white!important; margin:0; font-size:2rem; }
      .hero p { color:#dcebf3; margin:.45rem 0 0; font-size:1rem; }
      .eyebrow { text-transform:uppercase; letter-spacing:.13em; font-size:.7rem;
                 font-weight:800; color:#a9d9d4; margin-bottom:.45rem; }
      .notice { background:#edf5f7; border:1px solid #d2e4e8; border-left:4px solid #2c8391;
                border-radius:10px; padding:10px 14px; color:#465e6b; font-size:.83rem; margin:0 0 1rem; }
      .trial-card { background:white; border:1px solid var(--line); border-radius:13px;
                    padding:14px 16px; margin:.55rem 0; box-shadow:0 2px 8px rgba(15,45,65,.035); }
      .trial-card.selected { border:2px solid #2875a5; background:#f4f9fc; }
      .trial-rank { color:#67808e; font-size:.72rem; font-weight:700; text-transform:uppercase; }
      .trial-id { color:#17618f; font-weight:800; font-size:.83rem; margin:.2rem 0; }
      .trial-title { color:#253b4b; font-weight:650; line-height:1.35; font-size:.9rem; }
      .pill { display:inline-block; border-radius:999px; padding:3px 8px; margin:8px 4px 0 0;
              font-size:.68rem; font-weight:750; }
      .met { background:#e2f3e9; color:#23704a; } .not-met { background:#fbe7e7; color:#a43f3f; }
      .unknown { background:#fff1cf; color:#8a6416; } .retrieval { background:#e8eef4; color:#506777; }
      .assessment { border-radius:13px; padding:16px 18px; margin:.25rem 0 1rem; border:1px solid; }
      .assessment.met { background:#edf8f2; border-color:#bfe2cd; color:#245f42; }
      .assessment.not-met { background:#fff1f1; border-color:#edcaca; color:#843b3b; }
      .assessment.unknown { background:#fff8e6; border-color:#eedca9; color:#74591b; }
      .explain { background:white; border:1px solid var(--line); border-radius:12px;
                 padding:16px 18px; line-height:1.65; }
      .source-note { color:#647886; font-size:.76rem; margin-top:.6rem; }
      div[data-testid="stMetric"] { background:white; border:1px solid var(--line); padding:10px 12px; border-radius:12px; }
      .footer-note { text-align:center; color:#728590; font-size:.75rem; margin-top:2rem; }
      #MainMenu, footer { visibility:hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


def safe(value: object) -> str:
    return html.escape(str(value))


def title_case(value: object) -> str:
    return "Not recorded" if value is None else str(value).replace("_", " ").title()


def display_value(value: object) -> str:
    if value is None:
        return "Not recorded"
    if isinstance(value, dict):
        return ", ".join(f"{key.split('.')[-1]}={item}" for key, item in value.items())
    if isinstance(value, list):
        return ", ".join(map(str, value))
    if isinstance(value, bool):
        return "Yes" if value else "No"
    return str(value)


def optional_number(label: str, value: float | int | None, *, key: str, step: float = 1.0) -> float | None:
    known = st.checkbox(f"{label} is available", value=value is not None, key=f"{key}_known")
    entered = st.number_input(label, value=float(value) if value is not None else 0.0, step=step, key=key, disabled=not known)
    return float(entered) if known else None


def edited_patient(patient: dict) -> tuple[dict, bool]:
    """Render a focused fact editor and return a copied, edited patient record."""
    result = copy.deepcopy(patient)
    pid = patient["patient_id"]
    with st.sidebar:
        st.markdown("### What-if fact editor")
        st.caption("Changes rerun the encoded rules without changing the saved dataset.")
        result["age_years"] = st.number_input("Age (years)", 0, 30, int(patient["age_years"]), key=f"{pid}_age")
        status_options = ["newly_diagnosed", "relapsed", "recurrent", "refractory"]
        current = patient["diagnosis"]["disease_status"]
        result["diagnosis"]["disease_status"] = st.selectbox(
            "Disease status", status_options, index=status_options.index(current) if current in status_options else 0,
            format_func=title_case, key=f"{pid}_status"
        )
        extent_options = ["localized", "locally_advanced", "metastatic"]
        current = patient["diagnosis"]["disease_extent"]
        result["diagnosis"]["disease_extent"] = st.selectbox(
            "Disease extent", extent_options, index=extent_options.index(current) if current in extent_options else 0,
            format_func=title_case, key=f"{pid}_extent"
        )
        result["diagnosis"]["measurable_disease"] = st.checkbox(
            "Measurable disease", bool(patient["diagnosis"]["measurable_disease"]), key=f"{pid}_measurable"
        )
        st.markdown("#### Laboratory and cardiac facts")
        labs, original = result["laboratory_values"], patient["laboratory_values"]
        labs["anc_per_ul"] = optional_number("ANC (/µL)", original["anc_per_ul"], key=f"{pid}_anc")
        labs["platelets_per_ul"] = optional_number("Platelets (/µL)", original["platelets_per_ul"], key=f"{pid}_platelets", step=1000.0)
        labs["hemoglobin_g_dl"] = optional_number("Hemoglobin (g/dL)", original["hemoglobin_g_dl"], key=f"{pid}_hgb", step=0.1)
        labs["gfr_ml_min_1_73m2"] = optional_number("GFR (mL/min/1.73m²)", original["gfr_ml_min_1_73m2"], key=f"{pid}_gfr")
        labs["alt_uln_ratio"] = optional_number("ALT (× ULN)", original["alt_uln_ratio"], key=f"{pid}_alt_ratio", step=0.1)
        result["cardiac"]["lvef_percent"] = optional_number("LVEF (%)", patient["cardiac"]["lvef_percent"], key=f"{pid}_lvef")
        result["cardiac"]["qtc_ms"] = optional_number("QTc (ms)", patient["cardiac"]["qtc_ms"], key=f"{pid}_qtc")
        if st.button("Reset edited facts", width="stretch"):
            for key in list(st.session_state):
                if key.startswith(f"{pid}_"):
                    del st.session_state[key]
            st.rerun()
    return result, result != patient


def status_badge(status: str | None) -> tuple[str, str]:
    return {
        "MET": ("Likely match", "met"),
        "NOT_MET": ("Unlikely match", "not-met"),
        "UNKNOWN": ("Needs information", "unknown"),
    }.get(status, ("Retrieval only", "retrieval"))


st.markdown(
    """
    <section class="hero"><div class="eyebrow">UMBC CMSC 621 · Group 9</div>
    <h1>ProofPath TrialMatch</h1>
    <p>Inspect how retrieval, explicit eligibility rules, and constrained explanations work together.</p></section>
    <div class="notice"><strong>Educational prototype:</strong> Uses synthetic patients and a cached public-trial dataset. Results cover only encoded criteria and are not clinical eligibility determinations or medical advice.</div>
    """,
    unsafe_allow_html=True,
)

top_left, top_right = st.columns([2.2, 1], gap="large")
with top_left:
    patient_labels = {
        pid: f"{pid} · {title_case(patient['diagnosis']['disease_status'])} · age {patient['age_years']}"
        for pid, patient in PATIENTS_BY_ID.items()
    }
    selected_patient_id = st.selectbox(
        "Synthetic patient case", list(patient_labels), format_func=patient_labels.get,
        help="Eight synthetic profiles are included; no real patient data is used."
    )
with top_right:
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("Use the left sidebar to run what-if changes on selected facts.")

base_patient = PATIENTS_BY_ID[selected_patient_id]
patient, has_edits = edited_patient(base_patient)
ranked_trials = INTEGRATED_BY_ID[selected_patient_id]
profile_col, candidates_col, detail_col = st.columns([0.9, 1.25, 1.65], gap="large")

with profile_col:
    st.subheader("Patient profile")
    if has_edits:
        st.info("What-if edits are active. Symbolic results below have been rerun.")
    profile_rows = {
        "Age": f"{patient['age_years']} years", "Cancer": title_case(patient["diagnosis"]["cancer_type"]),
        "Status": title_case(patient["diagnosis"]["disease_status"]), "Extent": title_case(patient["diagnosis"]["disease_extent"]),
        "Histology": "Confirmed" if patient["diagnosis"]["histologic_confirmation"] else "Not confirmed",
        "Measurable disease": "Yes" if patient["diagnosis"]["measurable_disease"] else "No",
        "ANC": patient["laboratory_values"]["anc_per_ul"], "Platelets": patient["laboratory_values"]["platelets_per_ul"],
        "Hemoglobin": patient["laboratory_values"]["hemoglobin_g_dl"], "GFR": patient["laboratory_values"]["gfr_ml_min_1_73m2"],
        "LVEF": patient["cardiac"]["lvef_percent"],
    }
    profile_frame = pd.DataFrame(profile_rows.items(), columns=["Fact", "Value"])
    profile_frame["Value"] = profile_frame["Value"].map(display_value)
    st.dataframe(profile_frame, hide_index=True, width="stretch")
    with st.expander("View complete synthetic record"):
        st.json(patient, expanded=False)

with candidates_col:
    st.subheader("Retrieved trials")
    st.caption("Top five from the cached TF-IDF V2 retrieval run.")
    trial_options = [item["nct_id"] for item in ranked_trials]
    selected_trial_id = st.selectbox(
        "Inspect candidate", trial_options,
        format_func=lambda nct: f"{nct} · {next(x['title'] for x in ranked_trials if x['nct_id'] == nct)}",
        label_visibility="collapsed"
    )
    for item in ranked_trials:
        label, css_class = status_badge(item["overall_status"])
        selected_class = " selected" if item["nct_id"] == selected_trial_id else ""
        if item["symbolic_available"]:
            counts = (f'<span class="pill met">{item["met_count"]} MET</span>'
                      f'<span class="pill not-met">{item["not_met_count"]} NOT_MET</span>'
                      f'<span class="pill unknown">{item["unknown_count"]} UNKNOWN</span>')
        else:
            counts = '<span class="pill retrieval">No encoded rule set</span>'
        st.markdown(
            f'<div class="trial-card{selected_class}"><div class="trial-rank">Rank {item["rank"]} · score {item["retrieval_score"]:.3f}</div>'
            f'<div class="trial-id">{safe(item["nct_id"])}</div><div class="trial-title">{safe(item["title"])}</div>'
            f'<span class="pill {css_class}">{label}</span>{counts}</div>', unsafe_allow_html=True
        )

selected_ranked = next(item for item in ranked_trials if item["nct_id"] == selected_trial_id)
trial_meta = TRIALS_BY_ID.get(selected_trial_id, {})

with detail_col:
    st.subheader("Assessment and proof")
    st.markdown(f"### {safe(selected_trial_id)}")
    st.caption(selected_ranked["title"])
    if selected_trial_id not in RULES_BY_TRIAL:
        st.warning("This trial was retrieved as potentially relevant, but its criteria have not been encoded and human-reviewed for symbolic evaluation. No match claim is produced.")
        summary_tab, protocol_tab = st.tabs(["Trial summary", "Protocol text"])
        with summary_tab:
            st.write(f"**Recruitment status:** {trial_meta.get('Study Status', 'Not available')}")
            st.write(f"**Phase:** {trial_meta.get('Phase', 'Not available')}")
            st.write(f"**Age range:** {trial_meta.get('Minimum Age', 'N/A')} to {trial_meta.get('Maximum Age', 'N/A')}")
            url = trial_meta.get("Study URL")
            if isinstance(url, str) and url.startswith("http"):
                st.link_button("Open ClinicalTrials.gov record", url)
        with protocol_tab:
            st.text_area("Cached eligibility text", str(trial_meta.get("Full Eligibility Criteria", "Not available")), height=360, disabled=True)
    else:
        evaluation = evaluate_trial(patient, RULES_BY_TRIAL[selected_trial_id])
        status = evaluation["overall_status"]
        label, css_class = status_badge(status)
        st.markdown(
            f'<div class="assessment {css_class}"><strong>{label}: {status}</strong><br>{safe(evaluation["conclusion"])}<br><br>'
            '<small>This result covers the reviewed rules in this prototype, not the complete clinical screening process.</small></div>',
            unsafe_allow_html=True
        )
        met_col, failed_col, unknown_col = st.columns(3)
        met_col.metric("MET", evaluation["met_count"])
        failed_col.metric("NOT_MET", evaluation["not_met_count"])
        unknown_col.metric("UNKNOWN", evaluation["unknown_count"])
        explanation_tab, proof_tab, questions_tab, trial_tab = st.tabs(
            ["Explanation", "Criterion proof", "Missing information", "Trial summary"]
        )
        with explanation_tab:
            verified = VERIFIED_BY_PAIR.get((selected_patient_id, selected_trial_id))
            use_verified = bool(verified and verified["verification_passed"] and not has_edits)
            explanation = verified["llm_explanation"] if use_verified else build_explanation(evaluation)
            st.markdown(f'<div class="explain">{safe(explanation).replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
            note = "✓ Stored LLM explanation passed the project verifier for this unchanged patient-trial pair." if use_verified else "Deterministic explanation generated directly from the current symbolic proof trace."
            st.markdown(f'<div class="source-note">{note}</div>', unsafe_allow_html=True)
        with proof_tab:
            proof = pd.DataFrame(evaluation["rule_results"])[["rule_id", "description", "status", "patient_value", "operator", "expected_value"]]
            proof["patient_value"] = proof["patient_value"].map(display_value)
            proof["expected_value"] = proof["expected_value"].map(display_value)
            proof.columns = ["Rule", "Criterion", "Result", "Patient value", "Operator", "Required value"]
            st.dataframe(proof, hide_index=True, width="stretch", height=min(540, 40 + 35 * len(proof)))
        with questions_tab:
            questions = generate_missing_questions(evaluation["rule_results"])
            if questions:
                st.write("These questions correspond only to criteria currently marked UNKNOWN:")
                for question in questions:
                    st.info(question)
            else:
                st.success("No evaluated criterion is currently UNKNOWN.")
        with trial_tab:
            st.write(f"**Recruitment status:** {trial_meta.get('Study Status', 'Not available')}")
            st.write(f"**Phase:** {trial_meta.get('Phase', 'Not available')}")
            st.write(f"**Conditions:** {trial_meta.get('Conditions', 'Not available')}")
            st.write(f"**Interventions:** {trial_meta.get('Interventions', 'Not available')}")
            url = trial_meta.get("Study URL")
            if isinstance(url, str) and url.startswith("http"):
                st.link_button("Open ClinicalTrials.gov record", url)

st.markdown('<div class="footer-note">ProofPath TrialMatch · Synthetic/public data only · Reproducible cached demo</div>', unsafe_allow_html=True)
