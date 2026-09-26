import pytest
from app import create_app
from database.seed import seed_database
from database.db import query_db
from models.user import User
from services.eligibility_service import EligibilityService

@pytest.fixture
def app_with_seed(tmp_path):
    test_db = str(tmp_path / "test_sec.db")
    app = create_app("testing")
    app.config["DATABASE_PATH"] = test_db
    app.config["SECRET_KEY"] = "secure-test-secret"
    with app.app_context():
        seed_database(test_db)
    return app

@pytest.fixture
def client(app_with_seed):
    return app_with_seed.test_client()

def test_sql_injection_defense_in_auth_and_search(client, app_with_seed):
    # 1. Attempt SQL injection in login
    sqli_payload = "' OR '1'='1' --"
    res = client.post("/api/login", json={
        "email": sqli_payload,
        "password": "any"
    })
    assert res.status_code in (400, 401)

    # 2. Attempt SQL injection in scholarship search
    search_sqli = "'; DROP TABLE scholarships; --"
    res_search = client.get(f"/api/scholarships?search={search_sqli}")
    assert res_search.status_code == 200

    # Verify scholarships table still exists and has records
    with app_with_seed.app_context():
        count_row = query_db("SELECT count(*) as total FROM scholarships", one=True)
        assert count_row["total"] > 0

def test_password_hashing_security(app_with_seed):
    with app_with_seed.app_context():
        # Inspect raw database rows for users
        rows = query_db("SELECT email, password_hash FROM users")
        assert len(rows) > 0
        for r in rows:
            pwd_hash = r["password_hash"]
            # Must not be plain text
            assert pwd_hash != "Password123!"
            # Must start with standard secure hash algorithms (scrypt or pbkdf2)
            assert pwd_hash.startswith("scrypt:") or pwd_hash.startswith("pbkdf2:")

def test_privilege_escalation_defense(client):
    # Attempt to self-assign admin role through public registration
    res = client.post("/api/register", json={
        "name": "Hacker Aspirant",
        "email": "hacker@example.com",
        "password": "StrongPassword123!",
        "role": "admin"
    })
    # Public endpoint forces role to 'student'
    assert res.status_code == 201
    assert res.get_json()["user"]["role"] == "student"

    # Attempt to access admin routes with newly created account
    res_admin = client.get("/admin")
    assert res_admin.status_code == 403

def test_input_validation_boundary_limits(client):
    # Register & Login
    client.post("/api/register", json={
        "name": "Boundary Tester",
        "email": "boundary@example.com",
        "password": "Password123!"
    })

    # Percentage > 100 rejected
    res_high_pct = client.put("/api/profile", json={
        "course": "B.Tech",
        "state": "Tamil Nadu",
        "percentage": 105.0,
        "income": 200000.0
    })
    assert res_high_pct.status_code == 400

    # Negative income rejected
    res_neg_inc = client.put("/api/profile", json={
        "course": "B.Tech",
        "state": "Tamil Nadu",
        "percentage": 85.0,
        "income": -50000.0
    })
    assert res_neg_inc.status_code == 400

def test_xss_protection_in_templates(client):
    # Login
    client.post("/api/register", json={
        "name": "<script>alert('XSS')</script>",
        "email": "xss@example.com",
        "password": "Password123!"
    })
    res = client.get("/")
    assert res.status_code == 200
    # Must be escaped by Jinja2, not rendered raw
    assert b"<script>alert('XSS')</script>" not in res.data
    assert b"&lt;script&gt;alert(&#39;XSS&#39;)&lt;/script&gt;" in res.data or b"alert" not in res.data

def test_expired_scholarship_security_rule():
    # Expired status must never be deemed eligible
    expired_scholarship = {
        "id": 999,
        "name": "Old Expired Scheme",
        "min_percentage": 50.0,
        "max_income": 1000000.0,
        "state": "ALL",
        "course": "ALL",
        "deadline": "2020-01-01",
        "status": "EXPIRED"
    }
    student = {
        "course": "B.Tech",
        "percentage": 90.0,
        "income": 100000.0,
        "state": "Delhi"
    }
    is_eligible, details = EligibilityService.evaluate(student, expired_scholarship)
    assert is_eligible is False
    assert any("expired" in f.lower() or "passed" in f.lower() for f in details["failed_criteria"])
