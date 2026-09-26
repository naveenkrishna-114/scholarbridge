import pytest
from app import create_app
from database.db import init_db
from database.seed import seed_database
from services.recommendation_service import RecommendationService
from services.explanation_service import ExplanationService

@pytest.fixture
def app_with_seed(tmp_path):
    test_db = str(tmp_path / "test_rec.db")
    app = create_app("testing")
    app.config["DATABASE_PATH"] = test_db
    with app.app_context():
        seed_database(test_db)
    return app

@pytest.fixture
def client(app_with_seed):
    return app_with_seed.test_client()

def test_deterministic_recommendation_scoring(app_with_seed):
    with app_with_seed.app_context():
        service = RecommendationService()

        # Benchmark Profile: Tamil Nadu B.Tech 2nd Year student
        student = {
            "name": "Aarav",
            "state": "Tamil Nadu",
            "course": "B.Tech",
            "branch": "Computer Science",
            "year": 2,
            "percentage": 84.0,
            "income": 200000.0,
            "category": "General",
            "gender": "Male"
        }

        recommendations = service.get_recommendations(student, db_path=app_with_seed.config["DATABASE_PATH"])
        assert len(recommendations) > 0

        # Check ranking order (descending scores)
        scores = [r["match_score"] for r in recommendations]
        assert scores == sorted(scores, reverse=True)

        # Check top recommendation is highly relevant
        top = recommendations[0]
        assert top["match_score"] >= 0.75
        assert "explanation" in top
        assert len(top["explanation"]["reasons"]) > 0
        assert "disclaimer" in top["explanation"]
        assert top["official_url"].startswith("http")

        # Verify expired scholarships are pruned
        assert not any(r["status"] == "EXPIRED" for r in recommendations)
        assert not any("Expired" in r["name"] for r in recommendations)

def test_recommendation_api_endpoint(client):
    # Public recommendation payload test
    student_payload = {
        "state": "Maharashtra",
        "course": "B.Tech",
        "year": 1,
        "percentage": 88.0,
        "income": 250000.0,
        "category": "OBC",
        "gender": "Female"
    }

    res = client.post("/api/recommend", json={"profile": student_payload})
    assert res.status_code == 200
    data = res.get_json()
    assert data["total_matches"] > 0
    recs = data["recommendations"]

    # Since student is Female, AICTE Pragati should be matched and ranked high
    pragati_match = next((r for r in recs if "Pragati" in r["name"]), None)
    assert pragati_match is not None
    assert pragati_match["match_score"] >= 0.7

def test_saved_scholarship_endpoints(client):
    # Register and login user
    client.post("/api/register", json={
        "name": "Save User",
        "email": "saveuser@example.com",
        "password": "Password123"
    })

    # Get scholarship list
    res_list = client.get("/api/scholarships")
    assert res_list.status_code == 200
    sch_id = res_list.get_json()["scholarships"][0]["id"]

    # Bookmark scholarship
    res_save = client.post(f"/api/saved/{sch_id}")
    assert res_save.status_code == 200

    # Retrieve bookmarks
    res_saved = client.get("/api/saved")
    assert res_saved.status_code == 200
    assert any(s["id"] == sch_id for s in res_saved.get_json()["saved_scholarships"])

    # Remove bookmark
    res_del = client.delete(f"/api/saved/{sch_id}")
    assert res_del.status_code == 200

    # Verify bookmark removed
    res_after = client.get("/api/saved")
    assert not any(s["id"] == sch_id for s in res_after.get_json()["saved_scholarships"])
