from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def tfidf_match_score(resume_text: str, jd_text: str) -> float:
    """
    Compute similarity score between resume and job description using TF-IDF + cosine similarity.
    Returns a float between 0 and 1.
    """
    resume_text = (resume_text or "").strip()
    jd_text = (jd_text or "").strip()

    if not resume_text or not jd_text:
        return 0.0

    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform([resume_text, jd_text])
    score = cosine_similarity(vectors[0], vectors[1])[0][0]
    return float(score)
