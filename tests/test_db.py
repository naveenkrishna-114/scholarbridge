import pytest
import sqlite3
from pathlib import Path
from database.db import init_db, get_db
from models.user import User, StudentProfile
from models.scholarship import Scholarship, SavedScholarship, RecommendationRecord

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "database" / "schema.sql"

@pytest.fixture
def temp_db(tmp_path):
    db_file = str(tmp_path / "test_scholarships.db")
    init_db(db_path=db_file, schema_path=SCHEMA_PATH)
    return db_file

def test_user_creation_and_auth(temp_db):
    user = User.create(
        name="Test Student",
        email="test@example.com",
        password="SecurePassword123",
        role="student",
        db_path=temp_db
    )
    assert user["id"] is not None
    assert user["name"] == "Test Student"
    assert user["email"] == "test@example.com"
    assert user["role"] == "student"

    fetched = User.get_by_email("test@example.com", db_path=temp_db)
    assert fetched is not None
    assert User.check_password(fetched["password_hash"], "SecurePassword123")
    assert not User.check_password(fetched["password_hash"], "WrongPassword")

def test_duplicate_user_email_rejected(temp_db):
    User.create("Student A", "duplicate@example.com", "Password123", db_path=temp_db)
    with pytest.raises(ValueError, match="already exists"):
        User.create("Student B", "duplicate@example.com", "Password123", db_path=temp_db)

def test_student_profile_upsert_and_validation(temp_db):
    user = User.create("Profile User", "profile@example.com", "Password123", db_path=temp_db)
    
    # Valid profile
    profile_data = {
        "age": 20,
        "gender": "Male",
        "state": "Tamil Nadu",
        "district": "Chennai",
        "course": "B.Tech",
        "branch": "Computer Science",
        "year": 2,
        "percentage": 84.0,
        "cgpa": 8.7,
        "income": 200000.0,
        "category": "General",
        "disability_status": "No",
        "achievements": "Hackathon Winner"
    }
    profile = StudentProfile.upsert(user["id"], profile_data, db_path=temp_db)
    assert profile["course"] == "B.Tech"
    assert profile["percentage"] == 84.0

    # Update profile
    profile_data["percentage"] = 86.5
    updated_profile = StudentProfile.upsert(user["id"], profile_data, db_path=temp_db)
    assert updated_profile["percentage"] == 86.5

    # Invalid profile validation
    invalid_data = profile_data.copy()
    invalid_data["percentage"] = 105.0 # Invalid > 100
    with pytest.raises(ValueError, match="Percentage must be between 0.0 and 100.0"):
        StudentProfile.upsert(user["id"], invalid_data, db_path=temp_db)

def test_scholarship_crud_operations(temp_db):
    sch_data = {
        "name": "Merit Scholarship 2026",
        "provider": "Ministry of Education",
        "description": "Excellence grant",
        "amount": 50000.0,
        "course": "B.Tech",
        "min_percentage": 75.0,
        "max_income": 300000.0,
        "state": "Tamil Nadu",
        "category": "ALL",
        "gender": "ALL",
        "year": 2,
        "deadline": "2026-11-30",
        "official_url": "https://scholarships.gov.in/merit",
        "status": "ACTIVE"
    }
    created = Scholarship.create(sch_data, db_path=temp_db)
    assert created["id"] is not None
    assert created["name"] == "Merit Scholarship 2026"

    # Read/List
    active_list = Scholarship.list_all(status="ACTIVE", db_path=temp_db)
    assert len(active_list) == 1

    # Update
    sch_data["amount"] = 60000.0
    updated = Scholarship.update(created["id"], sch_data, db_path=temp_db)
    assert updated["amount"] == 60000.0

    # Delete
    Scholarship.delete(created["id"], db_path=temp_db)
    assert Scholarship.get_by_id(created["id"], db_path=temp_db) is None

def test_saved_scholarships_and_recommendations(temp_db):
    user = User.create("Bookmark User", "bm@example.com", "Password123", db_path=temp_db)
    sch = Scholarship.create({
        "name": "Saved Grant",
        "provider": "Trust",
        "amount": 20000.0,
        "official_url": "https://trust.org",
        "status": "ACTIVE"
    }, db_path=temp_db)

    # Save
    SavedScholarship.save(user["id"], sch["id"], db_path=temp_db)
    assert SavedScholarship.is_saved(user["id"], sch["id"], db_path=temp_db) is True
    saved_list = SavedScholarship.list_by_user(user["id"], db_path=temp_db)
    assert len(saved_list) == 1
    assert saved_list[0]["name"] == "Saved Grant"

    # Remove
    SavedScholarship.remove(user["id"], sch["id"], db_path=temp_db)
    assert SavedScholarship.is_saved(user["id"], sch["id"], db_path=temp_db) is False

    # Recommendations record
    RecommendationRecord.save(
        user["id"], sch["id"], score=0.88,
        explanation={"reasons": ["Academic match", "Income match"]},
        db_path=temp_db
    )
    rec_history = RecommendationRecord.list_by_user(user["id"], db_path=temp_db)
    assert len(rec_history) == 1
    assert rec_history[0]["score"] == 0.88
    assert "Academic match" in rec_history[0]["explanation"]["reasons"]
