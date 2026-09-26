import pytest
from app import create_app
from database.seed import seed_database
from database.db import init_db
from models.scholarship import Scholarship
from services.eligibility_service import EligibilityService
from services.explanation_service import ExplanationService
from services.recommendation_service import RecommendationService

@pytest.fixture
def app_instance(tmp_path):
    test_db = str(tmp_path / "test_bugfixes.db")
    app = create_app("testing")
    app.config["DATABASE_PATH"] = test_db
    app.config["SECRET_KEY"] = "test-secret"
    with app.app_context():
        seed_database(test_db)
    return app

@pytest.fixture
def client(app_instance):
    return app_instance.test_client()

def test_eligibility_string_numeric_handling():
    """Verify that string inputs for income, percentage, age, year do not crash EligibilityService."""
    student_with_strings = {
        "percentage": "85.5",
        "income": "250000",
        "age": "21",
        "year": "2",
        "state": "ALL",
        "course": "ALL",
        "gender": "ALL",
        "category": "General"
    }
    scholarship_with_strings = {
        "min_percentage": "60.0",
        "max_income": "500000",
        "age_min": "18",
        "age_max": "25",
        "year": "2",
        "state": "ALL",
        "course": "ALL",
        "gender": "ALL",
        "category": "ALL",
        "status": "ACTIVE"
    }

    is_eligible, details = EligibilityService.evaluate(student_with_strings, scholarship_with_strings)
    assert is_eligible is True
    assert len(details["failed_criteria"]) == 0
    # Ensure currency formatting did not crash and produced expected text
    assert any("250,000" in p for p in details["passed_criteria"])

def test_explanation_string_numeric_handling():
    """Verify that ExplanationService handles string and empty numbers without formatting errors."""
    student = {
        "course": "B.Tech",
        "percentage": "88.0",
        "income": "180000",
        "state": "Maharashtra",
        "gender": "Female"
    }
    scholarship = {
        "name": "Tech Grant",
        "course": "B.Tech",
        "min_percentage": "70.0",
        "max_income": "600000",
        "state": "Maharashtra",
        "gender": "Female",
        "official_url": "https://example.com"
    }
    explanation = ExplanationService.generate(
        student=student,
        scholarship=scholarship,
        score=0.92,
        score_breakdown={"academic_performance": 0.9, "income": 0.8},
        eligibility_details={"verification_items": []}
    )
    assert explanation["match_percentage"] == 92
    assert any("180,000" in r for r in explanation["reasons"])
    assert any("600,000" in r for r in explanation["reasons"])

def test_scholarship_empty_strings_crud(tmp_path):
    """Verify Scholarship.create and update handle empty string optional fields gracefully."""
    db_file = str(tmp_path / "crud_test.db")
    init_db(db_file)

    sch_data = {
        "name": "Flexible Grant",
        "provider": "Foundation",
        "official_url": "https://foundation.org",
        "amount": "",           # Empty string
        "min_percentage": "",   # Empty string
        "max_income": "",       # Empty string
        "year": "",
        "age_min": "",
        "age_max": "",
        "status": "ACTIVE"
    }
    created = Scholarship.create(sch_data, db_path=db_file)
    assert created["id"] is not None
    assert created["amount"] is None
    assert created["min_percentage"] == 0.0
    assert created["max_income"] == 10000000.0

    # Update with empty strings
    update_data = dict(sch_data, amount="50000")
    updated = Scholarship.update(created["id"], update_data, db_path=db_file)
    assert updated["amount"] == 50000.0

def test_template_rendering_with_null_max_income(client, app_instance):
    """Verify that scholarship details view renders properly even when max_income is None."""
    with app_instance.app_context():
        sch = Scholarship.create({
            "name": "No Income Ceiling Scholarship",
            "provider": "Philanthropy Trust",
            "official_url": "https://trust.example.org",
            "max_income": None,
            "status": "ACTIVE"
        })
        sch_id = sch["id"]

    res = client.get(f"/scholarships/{sch_id}")
    assert res.status_code == 200
    assert b"No Limit" in res.data or b"No Income Ceiling" in res.data

def test_api_404_json_error(client):
    """Verify that undefined /api routes return JSON error, not HTML."""
    res = client.get("/api/nonexistent-endpoint")
    assert res.status_code == 404
    data = res.get_json()
    assert data is not None
    assert "error" in data

def test_recommendation_integer_percentage_badges(app_instance):
    """Verify that RecommendationService calculations work without syntax or type errors."""
    with app_instance.app_context():
        service = RecommendationService()
        score, breakdown = service.calculate_score(
            {"course": "B.Tech", "percentage": "84.5", "income": "200000", "year": "2"},
            {"course": "B.Tech", "min_percentage": "60", "max_income": "500000", "year": "2"}
        )
        assert 0.0 <= score <= 1.0
        assert isinstance(breakdown, dict)
