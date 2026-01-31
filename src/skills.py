import re
from typing import List, Set

from src.skills_db import SKILLS


def _normalize(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"\s+", " ", text)
    return text


def extract_skills(text: str) -> List[str]:
    """
    Simple dictionary-based skill extraction.
    Finds skills from SKILLS that appear in the text.
    """
    t = _normalize(text)
    found: Set[str] = set()

    for skill in SKILLS:
        # word-boundary match for single words; phrase match for multi-words
        if " " in skill:
            if skill in t:
                found.add(skill)
        else:
            if re.search(rf"\b{re.escape(skill)}\b", t):
                found.add(skill)

    return sorted(found)


def missing_skills(jd_skills: List[str], resume_skills: List[str]) -> List[str]:
    return sorted(set(jd_skills) - set(resume_skills))
