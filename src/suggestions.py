from typing import Dict, List


def generate_suggestions(missing: List[str], sections: Dict[str, str]) -> List[str]:
    tips = []

    # Missing skills-based tips
    if missing:
        top_missing = missing[:8]
        tips.append(
            "Add or highlight these missing keywords (if you truly have them): "
            + ", ".join(top_missing)
        )
        tips.append("If you don't have some missing skills, build a small project to demonstrate them.")
    else:
        tips.append("Good coverage of JD skills. Focus on stronger impact statements and metrics.")

    # Section quality tips
    if not sections.get("projects", "").strip():
        tips.append("Add a Projects section with 2–3 projects, each with tech stack + measurable results.")
    if not sections.get("experience", "").strip():
        tips.append("Add an Experience section (internship/freelance/volunteer) or describe relevant work-like tasks.")
    if not sections.get("skills", "").strip():
        tips.append("Add a Skills section grouped by categories (Languages, Frameworks, Tools, Cloud).")

    # General resume tips
    tips.append("Use numbers: latency reduced by X%, accuracy improved by Y%, users served, requests/sec, etc.")
    tips.append("Mirror the job description language (same keywords) but keep it honest.")
    tips.append("Keep bullets action-driven: Built / Designed / Deployed / Optimized / Automated…")

    return tips
