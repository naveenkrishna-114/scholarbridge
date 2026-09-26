from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from routes.auth import login_required, admin_required
from models.scholarship import Scholarship

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin")
@admin_required
def admin_dashboard():
    """Admin dashboard listing all scholarships and management metrics."""
    # List all without status filtering
    all_scholarships = Scholarship.list_all(status=None)
    
    total_count = len(all_scholarships)
    active_count = sum(1 for s in all_scholarships if s["status"] == "ACTIVE")
    expired_count = sum(1 for s in all_scholarships if s["status"] == "EXPIRED")
    pending_count = sum(1 for s in all_scholarships if s["status"] == "PENDING_VERIFICATION")

    return render_template(
        "admin.html",
        scholarships=all_scholarships,
        total_count=total_count,
        active_count=active_count,
        expired_count=expired_count,
        pending_count=pending_count
    )

@admin_bp.route("/admin/scholarships/new", methods=["POST"])
@admin_required
def admin_create_scholarship_form():
    """Handle scholarship creation from admin dashboard web form."""
    form = request.form
    try:
        amount_str = form.get("amount", "").strip()
        min_pct_str = form.get("min_percentage", "").strip()
        max_inc_str = form.get("max_income", "").strip()
        year_str = form.get("year", "").strip()

        data = {
            "name": form.get("name", "").strip(),
            "provider": form.get("provider", "").strip(),
            "description": form.get("description", "").strip(),
            "amount": float(amount_str) if amount_str else None,
            "course": form.get("course", "ALL").strip(),
            "min_percentage": float(min_pct_str) if min_pct_str else 0.0,
            "max_income": float(max_inc_str) if max_inc_str else 10000000.0,
            "state": form.get("state", "ALL").strip(),
            "category": form.get("category", "ALL").strip(),
            "gender": form.get("gender", "ALL").strip(),
            "year": int(year_str) if year_str else None,
            "deadline": form.get("deadline", "").strip() or None,
            "official_url": form.get("official_url", "").strip(),
            "source_url": form.get("source_url", "").strip() or None,
            "last_verified": str(date.today()),
            "status": form.get("status", "ACTIVE").strip()
        }
        Scholarship.create(data)
        flash(f"Scholarship '{data['name']}' added successfully!", "success")
    except ValueError as e:
        flash(f"Validation error: {e}", "error")
    except Exception as e:
        flash(f"Failed to add scholarship: {e}", "error")

    return redirect(url_for("admin.admin_dashboard"))

@admin_bp.route("/admin/scholarships/<int:scholarship_id>/status", methods=["POST"])
@admin_required
def admin_toggle_status(scholarship_id: int):
    """Toggle or update scholarship status."""
    new_status = request.form.get("status")
    sch = Scholarship.get_by_id(scholarship_id)
    if not sch:
        flash("Scholarship not found.", "error")
        return redirect(url_for("admin.admin_dashboard"))

    if new_status in ("ACTIVE", "EXPIRED", "PENDING_VERIFICATION"):
        sch["status"] = new_status
        sch["last_verified"] = str(date.today())
        Scholarship.update(scholarship_id, sch)
        flash(f"Updated status of '{sch['name']}' to {new_status}.", "success")
    else:
        flash("Invalid status specified.", "error")

    return redirect(url_for("admin.admin_dashboard"))

@admin_bp.route("/admin/scholarships/<int:scholarship_id>/delete", methods=["POST"])
@admin_required
def admin_delete_scholarship_form(scholarship_id: int):
    """Delete scholarship record."""
    sch = Scholarship.get_by_id(scholarship_id)
    if sch:
        Scholarship.delete(scholarship_id)
        flash(f"Deleted scholarship '{sch['name']}'.", "info")
    else:
        flash("Scholarship not found.", "error")

    return redirect(url_for("admin.admin_dashboard"))

# REST API Endpoints per Section 20
@admin_bp.route("/api/admin/scholarships", methods=["POST"])
@admin_required
def api_admin_create_scholarship():
    data = request.get_json(silent=True) or {}
    try:
        if not data.get("last_verified"):
            data["last_verified"] = str(date.today())
        created = Scholarship.create(data)
        return jsonify({
            "message": "Scholarship created successfully.",
            "scholarship": created
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route("/api/admin/scholarships/<int:scholarship_id>", methods=["PUT"])
@admin_required
def api_admin_update_scholarship(scholarship_id: int):
    data = request.get_json(silent=True) or {}
    existing = Scholarship.get_by_id(scholarship_id)
    if not existing:
        return jsonify({"error": "Scholarship not found."}), 404

    try:
        updated = Scholarship.update(scholarship_id, data)
        return jsonify({
            "message": "Scholarship updated successfully.",
            "scholarship": updated
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route("/api/admin/scholarships/<int:scholarship_id>", methods=["DELETE"])
@admin_required
def api_admin_delete_scholarship(scholarship_id: int):
    existing = Scholarship.get_by_id(scholarship_id)
    if not existing:
        return jsonify({"error": "Scholarship not found."}), 404

    Scholarship.delete(scholarship_id)
    return jsonify({"message": f"Scholarship {scholarship_id} deleted successfully."}), 200
