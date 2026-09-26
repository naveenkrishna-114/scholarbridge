from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models.user import User, StudentProfile
from models.scholarship import Scholarship, SavedScholarship
from services.recommendation_service import RecommendationService

views_bp = Blueprint("views", __name__)

@views_bp.route("/")
def index():
    if request.headers.get("Accept") == "application/json" or request.args.get("format") == "json":
        return jsonify({
            "message": "Welcome to the Personalized Scholarship Recommendation System API",
            "health_endpoint": "/api/health",
            "documentation": "/README.md"
        }), 200
    return render_template("index.html")

@views_bp.route("/login", methods=["GET"])
def login_view():
    if session.get("user_id"):
        return redirect(url_for("views.recommendations_view"))
    return render_template("login.html")

@views_bp.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    user = User.get_by_email(email)
    if not user or not User.check_password(user["password_hash"], password):
        flash("Invalid email or password. Please try again.", "error")
        return redirect(url_for("views.login_view"))

    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    session["email"] = user["email"]
    session["role"] = user["role"]

    flash(f"Welcome back, {user['name']}!", "success")
    if user["role"] == "admin":
        return redirect(url_for("admin.admin_dashboard"))
    return redirect(url_for("views.recommendations_view"))

@views_bp.route("/register", methods=["GET"])
def register_view():
    if session.get("user_id"):
        return redirect(url_for("views.recommendations_view"))
    return render_template("register.html")

@views_bp.route("/register", methods=["POST"])
def register_post():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    try:
        user = User.create(name=name, email=email, password=password, role="student")
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        session["email"] = user["email"]
        session["role"] = user["role"]

        flash("Account created successfully! Please complete your academic profile.", "success")
        return redirect(url_for("views.profile_view"))
    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for("views.register_view"))
    except Exception:
        flash("Registration failed due to an error.", "error")
        return redirect(url_for("views.register_view"))

@views_bp.route("/logout")
def logout_view():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("views.index"))

@views_bp.route("/profile", methods=["GET"])
def profile_view():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to manage your student profile.", "warning")
        return redirect(url_for("views.login_view"))

    profile = StudentProfile.get_by_user_id(user_id)
    return render_template("profile.html", profile=profile)

@views_bp.route("/profile", methods=["POST"])
def profile_post():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("views.login_view"))

    try:
        cgpa_str = request.form.get("cgpa", "").strip()
        age_str = request.form.get("age", "").strip()
        year_str = request.form.get("year", "1").strip()
        pct_str = request.form.get("percentage", "").strip()
        income_str = request.form.get("income", "").strip()

        if not pct_str:
            raise ValueError("Academic percentage is required.")
        if not income_str:
            raise ValueError("Annual family income is required.")

        profile_data = {
            "course": request.form.get("course", "").strip(),
            "branch": request.form.get("branch", "").strip(),
            "year": int(year_str) if year_str else 1,
            "percentage": float(pct_str),
            "cgpa": float(cgpa_str) if cgpa_str else None,
            "state": request.form.get("state", "").strip(),
            "district": request.form.get("district", "").strip(),
            "gender": request.form.get("gender", "Prefer not to say"),
            "age": int(age_str) if age_str else None,
            "category": request.form.get("category", "General"),
            "income": float(income_str),
            "disability_status": request.form.get("disability_status", "No"),
            "achievements": request.form.get("achievements", "").strip()
        }

        StudentProfile.upsert(user_id, profile_data)
        flash("Profile updated successfully!", "success")
        return redirect(url_for("views.recommendations_view"))
    except ValueError as e:
        flash(f"Invalid input: {e}", "error")
        return redirect(url_for("views.profile_view"))
    except Exception as e:
        flash(f"Error saving profile: {e}", "error")
        return redirect(url_for("views.profile_view"))

@views_bp.route("/recommendations")
def recommendations_view():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to view personalized scholarship recommendations.", "warning")
        return redirect(url_for("views.login_view"))

    profile = StudentProfile.get_by_user_id(user_id)
    if not profile:
        flash("Please complete your profile first to compute recommendations.", "info")
        return redirect(url_for("views.profile_view"))

    rec_service = RecommendationService()
    recommendations = rec_service.get_recommendations(student=profile, user_id=user_id)

    # Saved scholarship IDs
    saved_list = SavedScholarship.list_by_user(user_id)
    saved_ids = {s["id"] for s in saved_list}

    return render_template(
        "recommendations.html",
        recommendations=recommendations,
        student=profile,
        saved_ids=saved_ids
    )

@views_bp.route("/scholarships")
def explore_scholarships():
    search = request.args.get("search", "")
    course = request.args.get("course", "")
    state = request.args.get("state", "")

    scholarships = Scholarship.list_all(
        status="ACTIVE",
        search=search if search else None,
        course=course if course else None,
        state=state if state else None
    )

    return render_template(
        "scholarships_list.html",
        scholarships=scholarships,
        search_term=search,
        selected_course=course,
        selected_state=state
    )

@views_bp.route("/scholarships/<int:scholarship_id>")
def scholarship_detail(scholarship_id: int):
    scholarship = Scholarship.get_by_id(scholarship_id)
    if not scholarship:
        flash("Scholarship not found.", "error")
        return redirect(url_for("views.explore_scholarships"))

    user_id = session.get("user_id")
    is_saved = False
    if user_id:
        is_saved = SavedScholarship.is_saved(user_id, scholarship_id)

    return render_template(
        "scholarship.html",
        scholarship=scholarship,
        is_saved=is_saved
    )

@views_bp.route("/saved")
def saved_view():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to view your saved scholarships.", "warning")
        return redirect(url_for("views.login_view"))

    saved_scholarships = SavedScholarship.list_by_user(user_id)
    return render_template("saved.html", saved_scholarships=saved_scholarships)
