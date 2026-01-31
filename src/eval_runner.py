"""
Experiment runner for evaluating ranking models.
Compares different weight configurations and computes metrics.
"""

from typing import List, Dict, Tuple
import pandas as pd

from src.ranking import score_resume_against_jd
from src.eval_metrics import precision_at_k, ndcg_at_k


def run_experiment(
    jd_text: str,
    resumes: List[Dict],
    weights: Tuple[float, float, float],
    k_values: Tuple[int, ...] = (3, 5),
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Run ranking experiment on labeled dataset.
    
    Args:
        jd_text: job description text
        resumes: list of dicts with keys:
                 - "filename": str (e.g., "resume1.pdf")
                 - "text": str (resume text)
                 - "label": int (0=bad, 1=ok, 2=good)
        weights: tuple of (keyword_weight, semantic_weight, skill_weight)
        k_values: tuple of k cutoffs for metrics (default: (3, 5))
    
    Returns:
        (df_metrics, df_ranked)
        - df_metrics: rows with k, precision@k, ndcg@k
        - df_ranked: ranked results with predictions and labels
    """

    # Score all resumes
    results = []
    for r in resumes:
        scored = score_resume_against_jd(
            resume_text=r["text"],
            jd_text=jd_text,
            filename=r["filename"],
            weights=weights,
        )
        results.append((scored, r["label"]))

    # Sort by predicted overall score (highest first)
    results_sorted = sorted(results, key=lambda x: x[0].overall, reverse=True)

    # Extract labels in ranked order
    rel = [lab for _, lab in results_sorted]
    binary_good = [1 if x >= 1 else 0 for x in rel]  # 0=bad, 1+=good

    # Compute metrics at each k
    rows_metrics = []
    for k in k_values:
        rows_metrics.append({
            "k": k,
            "Precision@K": round(precision_at_k(binary_good, k), 4),
            "NDCG@K": round(ndcg_at_k(rel, k), 4),
        })

    df_metrics = pd.DataFrame(rows_metrics)

    # Build ranked output for inspection
    rows_ranked = []
    for i, (scored, label) in enumerate(results_sorted):
        rows_ranked.append({
            "Rank": i + 1,
            "Filename": scored.filename,
            "Predicted Score": round(scored.overall, 4),
            "True Label": label,
            "Label Name": {0: "Bad", 1: "OK", 2: "Good"}.get(label, "Unknown"),
        })

    df_ranked = pd.DataFrame(rows_ranked)

    return df_metrics, df_ranked
