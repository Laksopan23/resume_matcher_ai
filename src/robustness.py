import re
from typing import List


def keyword_stuffing_penalty(text: str, jd_skills: List[str]) -> float:
    """
    Penalize excessive repetition of JD skills.
    Returns a penalty factor between 0.85 and 1.0
    """
    text = (text or "").lower()
    if not jd_skills:
        return 1.0

    counts = []
    for skill in jd_skills:
        if skill.strip():
            counts.append(len(re.findall(rf"\b{re.escape(skill)}\b", text)))

    if not counts:
        return 1.0

    avg = sum(counts) / len(counts)

    # If average repetition is suspiciously high
    if avg > 6:
        return 0.85
    if avg > 4:
        return 0.90
    if avg > 3:
        return 0.95

    return 1.0


def length_normalization(text: str) -> float:
    """
    Normalize score so very long resumes don't dominate.
    Returns factor between 0.9 and 1.0
    """
    words = len((text or "").split())

    if words > 1500:
        return 0.90
    if words > 1000:
        return 0.95

    return 1.0
