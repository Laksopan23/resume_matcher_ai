import re
from typing import Dict


SECTION_HEADERS = {
    "skills": ["skills", "technical skills", "core skills"],
    "experience": ["experience", "work experience", "professional experience", "employment"],
    "projects": ["projects", "personal projects", "academic projects"],
    "education": ["education", "academic background"],
}


def split_sections(resume_text: str) -> Dict[str, str]:
    """
    Lightweight section splitter:
    Finds common headings and extracts text between headings.
    If not found, returns empty for that section.
    """
    text = (resume_text or "").strip()
    low = text.lower()

    # Find positions of known headers
    hits = []
    for sec, names in SECTION_HEADERS.items():
        for name in names:
            # match header on its own line or with colon
            pattern = rf"(^|\n)\s*{re.escape(name)}\s*:?\s*(\n|$)"
            m = re.search(pattern, low)
            if m:
                hits.append((m.start(), sec))
                break

    hits.sort(key=lambda x: x[0])

    # If no headers found, return empty sections
    if not hits:
        return {k: "" for k in SECTION_HEADERS.keys()}

    # Slice between hits
    sections = {k: "" for k in SECTION_HEADERS.keys()}
    for i, (start, sec) in enumerate(hits):
        end = hits[i + 1][0] if i + 1 < len(hits) else len(text)
        sections[sec] = text[start:end].strip()

    return sections
