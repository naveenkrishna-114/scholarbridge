from flask import Blueprint, request, jsonify, session
from routes.auth import login_required
from models.user import StudentProfile, User

student_bp = Blueprint("student", __name__, url_prefix="/api")

@student_bp.route("/profile", methods=["GET"])
@login_required
def get_profile():
    """Retrieve the logged in student's profile."""
    user_id = session.get("user_id")
    user = User.get_by_id(user_id)
    profile = StudentProfile.get_by_user_id(user_id)

    return jsonify({
        "user": user,
        "profile": profile
    }), 200

@student_bp.route("/profile", methods=["PUT"])
@login_required
def update_profile():
    """Update or create student profile attributes."""
    user_id = session.get("user_id")
    data = request.get_json(silent=True) or {}

    try:
        updated_profile = StudentProfile.upsert(user_id, data)
        return jsonify({
            "message": "Profile updated successfully.",
            "profile": updated_profile
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to update profile due to an unexpected error."}), 500
