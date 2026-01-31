from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple

from src.scoring import tfidf_match_score
from src.semantic_scoring import sbert_match_score
from src.skills import extract_skills, missing_skills
from src.robustness import keyword_stuffing_penalty, length_normalization


@dataclass
class CandidateResult:
    filename: str
    overall: float
    tfidf: float
    sbert: float
    skill_overlap: float
    resume_skills: List[str]
    jd_skills: List[str]
    missing: List[str]
    decision: str


def _skill_overlap_ratio(resume_sk: List[str], jd_sk: List[str]) -> float:
    jd_set = set(jd_sk)
    if not jd_set:
        return 0.0
    return len(set(resume_sk) & jd_set) / len(jd_set)


def score_resume_against_jd(
    resume_text: str,
    jd_text: str,
    filename: str,
    weights: Tuple[float, float, float],
) -> CandidateResult:
    """
    weights = (w_tfidf, w_sbert, w_skill_overlap)
    All scores are 0..1.
    """
    tfidf = tfidf_match_score(resume_text, jd_text)
    sbert = sbert_match_score(resume_text, jd_text)

    resume_sk = extract_skills(resume_text)
    jd_sk = extract_skills(jd_text)
    overlap = _skill_overlap_ratio(resume_sk, jd_sk)
    miss = missing_skills(jd_sk, resume_sk)

    w_t, w_s, w_o = weights
    base_score = (w_t * tfidf) + (w_s * sbert) + (w_o * overlap)

    # Apply robustness penalties
    penalty = keyword_stuffing_penalty(resume_text, jd_sk)
    length_factor = length_normalization(resume_text)
    overall = base_score * penalty * length_factor

    # ATS decision
    if overall >= 0.75:
        decision = "SHORTLIST"
    elif overall >= 0.55:
        decision = "REVIEW"
    else:
        decision = "REJECT"

    return CandidateResult(
        filename=filename,
        overall=float(overall),
        tfidf=float(tfidf),
        sbert=float(sbert),
        skill_overlap=float(overlap),
        resume_skills=resume_sk,
        jd_skills=jd_sk,
        missing=miss,
        decision=decision,
    )


def to_row_dict(r: CandidateResult) -> Dict:
    d = asdict(r)
    # keep table clean
    d["overall_%"] = round(d.pop("overall") * 100, 2)
    d["tfidf_%"] = round(d.pop("tfidf") * 100, 2)
    d["sbert_%"] = round(d.pop("sbert") * 100, 2)
    d["skill_overlap_%"] = round(d.pop("skill_overlap") * 100, 2)

    # shorten long lists for table view
    d["missing_skills_preview"] = ", ".join(r.missing[:10]) + (" ..." if len(r.missing) > 10 else "")
    d.pop("resume_skills")
    d.pop("jd_skills")
    d.pop("missing")
    # Keep decision in output
    return d
