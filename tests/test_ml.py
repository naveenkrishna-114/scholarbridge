import pytest
from ml.preprocessing import DataPreprocessor
from ml.recommend import MLSimilarityEngine
from ml.metrics import precision_at_k, recall_at_k, hit_rate_at_k, evaluate_recommender
from ml.train_model import train_and_persist_model, MODEL_FILE

@pytest.fixture
def sample_scholarships():
    return [
        {
            "id": 1,
            "name": "AICTE Pragati Scholarship for Girls",
            "provider": "AICTE",
            "description": "Financial aid for female engineering students.",
            "course": "B.Tech",
            "min_percentage": 60.0,
            "max_income": 800000.0,
            "gender": "Female",
            "state": "ALL",
            "category": "ALL",
            "other_requirements": "Max 2 girls per family"
        },
        {
            "id": 2,
            "name": "General Science Research Grant",
            "provider": "DST",
            "description": "Basic sciences physics chemistry biology research.",
            "course": "B.Sc",
            "min_percentage": 75.0,
            "max_income": 500000.0,
            "gender": "ALL",
            "state": "ALL",
            "category": "ALL",
            "other_requirements": "Research aptitude"
        },
        {
            "id": 3,
            "name": "Reliance Foundation Undergraduate Scholarship",
            "provider": "Reliance Foundation",
            "description": "Empowering high-merit students across India.",
            "course": "ALL",
            "min_percentage": 75.0,
            "max_income": 1500000.0,
            "gender": "ALL",
            "state": "ALL",
            "category": "ALL",
            "other_requirements": "Merit and aptitude"
        }
    ]

def test_preprocessor_tokens():
    student = {
        "course": "B.Tech",
        "branch": "Computer Science",
        "state": "Tamil Nadu",
        "percentage": 88.0,
        "income": 200000.0,
        "achievements": "National Hackathon Winner"
    }
    doc = DataPreprocessor.create_student_document(student)
    assert "b tech" in doc
    assert "computer science" in doc
    assert "tamil nadu" in doc
    assert "high_merit" in doc
    assert "national hackathon winner" in doc

def test_ml_similarity_scoring(sample_scholarships):
    engine = MLSimilarityEngine()
    engine.fit(sample_scholarships)

    # Female engineering student
    female_eng_student = {
        "course": "B.Tech",
        "gender": "Female",
        "state": "Maharashtra",
        "percentage": 85.0,
        "income": 300000.0
    }

    similarities = engine.compute_similarity(female_eng_student, sample_scholarships)
    assert len(similarities) == 3
    # AICTE Pragati (id=1) should have highest similarity due to 'b tech' and 'female'
    assert similarities[1] > similarities[2]
    assert 0.0 <= similarities[1] <= 1.0

def test_ml_evaluation_metrics():
    # True relevant items: [1, 3]
    actual = [1, 3]
    predicted = [1, 2, 3, 4]

    # Precision@2: Top 2 are [1, 2], hits = {1} -> 1 / 2 = 0.5
    assert precision_at_k(actual, predicted, k=2) == 0.5

    # Recall@2: hits = {1} / len(actual) = 1 / 2 = 0.5
    assert recall_at_k(actual, predicted, k=2) == 0.5

    # HitRate@2: hits > 0 -> 1.0
    assert hit_rate_at_k(actual, predicted, k=2) == 1.0

    # Precision@3: Top 3 are [1, 2, 3], hits = {1, 3} -> 2 / 3 = 0.667
    assert round(precision_at_k(actual, predicted, k=3), 2) == 0.67

    # Evaluate multiple test cases
    benchmark_cases = [
        {"expected_relevant_ids": [1, 3], "predicted_ranked_ids": [1, 3, 2]},
        {"expected_relevant_ids": [2], "predicted_ranked_ids": [2, 1, 3]}
    ]
    eval_results = evaluate_recommender(benchmark_cases, k=2)
    assert eval_results["hit_rate@2"] == 1.0
    assert eval_results["precision@2"] >= 0.75
