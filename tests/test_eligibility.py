import pytest
from services.eligibility_service import EligibilityService

@pytest.fixture
def base_student():
    return {
        "name": "Aarav Sharma",
        "age": 20,
        "gender": "Male",
        "state": "Tamil Nadu",
        "course": "B.Tech",
        "branch": "Computer Science",
        "year": 2,
        "percentage": 84.0,
        "income": 200000.0,
        "category": "General"
    }

@pytest.fixture
def base_scholarship():
    return {
        "id": 1,
        "name": "General Tech Merit Grant",
        "provider": "Ministry of Education",
        "min_percentage": 75.0,
        "max_income": 300000.0,
        "state": "ALL",
        "course": "B.Tech",
        "category": "ALL",
        "gender": "ALL",
        "year": 2,
        "deadline": "2026-12-31",
        "official_url": "https://example.gov.in",
        "status": "ACTIVE"
    }

def test_eligibility_happy_path(base_student, base_scholarship):
    is_eligible, details = EligibilityService.evaluate(base_student, base_scholarship)
    assert is_eligible is True
    assert len(details["failed_criteria"]) == 0
    assert any("academic percentage satisfied" in p.lower() for p in details["passed_criteria"])
    assert any("income requirement satisfied" in p.lower() for p in details["passed_criteria"])

def test_academic_percentage_failure(base_student, base_scholarship):
    base_student["percentage"] = 70.0  # below 75.0
    is_eligible, details = EligibilityService.evaluate(base_student, base_scholarship)
    assert is_eligible is False
    assert any("below minimum required" in f.lower() for f in details["failed_criteria"])

def test_income_limit_failure(base_student, base_scholarship):
    base_student["income"] = 500000.0  # above 300000.0
    is_eligible, details = EligibilityService.evaluate(base_student, base_scholarship)
    assert is_eligible is False
    assert any("exceeds maximum ceiling" in f.lower() for f in details["failed_criteria"])

def test_state_specific_and_mismatch(base_student, base_scholarship):
    # Domicile requirement: Maharashtra only
    base_scholarship["state"] = "Maharashtra"
    is_eligible, details = EligibilityService.evaluate(base_student, base_scholarship)
    assert is_eligible is False
    assert any("state domicile requirement not met" in f.lower() for f in details["failed_criteria"])

    # Change student state to Maharashtra -> should pass
    base_student["state"] = "Maharashtra"
    is_eligible_pass, _ = EligibilityService.evaluate(base_student, base_scholarship)
    assert is_eligible_pass is True

def test_all_india_state_passes(base_student, base_scholarship):
    base_scholarship["state"] = "ALL"
    base_student["state"] = "Kerala"
    is_eligible, _ = EligibilityService.evaluate(base_student, base_scholarship)
    assert is_eligible is True

def test_gender_specific_criteria(base_student, base_scholarship):
    # Scholarship for Female only (e.g. AICTE Pragati)
    base_scholarship["gender"] = "Female"
    is_eligible, details = EligibilityService.evaluate(base_student, base_scholarship)
    assert is_eligible is False
    assert any("gender requirement not met" in f.lower() for f in details["failed_criteria"])

    # Female student passes
    base_student["gender"] = "Female"
    is_eligible_pass, _ = EligibilityService.evaluate(base_student, base_scholarship)
    assert is_eligible_pass is True

def test_category_reservation(base_student, base_scholarship):
    base_scholarship["category"] = "SC"
    is_eligible, details = EligibilityService.evaluate(base_student, base_scholarship)
    assert is_eligible is False

    base_student["category"] = "SC"
    is_eligible_pass, _ = EligibilityService.evaluate(base_student, base_scholarship)
    assert is_eligible_pass is True

def test_expired_scholarship(base_student, base_scholarship):
    # Past deadline
    base_scholarship["deadline"] = "2024-01-01"
    is_eligible, details = EligibilityService.evaluate(base_student, base_scholarship)
    assert is_eligible is False
    assert any("deadline has passed" in f.lower() for f in details["failed_criteria"])

    # Status marked EXPIRED
    base_scholarship["deadline"] = "2026-12-31"
    base_scholarship["status"] = "EXPIRED"
    is_eligible_exp, details_exp = EligibilityService.evaluate(base_student, base_scholarship)
    assert is_eligible_exp is False

def test_batch_filter_eligible(base_student, base_scholarship):
    sch1 = dict(base_scholarship, id=1, name="Eligible Scheme")
    sch2 = dict(base_scholarship, id=2, name="Ineligible Scheme (Low Pct)", min_percentage=95.0)
    sch3 = dict(base_scholarship, id=3, name="Ineligible Scheme (State)", state="Bihar")

    results = EligibilityService.filter_eligible(base_student, [sch1, sch2, sch3])
    assert len(results) == 1
    assert results[0]["id"] == 1
    assert "eligibility_details" in results[0]
