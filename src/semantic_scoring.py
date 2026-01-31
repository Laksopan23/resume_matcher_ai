from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# Cache model in memory (loads once)
_MODEL = None


def _get_model():
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _MODEL


def sbert_match_score(resume_text: str, jd_text: str) -> float:
    """
    Semantic similarity using Sentence-BERT embeddings.
    Returns a float between 0 and 1.
    """
    resume_text = (resume_text or "").strip()
    jd_text = (jd_text or "").strip()
    if not resume_text or not jd_text:
        return 0.0

    model = _get_model()
    emb = model.encode([resume_text, jd_text], normalize_embeddings=True)
    score = cosine_similarity([emb[0]], [emb[1]])[0][0]
    return float(score)
