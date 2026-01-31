import json
import pandas as pd
import streamlit as st
from datetime import datetime

from src.pdf_utils import extract_text_from_pdf
from src.sections import split_sections
from src.highlight import highlight_terms
from src.suggestions import generate_suggestions

from src.ranking import score_resume_against_jd
from src.ui_style import inject_css
from src.ui_components import brandbar, pill, pill_html, kpis, softline, chips
from src.pdf_export import generate_ats_pdf_report


st.set_page_config(page_title="TalentRank — ATS AI Screening", page_icon="", layout="wide")
inject_css()
brandbar(
    app_name="TalentRank — AI Resume Screening",
    tagline="Semantic matching • Skill coverage • Robust ranking • Explainable decisions"
)

# ---------------- Sidebar ----------------
st.sidebar.header("Scoring Controls")

w_kw = st.sidebar.slider("Keyword Relevance (TF-IDF)", 0.0, 1.0, 0.20, 0.05,
                         help="Exact keyword overlap with the job description.")
w_sem = st.sidebar.slider("Semantic Match (SBERT)", 0.0, 1.0, 0.65, 0.05,
                          help="Meaning-based match using transformer embeddings.")
w_skill = st.sidebar.slider("Skill Coverage", 0.0, 1.0, 0.15, 0.05,
                            help="How many JD skills are explicitly present in the resume.")

s = w_kw + w_sem + w_skill
weights = (0.20, 0.65, 0.15) if s == 0 else (w_kw / s, w_sem / s, w_skill / s)
st.sidebar.caption(f"**Normalized:** KW={weights[0]:.2f} • SEM={weights[1]:.2f} • SKILL={weights[2]:.2f}")

mode = st.sidebar.radio("**Mode**", ["Batch Rank (ATS)", "Single Resume"], index=0)
top_k = st.sidebar.slider("**Top K (Batch)**", 1, 30, 10, 1)

st.sidebar.divider()
st.sidebar.caption("💡 **Tip:** For HR-style ranking, keep Semantic high (0.6–0.75).")


# Responsive layout
col_left, col_right = st.columns([1, 1], gap="small")

with col_left:
    st.subheader("Input")
    st.caption("Paste job description and upload resumes for scoring")
    softline()
    
    jd_text = st.text_area("Paste Job Description", height=200, placeholder="Paste the job description here...")

    if mode == "Batch Rank (ATS)":
        resume_files = st.file_uploader("Upload Multiple Resumes (PDF)", type=["pdf"], accept_multiple_files=True)
    else:
        resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

    st.write("")  # spacing
    c1, c2 = st.columns(2, gap="small")
    with c1:
        run_btn = st.button("Run Screening", use_container_width=True)
    with c2:
        clear_btn = st.button("Clear All", use_container_width=True)

with col_right:
    st.subheader("Results")
    st.caption("Screening results and candidate analysis")
    softline()

if clear_btn:
    st.session_state.clear()
    st.rerun()


def _ensure_jd():
    if not jd_text.strip():
        st.error("Please paste the job description.")
        st.stop()


def _render_pipeline_summary(results_sorted):
    shortlisted = sum(r.decision == "SHORTLIST" for r in results_sorted)
    review = sum(r.decision == "REVIEW" for r in results_sorted)
    reject = sum(r.decision == "REJECT" for r in results_sorted)

    st.write("")  # spacing
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    with col1:
        st.metric("Candidates", len(results_sorted))
    with col2:
        st.metric("SHORTLIST", shortlisted)
    with col3:
        st.metric("⚙️ REVIEW", review)
    with col4:
        st.metric("REJECT", reject)
    st.write("")  # spacing


def _make_leaderboard_df(results_sorted):
    rows = []
    for rank, r in enumerate(results_sorted, start=1):
        rows.append({
            "Rank": rank,
            "Candidate": r.filename,
            "Decision": r.decision,
            "Overall %": round(r.overall * 100, 2),
            "Semantic %": round(r.sbert * 100, 2),
            "Keyword %": round(r.tfidf * 100, 2),
            "Skill %": round(r.skill_overlap * 100, 2),
            "Missing (preview)": ", ".join(r.missing[:8]) + (" ..." if len(r.missing) > 8 else ""),
        })
    return pd.DataFrame(rows)


# Initialize session state
if "results_sorted" not in st.session_state:
    st.session_state.results_sorted = []
if "jd_skills" not in st.session_state:
    st.session_state.jd_skills = []
if "jd_text" not in st.session_state:
    st.session_state.jd_text = ""


if run_btn:
    _ensure_jd()

    if mode == "Batch Rank (ATS)":
        if not resume_files:
            st.error("Please upload at least one resume PDF.")
            st.stop()

        results = []
        for f in resume_files:
            resume_text = extract_text_from_pdf(f)
            results.append(score_resume_against_jd(resume_text, jd_text, f.name, weights))

        results_sorted = sorted(results, key=lambda x: x.overall, reverse=True)

        st.session_state.results_sorted = results_sorted
        st.session_state.jd_skills = results_sorted[0].jd_skills if results_sorted else []
        st.session_state.jd_text = jd_text

    else:
        if not resume_file:
            st.error("Please upload a resume PDF.")
            st.stop()

        resume_text = extract_text_from_pdf(resume_file)
        result = score_resume_against_jd(resume_text, jd_text, resume_file.name, weights)

        st.session_state.results_sorted = [result]
        st.session_state.jd_skills = result.jd_skills
        st.session_state.jd_text = jd_text


# ---------------- Render Tabs ----------------
results_sorted = st.session_state.results_sorted
jd_skills_global = st.session_state.jd_skills
jd_text_global = st.session_state.jd_text

with col_right:
    tabs = st.tabs(["Screening", "Candidate View", "Exports", "Evaluation"])
    
    # -------- Screening Tab --------
    with tabs[0]:
        st.subheader("Screening Pipeline")
        if not results_sorted:
            st.info("Run screening to see ranked results")
        else:
            st.caption("Automated ATS ranking with explainable scores")
            softline()
            
            _render_pipeline_summary(results_sorted)
            softline()

            df = _make_leaderboard_df(results_sorted)
            st.dataframe(df.head(top_k), use_container_width=True, hide_index=True)

            st.caption("Overall = weighted ensemble of Keyword + Semantic + Skill coverage (with robustness adjustments).")

    # -------- Candidate View Tab --------
    with tabs[1]:
        st.subheader("Candidate Drill-down")
        if not results_sorted:
            st.info("Run screening first to view candidate details")
        else:
            # pick candidate
            filenames = [r.filename for r in results_sorted]
            selected = st.selectbox("Select Candidate", filenames, index=0, label_visibility="collapsed")

            chosen = next(r for r in results_sorted if r.filename == selected)
            
            softline()
            col1, col2 = st.columns([1, 0.3], gap="small")
            with col1:
                st.markdown(f"### {chosen.filename}")
            with col2:
                pill(chosen.decision)

            softline()
            st.write("")  # spacing
            col1, col2, col3, col4 = st.columns(4, gap="medium")
            with col1:
                st.metric("Overall", f"{chosen.overall*100:.1f}%", label_visibility="visible")
            with col2:
                st.metric("Semantic", f"{chosen.sbert*100:.1f}%", label_visibility="visible")
            with col3:
                st.metric("Keyword", f"{chosen.tfidf*100:.1f}%", label_visibility="visible")
            with col4:
                st.metric("Skill", f"{chosen.skill_overlap*100:.1f}%", label_visibility="visible")
            
            st.write("")  # spacing
            st.progress(min(max(chosen.overall, 0.0), 1.0))
            softline()

            # Skill gaps
            st.markdown("#### 📚 Skill Assessment")
            if chosen.missing:
                st.write("**Missing skills:**")
                chips(chosen.missing)
            else:
                st.success("All required skills detected!")

            st.info("For detailed section suggestions + highlights, use Single Resume mode (keeps resume text in memory).")

    # -------- Exports Tab --------
    with tabs[2]:
        st.subheader("Export Center")
        if not results_sorted:
            st.info("Run screening first to export results")
        else:
            st.caption("Download ATS reports in professional formats for your hiring workflow")
            softline()
            
            df = _make_leaderboard_df(results_sorted)

            # Generate PDF report
            pdf_data = generate_ats_pdf_report(results_sorted, jd_skills_global, mode, weights)
            
            # Generate template-ready JSON
            shortlist_count = sum(1 for r in results_sorted if r.decision == "SHORTLIST")
            review_count = sum(1 for r in results_sorted if r.decision == "REVIEW")
            reject_count = sum(1 for r in results_sorted if r.decision == "REJECT")
            avg_score = sum(r.overall for r in results_sorted) / len(results_sorted) if results_sorted else 0
            
            json_payload = {
                "template_id": "canva_ats_screening_report_v1",
                "brand": {
                    "product_name": "TalentRank",
                    "report_type": "AI Resume Screening System",
                    "primary_color": "#7C5CFC",
                    "secondary_color": "#1B2559",
                    "font_heading": "Poppins",
                    "font_body": "Inter"
                },
                "meta": {
                    "title": "ATS Screening Results",
                    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "mode": mode,
                    "total_candidates": len(results_sorted)
                },
                "executive_summary": {
                    "summary_text": "Automated ATS ranking using semantic matching, keyword relevance, and skill coverage. Results are explainable and exportable for HR review.",
                    "kpis": [
                        {"label": "Total Candidates", "value": len(results_sorted)},
                        {"label": "Shortlisted", "value": shortlist_count},
                        {"label": "Average Score", "value": f"{avg_score*100:.1f}%"}
                    ],
                    "weights": {
                        "keyword_tfidf": f"{weights[0]:.0%}",
                        "semantic_sbert": f"{weights[1]:.0%}",
                        "skill_coverage": f"{weights[2]:.0%}"
                    }
                },
                "required_skills": {
                    "title": "Required Skills",
                    "items": jd_skills_global if jd_skills_global else []
                },
                "ranking_results": {
                    "title": "Candidate Ranking Results",
                    "table": {
                        "columns": ["Rank", "Filename", "Decision", "Overall", "Semantic", "Keyword", "Skill"],
                        "rows": [
                            [idx, r.filename, r.decision, f"{r.overall*100:.1f}%", f"{r.sbert*100:.1f}%", f"{r.tfidf*100:.1f}%", f"{r.skill_overlap*100:.1f}%"]
                            for idx, r in enumerate(results_sorted, 1)
                        ]
                    }
                },
                "decision_breakdown": {
                    "title": "Decision Breakdown",
                    "items": [
                        {"label": "SHORTLIST", "count": shortlist_count, "percent": f"{shortlist_count/len(results_sorted)*100:.1f}%", "priority_label": "High Priority"},
                        {"label": "REVIEW", "count": review_count, "percent": f"{review_count/len(results_sorted)*100:.1f}%", "priority_label": "Moderate Priority"},
                        {"label": "REJECT", "count": reject_count, "percent": f"{reject_count/len(results_sorted)*100:.1f}%", "priority_label": "Not Qualified"}
                    ]
                },
                "insights": {
                    "title": "Key Insights",
                    "bullets": [
                        f"Top candidate: {results_sorted[0].filename} ({results_sorted[0].overall*100:.1f}%)",
                        f"Shortlist: {shortlist_count} candidates | Review: {review_count} candidates | Reject: {reject_count} candidates",
                        f"Weights: Keyword {weights[0]:.0%} | Semantic {weights[1]:.0%} | Skill {weights[2]:.0%}"
                    ]
                },
                "footer": {
                    "note": "Generated by TalentRank AI Resume Screening System",
                    "audit_line": "For hiring transparency and audit trail.",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }

            col1, col2 = st.columns(2, gap="small")
            
            with col1:
                st.download_button(
                    "Professional Report (PDF)",
                    data=pdf_data,
                    file_name="ats_report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

            with col2:
                st.download_button(
                    "Leaderboard (CSV)",
                    data=df.to_csv(index=False).encode("utf-8"),
                    file_name="ats_leaderboard.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            st.caption("PDF for hiring notes, interviews, and candidate feedback.")

    # -------- Evaluation Tab (V9.1: PDF-based evaluation) --------
    with tabs[3]:
        with st.container(border=True):
            st.subheader("Evaluation Dashboard (Offline Metrics)")
            st.caption("Prove ranking quality using Precision@K and NDCG@K — perfect for interviews.")

            jd_eval = st.text_area("Paste Job Description for evaluation", height=160, placeholder="Paste JD here...")

            eval_files = st.file_uploader(
                "Upload labeled resumes (PDF) for evaluation",
                type=["pdf"],
                accept_multiple_files=True,
                key="eval_uploader"
            )

            st.markdown("### Label each resume")
            st.caption("Label meanings: 2 = Good fit, 1 = OK fit, 0 = Bad fit")

            labels = {}
            if eval_files:
                for f in eval_files:
                    labels[f.name] = st.selectbox(
                        f"Label for {f.name}",
                        options=[2, 1, 0],
                        index=1,
                        key=f"label_{f.name}"
                    )

            run_eval = st.button("Run Evaluation", use_container_width=True)

            if run_eval:
                if not jd_eval.strip():
                    st.error("Please paste the evaluation Job Description.")
                    st.stop()
                if not eval_files:
                    st.error("Please upload at least 3 labeled resumes for evaluation.")
                    st.stop()

                from src.pdf_utils import extract_text_from_pdf
                from src.eval_experiment import EvalItem, compare_models

                items = []
                for f in eval_files:
                    text = extract_text_from_pdf(f)
                    items.append(EvalItem(filename=f.name, text=text, label=int(labels[f.name])))

                with st.spinner("Scoring resumes and computing metrics..."):
                    df_metrics, leaderboards = compare_models(jd_eval, items, ensemble_weights=weights, k_values=(3, 5, 10))

                st.markdown("## Metrics Comparison (4 Models)")
                st.dataframe(df_metrics, use_container_width=True, hide_index=True)

                st.download_button(
                    "Download Metrics CSV",
                    data=df_metrics.to_csv(index=False).encode("utf-8"),
                    file_name="talentrank_eval_metrics.csv",
                    mime="text/csv",
                    use_container_width=True
                )

                st.markdown("## Leaderboards (per model)")
                model_choice = st.selectbox("Select model leaderboard", list(leaderboards.keys()))
                st.dataframe(leaderboards[model_choice], use_container_width=True, hide_index=True)

                st.success("Evaluation complete! Use these metrics in your README and interviews.")
