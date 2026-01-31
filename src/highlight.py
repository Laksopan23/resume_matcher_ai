import re
from typing import List


def highlight_terms(text: str, terms: List[str]) -> str:
    """
    Returns HTML with highlighted matches for the given terms.
    Note: Streamlit must render with unsafe_allow_html=True
    """
    if not text.strip() or not terms:
        return text

    # Highlight longer phrases first to avoid partial overlaps
    terms_sorted = sorted(set(terms), key=len, reverse=True)

    escaped_terms = [re.escape(t) for t in terms_sorted if t.strip()]
    pattern = r"(" + "|".join(escaped_terms) + r")"

    def repl(match):
        return f"<mark>{match.group(0)}</mark>"

    return re.sub(pattern, repl, text, flags=re.IGNORECASE)
