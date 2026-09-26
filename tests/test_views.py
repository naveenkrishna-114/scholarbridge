import pytest
from app import create_app
from database.seed import seed_database

@pytest.fixture
def app_with_seed(tmp_path):
    test_db = str(tmp_path / "test_views.db")
    app = create_app("testing")
    app.config["DATABASE_PATH"] = test_db
    app.config["SECRET_KEY"] = "test-secret"
    with app.app_context():
        seed_database(test_db)
    return app

@pytest.fixture
def client(app_with_seed):
    return app_with_seed.test_client()

def test_landing_page(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"ScholarMatch" in res.data
    assert b"Discover Scholarships" in res.data

def test_browse_directory(client):
    res = client.get("/scholarships")
    assert res.status_code == 200
    assert b"Scholarship Directory" in res.data
    assert b"Reliance Foundation" in res.data

def test_scholarship_details_view(client):
    # Scholarship 1 (AICTE Pragati)
    res = client.get("/scholarships/1")
    assert res.status_code == 200
    assert b"AICTE Pragati" in res.data
    assert b"Eligibility Requirements" in res.data

def test_protected_views_require_login(client):
    # Recommendations without login
    res_rec = client.get("/recommendations")
    assert res_rec.status_code == 302
    assert "/login" in res_rec.headers["Location"]

    # Saved without login
    res_saved = client.get("/saved")
    assert res_saved.status_code == 302
    assert "/login" in res_saved.headers["Location"]

def test_authenticated_student_recommendations_view(client):
    # Login as seeded demo student (Aarav Sharma)
    res_login = client.post("/login", data={
        "email": "aarav.sharma@example.com",
        "password": "Password123!"
    }, follow_redirects=True)
    assert res_login.status_code == 200

    # View recommendations
    res_rec = client.get("/recommendations")
    assert res_rec.status_code == 200
    assert b"Personalized Recommendations" in res_rec.data
    assert b"Why You Matched" in res_rec.data
    assert b"Relevant" in res_rec.data

    # View saved list
    res_saved = client.get("/saved")
    assert res_saved.status_code == 200
    assert b"Saved Scholarships" in res_saved.data
