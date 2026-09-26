from flask import Blueprint, request, jsonify, session
from routes.auth import login_required
from models.user import StudentProfile
from models.scholarship import Scholarship, SavedScholarship, RecommendationRecord
from services.recommendation_service import RecommendationService

scholarships_bp = Blueprint("scholarships", __name__, url_prefix="/api")

@scholarships_bp.route("/scholarships", methods=["GET"])
def list_scholarships():
    """List and search scholarships with query filters."""
    search = request.args.get("search")
    course = request.args.get("course")
    state = request.args.get("state")
    status = request.args.get("status", "ACTIVE")

    scholarships = Scholarship.list_all(
        status=status,
        search=search,
        course=course,
        state=state
    )
    return jsonify({
        "count": len(scholarships),
        "scholarships": scholarships
    }), 200

@scholarships_bp.route("/scholarships/<int:scholarship_id>", methods=["GET"])
def get_scholarship(scholarship_id: int):
    """Retrieve full details of a specific scholarship."""
    scholarship = Scholarship.get_by_id(scholarship_id)
    if not scholarship:
        return jsonify({"error": "Scholarship not found."}), 404

    # Check if saved by current user
    user_id = session.get("user_id")
    is_saved = False
    if user_id:
        is_saved = SavedScholarship.is_saved(user_id, scholarship_id)

    return jsonify({
        "scholarship": scholarship,
        "is_saved": is_saved
    }), 200

@scholarships_bp.route("/recommend", methods=["POST"])
def get_recommendations():
    """
    Generate personalized scholarship recommendations:
    - If user is logged in, can use stored student profile.
    - Alternatively, accept student profile payload directly in request body.
    """
    user_id = session.get("user_id")
    payload = request.get_json(silent=True) or {}

    student_profile = None

    if user_id:
        student_profile = StudentProfile.get_by_user_id(user_id)

    # Allow overriding or providing profile directly
    if payload.get("profile"):
        student_profile = payload["profile"]
    elif not student_profile and payload:
        student_profile = payload

    if not student_profile:
        return jsonify({
            "error": "Student profile information is required to generate recommendations. Please complete your profile."
        }), 400

    rec_service = RecommendationService()
    recommendations = rec_service.get_recommendations(
        student=student_profile,
        user_id=user_id,
        save_history=(user_id is not None)
    )

    return jsonify({
        "total_matches": len(recommendations),
        "recommendations": recommendations
    }), 200

@scholarships_bp.route("/saved", methods=["GET"])
@login_required
def get_saved_scholarships():
    """Retrieve all scholarships saved/bookmarked by current user."""
    user_id = session.get("user_id")
    saved = SavedScholarship.list_by_user(user_id)
    return jsonify({
        "count": len(saved),
        "saved_scholarships": saved
    }), 200

@scholarships_bp.route("/saved/<int:scholarship_id>", methods=["POST"])
@login_required
def save_scholarship(scholarship_id: int):
    """Bookmark a scholarship."""
    user_id = session.get("user_id")
    sch = Scholarship.get_by_id(scholarship_id)
    if not sch:
        return jsonify({"error": "Scholarship not found."}), 404

    SavedScholarship.save(user_id, scholarship_id)
    return jsonify({"message": "Scholarship bookmarked successfully."}), 200

@scholarships_bp.route("/saved/<int:scholarship_id>", methods=["DELETE"])
@login_required
def remove_saved_scholarship(scholarship_id: int):
    """Remove a bookmarked scholarship."""
    user_id = session.get("user_id")
    SavedScholarship.remove(user_id, scholarship_id)
    return jsonify({"message": "Scholarship removed from bookmarks."}), 200

@scholarships_bp.route("/recommendations/history", methods=["GET"])
@login_required
def get_recommendation_history():
    """Retrieve audit history of previously generated recommendations."""
    user_id = session.get("user_id")
    history = RecommendationRecord.list_by_user(user_id, limit=20)
    return jsonify({
        "count": len(history),
        "history": history
    }), 200
