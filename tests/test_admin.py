import pytest
from app import create_app
from database.seed import seed_database
from models.user import User
from models.scholarship import Scholarship

@pytest.fixture
def app_with_seed(tmp_path):
    test_db = str(tmp_path / "test_admin.db")
    app = create_app("testing")
    app.config["DATABASE_PATH"] = test_db
    app.config["SECRET_KEY"] = "test-secret"
    with app.app_context():
        seed_database(test_db)
    return app

@pytest.fixture
def client(app_with_seed):
    return app_with_seed.test_client()

def test_admin_dashboard_unauthorized_guest(client):
    res = client.get("/admin")
    assert res.status_code == 401

def test_admin_dashboard_forbidden_student(client):
    # Log in as a student
    client.post("/login", data={
        "email": "aarav.sharma@example.com",
        "password": "Password123!"
    })
    res = client.get("/admin")
    assert res.status_code == 403
    assert b"Forbidden" in res.data or b"Admin access required" in res.data

def test_admin_dashboard_success_admin(client):
    # Log in as an admin
    client.post("/login", data={
        "email": "vikram.admin@example.com",
        "password": "Password123!"
    })
    res = client.get("/admin")
    assert res.status_code == 200
    assert b"Scholarship Administration" in res.data
    assert b"ACTIVE SCHEMES" in res.data

def test_admin_crud_api(client):
    # Log in as admin
    client.post("/login", data={
        "email": "vikram.admin@example.com",
        "password": "Password123!"
    })

    # 1. Create scholarship via API
    new_sch = {
        "name": "State Women in STEM Grant",
        "provider": "Department of Higher Education",
        "description": "Full grant for female researchers.",
        "amount": 80000.0,
        "course": "B.Tech",
        "min_percentage": 70.0,
        "max_income": 600000.0,
        "state": "Tamil Nadu",
        "category": "ALL",
        "gender": "Female",
        "official_url": "https://stem.tn.gov.in",
        "status": "ACTIVE"
    }
    res_create = client.post("/api/admin/scholarships", json=new_sch)
    assert res_create.status_code == 201
    created_id = res_create.get_json()["scholarship"]["id"]

    # 2. Update scholarship via API
    update_payload = dict(new_sch, amount=90000.0, status="PENDING_VERIFICATION")
    res_update = client.put(f"/api/admin/scholarships/{created_id}", json=update_payload)
    assert res_update.status_code == 200
    assert res_update.get_json()["scholarship"]["amount"] == 90000.0
    assert res_update.get_json()["scholarship"]["status"] == "PENDING_VERIFICATION"

    # 3. Delete scholarship via API
    res_delete = client.delete(f"/api/admin/scholarships/{created_id}")
    assert res_delete.status_code == 200
    assert "deleted successfully" in res_delete.get_json()["message"]
