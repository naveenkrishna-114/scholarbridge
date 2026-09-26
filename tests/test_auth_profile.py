import pytest
from app import create_app
from database.db import init_db

@pytest.fixture
def app(tmp_path):
    test_db = str(tmp_path / "test_auth.db")
    app = create_app("testing")
    app.config["DATABASE_PATH"] = test_db
    app.config["SECRET_KEY"] = "test-secret"
    with app.app_context():
        init_db(test_db)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_register_success(client):
    res = client.post("/api/register", json={
        "name": "Kavya Sundaram",
        "email": "kavya@example.com",
        "password": "Password123!"
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data["message"] == "Registration successful."
    assert data["user"]["email"] == "kavya@example.com"
    assert data["user"]["role"] == "student"

def test_register_duplicate_email(client):
    client.post("/api/register", json={
        "name": "Original User",
        "email": "dup@example.com",
        "password": "Password123!"
    })
    res = client.post("/api/register", json={
        "name": "Another User",
        "email": "dup@example.com",
        "password": "Password123!"
    })
    assert res.status_code == 400
    assert "already exists" in res.get_json()["error"]

def test_register_invalid_inputs(client):
    # Missing name
    res = client.post("/api/register", json={"name": "", "email": "a@b.com", "password": "pass12345"})
    assert res.status_code == 400

    # Invalid email
    res = client.post("/api/register", json={"name": "Test", "email": "invalid-email", "password": "pass12345"})
    assert res.status_code == 400

    # Short password
    res = client.post("/api/register", json={"name": "Test", "email": "valid@email.com", "password": "123"})
    assert res.status_code == 400

def test_login_and_logout(client):
    # Register first
    client.post("/api/register", json={
        "name": "Login User",
        "email": "loginuser@example.com",
        "password": "CorrectPassword"
    })

    # Successful login
    res = client.post("/api/login", json={
        "email": "loginuser@example.com",
        "password": "CorrectPassword"
    })
    assert res.status_code == 200
    assert res.get_json()["message"] == "Login successful."

    # Check /api/me
    res_me = client.get("/api/me")
    assert res_me.status_code == 200
    assert res_me.get_json()["authenticated"] is True
    assert res_me.get_json()["user"]["email"] == "loginuser@example.com"

    # Failed login (wrong password)
    res_fail = client.post("/api/login", json={
        "email": "loginuser@example.com",
        "password": "WrongPassword"
    })
    assert res_fail.status_code == 401

    # Logout
    res_logout = client.post("/api/logout")
    assert res_logout.status_code == 200

    # Verify session cleared
    res_me_after = client.get("/api/me")
    assert res_me_after.get_json()["authenticated"] is False

def test_profile_unauthorized_access(client):
    # Access profile without logging in
    res = client.get("/api/profile")
    assert res.status_code == 401
    assert "Authentication required" in res.get_json()["error"]

    res_put = client.put("/api/profile", json={"course": "B.Tech"})
    assert res_put.status_code == 401

def test_profile_lifecycle(client):
    # Register & Login
    client.post("/api/register", json={
        "name": "Dev Student",
        "email": "dev@example.com",
        "password": "Password123"
    })

    # Empty profile initially
    res = client.get("/api/profile")
    assert res.status_code == 200
    assert res.get_json()["profile"] is None

    # Update profile with valid data
    profile_payload = {
        "age": 20,
        "gender": "Female",
        "state": "Tamil Nadu",
        "district": "Madurai",
        "course": "B.Tech",
        "branch": "Electronics",
        "year": 3,
        "percentage": 82.5,
        "cgpa": 8.4,
        "income": 180000.0,
        "category": "OBC",
        "disability_status": "No",
        "achievements": "Robotics Club Lead"
    }
    res_put = client.put("/api/profile", json=profile_payload)
    assert res_put.status_code == 200
    assert res_put.get_json()["profile"]["course"] == "B.Tech"
    assert res_put.get_json()["profile"]["percentage"] == 82.5

    # Verify via GET
    res_get = client.get("/api/profile")
    assert res_get.status_code == 200
    assert res_get.get_json()["profile"]["branch"] == "Electronics"

    # Invalid profile update (e.g. invalid percentage > 100)
    invalid_payload = profile_payload.copy()
    invalid_payload["percentage"] = 150.0
    res_invalid = client.put("/api/profile", json=invalid_payload)
    assert res_invalid.status_code == 400
    assert "Percentage must be between 0.0 and 100.0" in res_invalid.get_json()["error"]
