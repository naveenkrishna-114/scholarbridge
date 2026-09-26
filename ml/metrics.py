from typing import List, Set, Any, Dict

def precision_at_k(actual: List[Any], predicted: List[Any], k: int) -> float:
    """
    Calculate Precision@K: Proportion of top-K recommended items that are relevant.
    """
    if k <= 0 or not predicted:
        return 0.0
    top_k_pred = predicted[:k]
    relevant_set = set(actual)
    hits = sum(1 for item in top_k_pred if item in relevant_set)
    return hits / k

def recall_at_k(actual: List[Any], predicted: List[Any], k: int) -> float:
    """
    Calculate Recall@K: Proportion of relevant items that are captured in top-K recommendations.
    """
    if not actual or k <= 0:
        return 0.0
    top_k_pred = predicted[:k]
    relevant_set = set(actual)
    hits = sum(1 for item in top_k_pred if item in relevant_set)
    return hits / len(relevant_set)

def hit_rate_at_k(actual: List[Any], predicted: List[Any], k: int) -> float:
    """
    Calculate Hit Rate@K: Returns 1.0 if at least one relevant item appears in top-K, else 0.0.
    """
    if k <= 0 or not predicted or not actual:
        return 0.0
    top_k_pred = set(predicted[:k])
    relevant_set = set(actual)
    return 1.0 if len(top_k_pred.intersection(relevant_set)) > 0 else 0.0

def evaluate_recommender(test_cases: List[Dict[str, Any]], k: int = 3) -> Dict[str, float]:
    """
    Evaluate ranking performance across a suite of labeled benchmark student profiles.
    Each test case must supply:
        'student': dict
        'expected_relevant_ids': list of scholarship ids
        'predicted_ranked_ids': list of recommended scholarship ids
    """
    if not test_cases:
        return {"precision@k": 0.0, "recall@k": 0.0, "hit_rate@k": 0.0}

    precisions = []
    recalls = []
    hit_rates = []

    for case in test_cases:
        actual = case["expected_relevant_ids"]
        pred = case["predicted_ranked_ids"]
        precisions.append(precision_at_k(actual, pred, k))
        recalls.append(recall_at_k(actual, pred, k))
        hit_rates.append(hit_rate_at_k(actual, pred, k))

    return {
        f"precision@{k}": round(sum(precisions) / len(precisions), 3),
        f"recall@{k}": round(sum(recalls) / len(recalls), 3),
        f"hit_rate@{k}": round(sum(hit_rates) / len(hit_rates), 3)
    }
