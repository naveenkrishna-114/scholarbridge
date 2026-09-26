import pytest
from app import create_app
from database.seed import seed_database

@pytest.fixture
def e2e_app(tmp_path):
    test_db = str(tmp_path / "test_e2e.db")
    app = create_app("testing")
    app.config["DATABASE_PATH"] = test_db
    app.config["SECRET_KEY"] = "e2e-secret-key"
    with app.app_context():
        seed_database(test_db)
    return app

@pytest.fixture
def client(e2e_app):
    return e2e_app.test_client()

def test_complete_demonstration_workflow(client):
    """
    Executes the exact 11-step Final Demonstration Flow per Section 30 of the Master Specification.
    """
    # Step 1: Open landing page
    res_home = client.get("/")
    assert res_home.status_code == 200
    assert b"ScholarMatch" in res_home.data
    assert b"Discover Scholarships" in res_home.data

    # Step 2: Register a demo student
    student_email = "demo.student2026@example.com"
    res_reg = client.post("/register", data={
        "name": "Karthik Raja",
        "email": student_email,
        "password": "Password123!"
    }, follow_redirects=True)
    assert res_reg.status_code == 200
    assert b"Student Profile" in res_reg.data

    # Step 3: Complete profile with academic, income, course and location details
    res_profile = client.post("/profile", data={
        "course": "B.Tech",
        "branch": "Computer Science",
        "year": "2",
        "percentage": "84.0",
        "cgpa": "8.7",
        "state": "Tamil Nadu",
        "district": "Chennai",
        "gender": "Male",
        "age": "20",
        "category": "General",
        "income": "200000",
        "disability_status": "No",
        "achievements": "National Coding Hackathon Winner"
    }, follow_redirects=True)
    assert res_profile.status_code == 200

    # Step 4 & 5: Check processing and display recommendations
    res_rec = client.get("/recommendations")
    assert res_rec.status_code == 200
    assert b"Personalized Recommendations" in res_rec.data

    # Step 6: Verify ranked results and match scores
    assert b"Relevant" in res_rec.data
    assert b"Why You Matched" in res_rec.data
    assert b"Tamil Nadu Chief Minister Merit Scholarship" in res_rec.data

    # Step 7: Open a scholarship details page
    res_detail = client.get("/scholarships/6")
    assert res_detail.status_code == 200
    assert b"Tamil Nadu Chief Minister Merit Scholarship" in res_detail.data

    # Step 8: Show matching reasons and verification items
    assert b"Eligibility Requirements" in res_detail.data
    assert b"Tamil Nadu" in res_detail.data

    # Step 9: Verify official application link is present
    assert b"https://www.tn.gov.in/scholarships" in res_detail.data

    # Step 10: Show saved scholarship functionality
    res_save = client.post("/api/saved/6")
    assert res_save.status_code == 200

    res_saved_view = client.get("/saved")
    assert res_saved_view.status_code == 200
    assert b"Tamil Nadu Chief Minister Merit Scholarship" in res_saved_view.data

    # Step 11: Open admin dashboard and demonstrate management
    # Logout student
    client.get("/logout")

    # Login as seeded Admin
    client.post("/login", data={
        "email": "vikram.admin@example.com",
        "password": "Password123!"
    }, follow_redirects=True)

    res_admin = client.get("/admin")
    assert res_admin.status_code == 200
    assert b"Scholarship Administration" in res_admin.data
    assert b"ACTIVE SCHEMES" in res_admin.data
