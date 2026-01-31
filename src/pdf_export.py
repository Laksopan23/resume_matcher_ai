from fpdf import FPDF
from datetime import datetime

def generate_ats_pdf_report(results_sorted, jd_skills, mode, weights, top_n=10, brand_name="TalentRank"):
    """
    Canva-style template PDF:
    - Title
    - Executive Summary (Total Candidates / Shortlist / Average Score)
    - Required Skills
    - Ranking Results Table
    - Decision Breakdown (with priority labels)
    - Key Insights
    - Footer
    """

    # ---- Helpers ----
    def pct(x):
        return f"{x*100:.1f}%"

    def safe_div(a, b):
        return (a / b) if b else 0

    def ellipsize(text, n=18):
        text = text or ""
        return text if len(text) <= n else text[: max(0, n-3)] + "..."

    # ---- PDF init ----
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()

    # Page layout constants
    left = 12
    top = 12
    content_w = 210 - 2*left  # A4 width 210mm minus margins
    purple = (124, 92, 252)
    dark = (25, 25, 80)
    gray = (90, 90, 90)
    light_bg = (240, 235, 255)
    border = (200, 180, 255)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ---- KPIs ----
    total = len(results_sorted)
    shortlist_count = sum(1 for r in results_sorted if r.decision == "SHORTLIST")
    review_count = sum(1 for r in results_sorted if r.decision == "REVIEW")
    reject_count = sum(1 for r in results_sorted if r.decision == "REJECT")
    avg_score = (sum(r.overall for r in results_sorted) / total) if total else 0

    # ---- Branding header ----
    pdf.set_xy(left, top)
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(*purple)
    pdf.cell(0, 5, brand_name, ln=True)

    pdf.set_x(left)
    pdf.set_font("Arial", size=8)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 4, "AI Resume Screening System", ln=True)
    pdf.ln(2)

    # ---- Main title ----
    pdf.set_x(left)
    pdf.set_font("Arial", "B", size=26)
    pdf.set_text_color(*dark)
    pdf.cell(0, 10, "ATS Screening Results", ln=True)
    pdf.ln(2)

    # ---- Executive Summary Box ----
    box_h = 26
    box_y = pdf.get_y()
    pdf.set_fill_color(*light_bg)
    pdf.set_draw_color(*border)
    pdf.set_line_width(0.3)
    pdf.rect(left, box_y, content_w, box_h, style="FD")

    pdf.set_xy(left + 4, box_y + 3)
    pdf.set_font("Arial", "B", size=11)
    pdf.set_text_color(*dark)
    pdf.cell(0, 6, "Executive Summary", ln=True)

    # Left side labels
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(*gray)

    label_x = left + 6
    val_x = left + content_w - 35  # right aligned values
    row1_y = box_y + 11

    pdf.set_xy(label_x, row1_y)
    pdf.cell(60, 5, "Total Candidates")
    pdf.set_text_color(*purple)
    pdf.set_font("Arial", "B", size=11)
    pdf.set_xy(val_x, row1_y)
    pdf.cell(25, 5, str(total), align="R")

    pdf.set_font("Arial", size=10)
    pdf.set_text_color(*gray)
    pdf.set_xy(label_x, row1_y + 6)
    pdf.cell(60, 5, "Shortlist")
    pdf.set_text_color(46, 204, 113)
    pdf.set_font("Arial", "B", size=11)
    pdf.set_xy(val_x, row1_y + 6)
    pdf.cell(25, 5, str(shortlist_count), align="R")

    pdf.set_font("Arial", size=10)
    pdf.set_text_color(*gray)
    pdf.set_xy(label_x, row1_y + 12)
    pdf.cell(60, 5, "Average Score")
    pdf.set_text_color(*purple)
    pdf.set_font("Arial", "B", size=11)
    pdf.set_xy(val_x, row1_y + 12)
    pdf.cell(25, 5, pct(avg_score), align="R")

    pdf.set_y(box_y + box_h + 6)

    # ---- Required Skills ----
    if jd_skills:
        pdf.set_x(left)
        pdf.set_font("Arial", "B", size=12)
        pdf.set_text_color(*dark)
        pdf.cell(0, 6, "Required Skills", ln=True)

        pdf.set_x(left)
        pdf.set_font("Arial", size=9)
        pdf.set_text_color(*gray)

        max_skills = 26
        skills_text = ", ".join(jd_skills[:max_skills])
        if len(jd_skills) > max_skills:
            skills_text += f", +{len(jd_skills) - max_skills} more"

        pdf.multi_cell(0, 5, skills_text)
        pdf.ln(3)

    # ---- Ranking Results ----
    pdf.set_x(left)
    pdf.set_font("Arial", "B", size=12)
    pdf.set_text_color(*dark)
    pdf.cell(0, 6, "Candidate Ranking Results", ln=True)
    pdf.ln(1)

    # Table header
    headers = ["Rank", "Filename", "Decision", "Overall", "Semantic", "Keyword", "Skill"]
    col_w = [10, 42, 22, 18, 18, 18, 16]  # total ~144; fits well
    row_h = 7

    pdf.set_font("Arial", "B", size=9)
    pdf.set_fill_color(*border)
    pdf.set_text_color(255, 255, 255)

    for i, h in enumerate(headers):
        pdf.cell(col_w[i], row_h, h, border=1, align="C", fill=True)
    pdf.ln()

    # Table rows
    pdf.set_font("Arial", size=9)
    pdf.set_text_color(20, 20, 20)

    shown = results_sorted[:top_n]
    for i, r in enumerate(shown, start=1):
        fill = (245, 240, 255) if (i % 2 == 0) else (255, 255, 255)
        pdf.set_fill_color(*fill)

        pdf.cell(col_w[0], row_h, str(i), border=1, align="C", fill=True)
        pdf.cell(col_w[1], row_h, ellipsize(r.filename, 20), border=1, align="L", fill=True)
        pdf.cell(col_w[2], row_h, r.decision, border=1, align="C", fill=True)
        pdf.cell(col_w[3], row_h, pct(r.overall), border=1, align="C", fill=True)
        pdf.cell(col_w[4], row_h, pct(r.sbert), border=1, align="C", fill=True)
        pdf.cell(col_w[5], row_h, pct(r.tfidf), border=1, align="C", fill=True)
        pdf.cell(col_w[6], row_h, pct(r.skill_overlap), border=1, align="C", fill=True)
        pdf.ln()

    if total > top_n:
        pdf.set_font("Arial", "I", size=8)
        pdf.set_text_color(140, 140, 140)
        pdf.cell(0, 5, f"... and {total - top_n} more candidates", ln=True)
        pdf.ln(2)
    else:
        pdf.ln(2)

    # ---- Decision Breakdown Box ----
    box_h = 24
    box_y = pdf.get_y()
    pdf.set_fill_color(*light_bg)
    pdf.set_draw_color(*border)
    pdf.set_line_width(0.3)
    pdf.rect(left, box_y, content_w, box_h, style="FD")

    pdf.set_xy(left + 4, box_y + 3)
    pdf.set_font("Arial", "B", size=12)
    pdf.set_text_color(*dark)
    pdf.cell(0, 6, "Decision Breakdown", ln=True)

    pdf.set_font("Arial", size=10)
    pdf.set_text_color(60, 60, 60)

    base_y = box_y + 11
    pct_short = pct(safe_div(shortlist_count, total))
    pct_rev = pct(safe_div(review_count, total))
    pct_rej = pct(safe_div(reject_count, total))

    pdf.set_xy(left + 6, base_y)
    pdf.cell(80, 5, f"SHORTLIST: {shortlist_count} ({pct_short})")
    pdf.set_text_color(46, 204, 113)
    pdf.set_xy(left + content_w - 55, base_y)
    pdf.cell(50, 5, "High Priority", align="R")

    pdf.set_text_color(60, 60, 60)
    pdf.set_xy(left + 6, base_y + 6)
    pdf.cell(80, 5, f"REVIEW: {review_count} ({pct_rev})")
    pdf.set_text_color(241, 196, 15)
    pdf.set_xy(left + content_w - 55, base_y + 6)
    pdf.cell(50, 5, "Moderate Priority", align="R")

    pdf.set_text_color(60, 60, 60)
    pdf.set_xy(left + 6, base_y + 12)
    pdf.cell(80, 5, f"REJECT: {reject_count} ({pct_rej})")
    pdf.set_text_color(231, 76, 60)
    pdf.set_xy(left + content_w - 55, base_y + 12)
    pdf.cell(50, 5, "Not Qualified", align="R")

    pdf.set_y(box_y + box_h + 6)

    # ---- Key Insights ----
    pdf.set_x(left)
    pdf.set_font("Arial", "B", size=12)
    pdf.set_text_color(*dark)
    pdf.cell(0, 6, "Key Insights", ln=True)

    pdf.set_font("Arial", size=10)
    pdf.set_text_color(*gray)

    if total:
        top_candidate = results_sorted[0]
        pdf.cell(0, 5, f"- Top candidate: {top_candidate.filename} ({pct(top_candidate.overall)})", ln=True)

        if shortlist_count == 0:
            pdf.cell(0, 5, "- No candidates met shortlist threshold - consider adjusting weights or thresholds.", ln=True)
        else:
            pdf.cell(0, 5, f"- {shortlist_count} candidates ready for interview shortlisting.", ln=True)

        pdf.cell(0, 5, f"- Scoring weights: Keyword {weights[0]:.0%} | Semantic {weights[1]:.0%} | Skill {weights[2]:.0%}", ln=True)

    pdf.ln(6)

    # ---- Footer ----
    pdf.set_font("Arial", "I", size=9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, f"Generated by {brand_name} AI Resume Screening System | {now}", ln=True, align="C")

    # Return PDF bytes (works reliably across fpdf versions)
    pdf_out = pdf.output(dest="S")
    if isinstance(pdf_out, (bytes, bytearray)):
        return bytes(pdf_out)
    else:
        return pdf_out.encode("latin-1")



