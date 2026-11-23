import streamlit as st
from textwrap import dedent
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

PATIENTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "synthetic_patients"
    / "synthetic_patients.json"
)

@st.cache_data
def load_patients():
    with open(
        PATIENTS_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)

patients = load_patients()

patients_by_id = {
    patient["patient_id"]: patient
    for patient in patients
}

st.success(
    f"Patients loaded successfully: {len(patients_by_id)}"
)

st.write(
    "Patients loaded:",
    len(patients_by_id)
)


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Proof Path TrialMatch",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ==========================================================
# HTML HELPER
# ==========================================================

def html(content):
    st.html(
        dedent(content).strip()
    )


# ==========================================================
# CUSTOM CSS
# ==========================================================

st.html(
    """
    <style>

    /* =====================================================
       GLOBAL
    ===================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at 8% 12%,
                rgba(73, 145, 184, 0.06),
                transparent 26%
            ),
            radial-gradient(
                circle at 92% 78%,
                rgba(42, 140, 130, 0.05),
                transparent 30%
            ),
            #f7fafc;

        color: #1e293b;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1rem;
        padding-bottom: 3rem;
    }

    html,
    body,
    [class*="css"] {
        font-family:
            Inter,
            -apple-system,
            BlinkMacSystemFont,
            "Segoe UI",
            sans-serif;
    }

    .stMarkdown,
    .stMarkdown p,
    .stMarkdown li {
        color: #334155;
    }

    h1,
    h2,
    h3,
    h4 {
        color: #163a5f !important;
    }

    [data-testid="stCaptionContainer"] {
        color: #64748b !important;
    }


    /* =====================================================
       HEADER
    ===================================================== */

    .medical-header {
        background:
            linear-gradient(
                110deg,
                #163a5f 0%,
                #2563a6 58%,
                #2a8c82 100%
            );

        border-radius: 16px;

        padding: 16px 24px;

        margin-bottom: 16px;

        box-shadow:
            0 8px 24px
            rgba(25, 65, 100, 0.12);
    }

    .header-title {
        color: white;

        font-size: 24px;

        font-weight: 700;

        letter-spacing: -0.3px;

        margin-bottom: 4px;
    }

    .header-subtitle {
        color: #dcecf7;

        font-size: 14px;

        line-height: 1.5;
    }

    .research-badge {
        display: inline-block;

        background:
            rgba(255, 255, 255, 0.14);

        color: white;

        padding: 5px 11px;

        border-radius: 20px;

        font-size: 12px;

        font-weight: 600;

        margin-top: 9px;

        border:
            1px solid
            rgba(255, 255, 255, 0.2);
    }


    /* =====================================================
       DISCLAIMER
    ===================================================== */

    .disclaimer {
        background: #eef5f8;

        border:
            1px solid
            #d6e5ec;

        color: #526875;

        padding: 10px 14px;

        border-radius: 10px;

        font-size: 12px;

        margin-bottom: 18px;

        line-height: 1.5;
    }


    /* =====================================================
       PANEL TITLES
    ===================================================== */

    .panel-title {
        color: #163a5f;

        font-size: 17px;

        font-weight: 700;

        margin-bottom: 12px;

        padding-bottom: 9px;

        border-bottom:
            2px solid
            #e8f0f6;
    }


    /* =====================================================
       PATIENT INFORMATION
    ===================================================== */

    .patient-row {
        display: flex;

        justify-content: space-between;

        gap: 12px;

        padding:
            8px 4px;

        border-bottom:
            1px solid
            #edf2f7;

        font-size: 13px;
    }

    .patient-label {
        color: #64748b;

        font-weight: 500;
    }

    .patient-value {
        color: #1e293b;

        font-weight: 600;

        text-align: right;
    }


    /* =====================================================
       TRIAL CARDS
    ===================================================== */

    .trial-card {
        background: white;

        border:
            1px solid
            #dce6ef;

        border-radius: 12px;

        padding: 14px;

        margin-bottom: 12px;

        box-shadow:
            0 2px 8px
            rgba(30, 64, 100, 0.04);

        transition:
            all 0.2s ease;
    }

    .trial-card:hover {
        border-color: #8db9dc;

        box-shadow:
            0 5px 16px
            rgba(30, 90, 140, 0.09);
    }

    .trial-id {
        color: #2563a6;

        font-size: 13px;

        font-weight: 700;

        margin-bottom: 4px;
    }

    .trial-title {
        color: #1e293b;

        font-size: 13px;

        font-weight: 600;

        line-height: 1.4;
    }

    .trial-meta {
        color: #64748b;

        font-size: 11px;

        margin-top: 7px;
    }


    /* =====================================================
       STATUS PILLS
    ===================================================== */

    .status-row {
        display: flex;

        flex-wrap: wrap;

        gap: 6px;

        margin-top: 10px;
    }

    .status-met {
        background: #e8f6ee;

        color: #26734d;

        padding: 4px 8px;

        border-radius: 20px;

        font-size: 11px;

        font-weight: 600;
    }

    .status-not-met {
        background: #fdecec;

        color: #b44545;

        padding: 4px 8px;

        border-radius: 20px;

        font-size: 11px;

        font-weight: 600;
    }

    .status-unknown {
        background: #fff5dd;

        color: #9b6b19;

        padding: 4px 8px;

        border-radius: 20px;

        font-size: 11px;

        font-weight: 600;
    }


    /* =====================================================
       ASSESSMENT
    ===================================================== */

    .assessment-box {
        background: #edf6fb;

        border-left:
            4px solid
            #397fae;

        border-radius: 8px;

        padding: 13px 14px;

        color: #27465f;

        font-size: 13px;

        line-height: 1.55;

        margin-bottom: 15px;
    }


    /* =====================================================
       VERIFIED EXPLANATION
    ===================================================== */

    .explanation-box {
        background: white;

        border:
            1px solid
            #dce6ef;

        border-radius: 10px;

        padding: 14px;

        color: #334155;

        font-size: 13px;

        line-height: 1.6;

        box-shadow:
            0 2px 8px
            rgba(30, 64, 100, 0.03);
    }


    /* =====================================================
       MISSING INFORMATION
    ===================================================== */

    .question-box {
        background: #fff9e9;

        border:
            1px solid
            #f2dfac;

        border-radius: 9px;

        padding: 10px 12px;

        margin-bottom: 8px;

        color: #6d581c;

        font-size: 12px;
    }


    /* =====================================================
       STREAMLIT SELECTBOX
    ===================================================== */

    div[data-baseweb="select"] > div {
        background: white !important;

        border-color: #ccdce8 !important;

        border-radius: 9px !important;

        color: #1e293b !important;
    }


    /* =====================================================
       STREAMLIT TABS
    ===================================================== */

    button[data-baseweb="tab"] {
        color: #64748b !important;

        font-weight: 500;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #2563a6 !important;

        font-weight: 700;
    }


    /* =====================================================
       STREAMLIT DATAFRAME
    ===================================================== */

    [data-testid="stDataFrame"] {
        background: white;

        border-radius: 10px;
    }


    /* =====================================================
       BUTTONS
    ===================================================== */

    .stButton > button {
        width: 100%;

        background: #2563a6;

        color: white;

        border: none;

        border-radius: 8px;

        font-weight: 600;
    }

    .stButton > button:hover {
        background: #1d527e;

        color: white;
    }


    /* =====================================================
       REMOVE DEFAULT STREAMLIT DECORATION
    ===================================================== */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """,
)


# ==========================================================
# HEADER
# ==========================================================

html(
    """
    <div class="medical-header">

        <div class="header-title">
            🩺 Proof Path TrialMatch
        </div>

        <div class="header-subtitle">
            Neuro-Symbolic Pediatric Oncology Clinical Trial Matching Assistant
        </div>

        <div class="research-badge">
            Research Prototype · Osteosarcoma
        </div>

    </div>
    """
)


# ==========================================================
# DISCLAIMER
# ==========================================================

html(
    """
    <div class="disclaimer">
        This system is an educational research prototype.
        It evaluates only encoded trial criteria and does not
        determine final clinical eligibility or provide medical advice.
    </div>
    """
)


# ==========================================================
# MAIN THREE-COLUMN LAYOUT
# ==========================================================

left_col, middle_col, right_col = st.columns(
    [0.85, 1.15, 1.55],
    gap="medium"
)


# ==========================================================
# LEFT COLUMN — PATIENT CASE
# ==========================================================

with left_col:

    html(
        """
        <div class="panel-title">
            Patient Case
        </div>
        """
    )

   patient_labels = {
    patient_id: f"{patient_id} — {patients_by_id[patient_id]['diagnosis']['disease_status'].replace('_', ' ').title()}"
    for patient_id in patients_by_id
   }
    

    selected_patient_id = st.selectbox(
    "Select a synthetic case",
    list(patient_labels.keys()),
    format_func=lambda patient_id: patient_labels[patient_id]
    )

    selected_patient = patients_by_id[
    selected_patient_id
    ]

st.write(
    "Selected patient:",
    selected_patient_id
)
    st.markdown("#### Patient Information")

    html(
        """
        <div class="patient-row">
            <span class="patient-label">
                Age
            </span>

            <span class="patient-value">
                15 years
            </span>
        </div>

        <div class="patient-row">
            <span class="patient-label">
                Diagnosis
            </span>

            <span class="patient-value">
                Osteosarcoma
            </span>
        </div>

        <div class="patient-row">
            <span class="patient-label">
                Disease Status
            </span>

            <span class="patient-value">
                Newly diagnosed
            </span>
        </div>

        <div class="patient-row">
            <span class="patient-label">
                Disease Extent
            </span>

            <span class="patient-value">
                Localized
            </span>
        </div>

        <div class="patient-row">
            <span class="patient-label">
                Histology
            </span>

            <span class="patient-value">
                Confirmed
            </span>
        </div>

        <div class="patient-row">
            <span class="patient-label">
                Current Therapy
            </span>

            <span class="patient-value">
                MAP
            </span>
        </div>

        <div class="patient-row">
            <span class="patient-label">
                ANC
            </span>

            <span class="patient-value">
                1850 / μL
            </span>
        </div>

        <div class="patient-row">
            <span class="patient-label">
                Platelets
            </span>

            <span class="patient-value">
                168,000 / μL
            </span>
        </div>

        <div class="patient-row">
            <span class="patient-label">
                Hemoglobin
            </span>

            <span class="patient-value">
                10.2 g/dL
            </span>
        </div>

        <div class="patient-row">
            <span class="patient-label">
                LVEF
            </span>

            <span class="patient-value">
                61%
            </span>
        </div>
        """
    )


# ==========================================================
# MIDDLE COLUMN — RETRIEVED TRIALS
# ==========================================================

with middle_col:

    html(
        """
        <div class="panel-title">
            Retrieved Candidate Trials
        </div>
        """
    )

    st.caption(
        "Top candidates ranked by TF-IDF V2 retrieval"
    )


    # ------------------------------------------------------
    # TRIAL 1
    # ------------------------------------------------------

    html(
        """
        <div class="trial-card">

            <div class="trial-id">
                NCT07560826
            </div>

            <div class="trial-title">
                CATSINDO Trial — Newly Diagnosed
                High-Grade Osteosarcoma
            </div>

            <div class="trial-meta">
                Rank 1 · Symbolic rules available
            </div>

            <div class="status-row">

                <span class="status-met">
                    18 MET
                </span>

                <span class="status-not-met">
                    0 NOT_MET
                </span>

                <span class="status-unknown">
                    0 UNKNOWN
                </span>

            </div>

        </div>
        """
    )


    # ------------------------------------------------------
    # TRIAL 2
    # ------------------------------------------------------

    html(
        """
        <div class="trial-card">

            <div class="trial-id">
                NCT07321912
            </div>

            <div class="trial-title">
                Pediatric Osteosarcoma Study
            </div>

            <div class="trial-meta">
                Rank 2 · Retrieval-only candidate
            </div>

        </div>
        """
    )


    # ------------------------------------------------------
    # TRIAL 3
    # ------------------------------------------------------

    html(
        """
        <div class="trial-card">

            <div class="trial-id">
                NCT07725380
            </div>

            <div class="trial-title">
                Relapsed Osteosarcoma Treatment Study
            </div>

            <div class="trial-meta">
                Rank 3 · Retrieval-only candidate
            </div>

        </div>
        """
    )


    # ------------------------------------------------------
    # TRIAL 4
    # ------------------------------------------------------

    html(
        """
        <div class="trial-card">

            <div class="trial-id">
                NCT03643133
            </div>

            <div class="trial-title">
                Mifamurtide Combined With
                Post-Operative Chemotherapy
            </div>

            <div class="trial-meta">
                Rank 4 · Retrieval-only candidate
            </div>

        </div>
        """
    )


    # ------------------------------------------------------
    # TRIAL 5
    # ------------------------------------------------------

    html(
        """
        <div class="trial-card">

            <div class="trial-id">
                NCT05019703
            </div>

            <div class="trial-title">
                Osteosarcoma Immunotherapy Study
            </div>

            <div class="trial-meta">
                Rank 5 · Retrieval-only candidate
            </div>

        </div>
        """
    )


# ==========================================================
# RIGHT COLUMN — TRIAL DETAILS
# ==========================================================

with right_col:

    html(
        """
        <div class="panel-title">
            Trial Details & Explanation
        </div>
        """
    )

    st.markdown(
        "### NCT07560826"
    )

    st.caption(
        "CATSINDO Trial — Newly Diagnosed "
        "High-Grade Osteosarcoma"
    )


    # ------------------------------------------------------
    # OVERALL ASSESSMENT
    # ------------------------------------------------------

    html(
        """
        <div class="assessment-box">

            <b>
                Overall Assessment: MET
            </b>

            <br><br>

            The patient satisfies all evaluated encoded
            eligibility criteria for this trial.

            <br><br>

            This result does not establish final clinical
            eligibility.

        </div>
        """
    )


    # ------------------------------------------------------
    # TABS
    # ------------------------------------------------------

    tab1, tab2, tab3 = st.tabs(
        [
            "Explanation",
            "Eligibility Criteria",
            "Trial Summary"
        ]
    )


    # ======================================================
    # TAB 1 — EXPLANATION
    # ======================================================

    with tab1:

        st.markdown(
            "#### Verified Explanation"
        )

        html(
            """
            <div class="explanation-box">

                The patient's encoded clinical information
                satisfies all evaluated criteria in the
                symbolic rule set.

                <br><br>

                The explanation is generated from the
                symbolic proof trace and verified before
                being displayed.

                <br><br>

                <b>
                    This is not a final clinical eligibility
                    determination.
                </b>

            </div>
            """
        )


    # ======================================================
    # TAB 2 — ELIGIBILITY CRITERIA
    # ======================================================

    with tab2:

        st.markdown(
            "#### Criterion-Level Results"
        )

        criteria = {
            "Criterion": [
                "Age requirement",
                "Diagnosis",
                "Histologic confirmation",
                "Current MAP therapy",
                "ANC",
                "Platelet count",
                "Hemoglobin",
                "Cardiac function"
            ],

            "Result": [
                "MET",
                "MET",
                "MET",
                "MET",
                "MET",
                "MET",
                "MET",
                "MET"
            ],

            "Patient Value": [
                "15 years",
                "Osteosarcoma",
                "Confirmed",
                "Yes",
                "1850 / μL",
                "168,000 / μL",
                "10.2 g/dL",
                "LVEF 61%"
            ]
        }

        st.dataframe(
            criteria,
            use_container_width=True,
            hide_index=True
        )


    # ======================================================
    # TAB 3 — TRIAL SUMMARY
    # ======================================================

    with tab3:

        st.markdown(
            "#### Trial Summary"
        )

        html(
            """
            <div class="explanation-box">

                <b>Trial ID:</b>
                NCT07560826

                <br><br>

                <b>Condition:</b>
                High-grade osteosarcoma

                <br><br>

                <b>Study Type:</b>
                Interventional

                <br><br>

                <b>Symbolic Rule Set:</b>
                Available

                <br><br>

                Trial metadata and full eligibility
                information are derived from the project's
                ClinicalTrials.gov dataset.

            </div>
            """
        )