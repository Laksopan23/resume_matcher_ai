"""
Experiment runner for evaluating and comparing ranking models.
Supports PDF uploads with ground truth labels.
"""

from dataclasses import dataclass
from typing import List, Tuple, Dict
import pandas as pd

from src.ranking import score_resume_against_jd
from src.eval_metrics import precision_at_k, ndcg_at_k


@dataclass
class EvalItem:
    """Represents a labeled resume for evaluation."""
    filename: str
    text: str
    label: int  # 0=bad, 1=ok, 2=good


def _run_once(
    jd_text: str,
    items: List[EvalItem],
    weights: Tuple[float, float, float]
) -> Tuple[List[int], List[int], pd.DataFrame]:
    """
    Score all items and return metrics.
    
    Returns:
        (relevances, binary_labels, leaderboard_df)
    """
    scored = []
    for it in items:
        s = score_resume_against_jd(it.text, jd_text, it.filename, weights)
        scored.append((s, it.label))

    # Sort by predicted overall score
    scored_sorted = sorted(scored, key=lambda x: x[0].overall, reverse=True)
    
    # Extract labels in ranked order
    rel = [lab for _, lab in scored_sorted]
    binary = [1 if r >= 1 else 0 for r in rel]  # ok+good are relevant

    # Build leaderboard
    leaderboard = pd.DataFrame([{
        "Rank": i + 1,
        "Filename": s.filename,
        "Predicted": round(s.overall, 4),
        "Semantic": round(s.sbert, 4),
        "Keyword": round(s.tfidf, 4),
        "Skill": round(s.skill_overlap, 4),
        "True Label": lab,
    } for i, (s, lab) in enumerate(scored_sorted)])

    return rel, binary, leaderboard


def compare_models(
    jd_text: str,
    items: List[EvalItem],
    ensemble_weights: Tuple[float, float, float],
    k_values: Tuple[int, ...] = (3, 5, 10)
) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """
    Compare TF-IDF, SBERT, Skill, and Ensemble models.
    
    Args:
        jd_text: job description
        items: list of labeled resumes
        ensemble_weights: (kw, sem, skill) weights for ensemble
        k_values: cutoffs for metrics
    
    Returns:
        (metrics_df, leaderboards_dict)
    """
    configs = [
        ("TF-IDF only", (1.0, 0.0, 0.0)),
        ("SBERT only", (0.0, 1.0, 0.0)),
        ("Skill only", (0.0, 0.0, 1.0)),
        ("Ensemble", ensemble_weights),
    ]

    metrics_rows = []
    leaderboards: Dict[str, pd.DataFrame] = {}

    for name, w in configs:
        rel, binary, lb = _run_once(jd_text, items, w)
        leaderboards[name] = lb

        for k in k_values:
            metrics_rows.append({
                "Model": name,
                "K": k,
                "Precision@K": round(precision_at_k(binary, k), 4),
                "NDCG@K": round(ndcg_at_k(rel, k), 4),
            })

    df_metrics = pd.DataFrame(metrics_rows)
    return df_metrics, leaderboards
