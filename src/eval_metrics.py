"""
Evaluation metrics for ranking quality assessment.
Used to compute Precision@K and NDCG@K for model comparison.
"""

import math
from typing import List


def precision_at_k(labels: List[int], k: int) -> float:
    """
    Precision@K: fraction of top-k results that are relevant.
    
    Args:
        labels: ranked list where 1 = relevant/good, 0 = not relevant
        k: cutoff position
    
    Returns:
        Precision@K (0 to 1)
    """
    k = max(1, min(k, len(labels)))
    return sum(labels[:k]) / k


def dcg_at_k(relevances: List[int], k: int) -> float:
    """
    Discounted Cumulative Gain@K: sums relevances with log discount.
    Rewards relevant items placed higher in ranking.
    
    Args:
        relevances: ranked list of relevance scores (0, 1, 2, ...)
        k: cutoff position
    
    Returns:
        DCG@K score
    """
    k = max(1, min(k, len(relevances)))
    score = 0.0
    for i in range(k):
        rel = relevances[i]
        score += (2**rel - 1) / math.log2(i + 2)
    return score


def ndcg_at_k(relevances: List[int], k: int) -> float:
    """
    Normalized Discounted Cumulative Gain@K: DCG normalized by ideal ranking.
    
    Args:
        relevances: ranked list of relevance scores
        k: cutoff position
    
    Returns:
        NDCG@K (0 to 1, where 1 = perfect ranking)
    """
    ideal = sorted(relevances, reverse=True)
    denom = dcg_at_k(ideal, k)
    return 0.0 if denom == 0 else dcg_at_k(relevances, k) / denom
