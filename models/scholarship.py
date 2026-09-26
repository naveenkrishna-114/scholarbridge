import json
from database.db import query_db, execute_db

class Scholarship:
    """Scholarship model and database operations."""

    @staticmethod
    def validate_scholarship_data(data: dict):
        errors = []
        if not data.get("name") or not str(data["name"]).strip():
            errors.append("Scholarship name is required.")
        if not data.get("provider") or not str(data["provider"]).strip():
            errors.append("Provider is required.")
        if not data.get("official_url") or not str(data["official_url"]).strip():
            errors.append("Official application URL is required.")
        
        status = data.get("status", "ACTIVE")
        if status not in ("ACTIVE", "EXPIRED", "PENDING_VERIFICATION"):
            errors.append("Status must be ACTIVE, EXPIRED, or PENDING_VERIFICATION.")

        if errors:
            raise ValueError("; ".join(errors))

    @staticmethod
    def _safe_float(val, default=0.0):
        if val is None or val == "":
            return default
        try:
            return float(val)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def _safe_int(val, default=None):
        if val is None or val == "":
            return default
        try:
            return int(val)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def create(data: dict, db_path=None):
        Scholarship.validate_scholarship_data(data)
        query = """
            INSERT INTO scholarships (
                name, provider, description, amount, course,
                min_percentage, max_income, state, category, gender,
                year, age_min, age_max, other_requirements, start_date,
                deadline, official_url, source_url, last_verified, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            str(data.get("name", "")).strip(),
            str(data.get("provider", "")).strip(),
            str(data.get("description", "") or "").strip(),
            Scholarship._safe_float(data.get("amount"), default=None),
            str(data.get("course", "ALL") or "ALL").strip(),
            Scholarship._safe_float(data.get("min_percentage"), default=0.0),
            Scholarship._safe_float(data.get("max_income"), default=10000000.0),
            str(data.get("state", "ALL") or "ALL").strip(),
            str(data.get("category", "ALL") or "ALL").strip(),
            str(data.get("gender", "ALL") or "ALL").strip(),
            Scholarship._safe_int(data.get("year")),
            Scholarship._safe_int(data.get("age_min")),
            Scholarship._safe_int(data.get("age_max")),
            str(data.get("other_requirements", "") or "").strip(),
            str(data.get("start_date", "")).strip() or None if data.get("start_date") else None,
            str(data.get("deadline", "")).strip() or None if data.get("deadline") else None,
            str(data.get("official_url", "")).strip(),
            str(data.get("source_url", "")).strip() or None if data.get("source_url") else None,
            str(data.get("last_verified", "")).strip() or None if data.get("last_verified") else None,
            data.get("status", "ACTIVE"),
        )
        scholarship_id = execute_db(query, params, db_path=db_path)
        return Scholarship.get_by_id(scholarship_id, db_path=db_path)

    @staticmethod
    def get_by_id(scholarship_id: int, db_path=None):
        query = "SELECT * FROM scholarships WHERE id = ?"
        row = query_db(query, (scholarship_id,), one=True, db_path=db_path)
        return dict(row) if row else None

    @staticmethod
    def list_all(status: str = "ACTIVE", search: str = None, course: str = None, state: str = None, db_path=None):
        query = "SELECT * FROM scholarships WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status)

        if course and course != "ALL":
            query += " AND (course = 'ALL' OR course = ?)"
            params.append(course)

        if state and state != "ALL":
            query += " AND (state = 'ALL' OR state = ?)"
            params.append(state)

        if search and search.strip():
            query += " AND (name LIKE ? OR provider LIKE ? OR description LIKE ?)"
            term = f"%{search.strip()}%"
            params.extend([term, term, term])

        query += " ORDER BY deadline ASC, id DESC"
        rows = query_db(query, tuple(params), db_path=db_path)
        return [dict(r) for r in rows]

    @staticmethod
    def update(scholarship_id: int, data: dict, db_path=None):
        Scholarship.validate_scholarship_data(data)
        query = """
            UPDATE scholarships
            SET name = ?, provider = ?, description = ?, amount = ?, course = ?,
                min_percentage = ?, max_income = ?, state = ?, category = ?, gender = ?,
                year = ?, age_min = ?, age_max = ?, other_requirements = ?, start_date = ?,
                deadline = ?, official_url = ?, source_url = ?, last_verified = ?, status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        params = (
            str(data.get("name", "")).strip(),
            str(data.get("provider", "")).strip(),
            str(data.get("description", "") or "").strip(),
            Scholarship._safe_float(data.get("amount"), default=None),
            str(data.get("course", "ALL") or "ALL").strip(),
            Scholarship._safe_float(data.get("min_percentage"), default=0.0),
            Scholarship._safe_float(data.get("max_income"), default=10000000.0),
            str(data.get("state", "ALL") or "ALL").strip(),
            str(data.get("category", "ALL") or "ALL").strip(),
            str(data.get("gender", "ALL") or "ALL").strip(),
            Scholarship._safe_int(data.get("year")),
            Scholarship._safe_int(data.get("age_min")),
            Scholarship._safe_int(data.get("age_max")),
            str(data.get("other_requirements", "") or "").strip(),
            str(data.get("start_date", "")).strip() or None if data.get("start_date") else None,
            str(data.get("deadline", "")).strip() or None if data.get("deadline") else None,
            str(data.get("official_url", "")).strip(),
            str(data.get("source_url", "")).strip() or None if data.get("source_url") else None,
            str(data.get("last_verified", "")).strip() or None if data.get("last_verified") else None,
            data.get("status", "ACTIVE"),
            scholarship_id
        )
        execute_db(query, params, db_path=db_path)
        return Scholarship.get_by_id(scholarship_id, db_path=db_path)

    @staticmethod
    def delete(scholarship_id: int, db_path=None):
        query = "DELETE FROM scholarships WHERE id = ?"
        execute_db(query, (scholarship_id,), db_path=db_path)
        return True


class SavedScholarship:
    """Manages student bookmarked / saved scholarships."""

    @staticmethod
    def save(user_id: int, scholarship_id: int, db_path=None):
        query = """
            INSERT OR IGNORE INTO saved_scholarships (user_id, scholarship_id)
            VALUES (?, ?)
        """
        execute_db(query, (user_id, scholarship_id), db_path=db_path)
        return True

    @staticmethod
    def remove(user_id: int, scholarship_id: int, db_path=None):
        query = "DELETE FROM saved_scholarships WHERE user_id = ? AND scholarship_id = ?"
        execute_db(query, (user_id, scholarship_id), db_path=db_path)
        return True

    @staticmethod
    def list_by_user(user_id: int, db_path=None):
        query = """
            SELECT s.*, ss.created_at as saved_at
            FROM saved_scholarships ss
            JOIN scholarships s ON ss.scholarship_id = s.id
            WHERE ss.user_id = ?
            ORDER BY ss.created_at DESC
        """
        rows = query_db(query, (user_id,), db_path=db_path)
        return [dict(r) for r in rows]

    @staticmethod
    def is_saved(user_id: int, scholarship_id: int, db_path=None):
        query = "SELECT id FROM saved_scholarships WHERE user_id = ? AND scholarship_id = ?"
        row = query_db(query, (user_id, scholarship_id), one=True, db_path=db_path)
        return bool(row)


class RecommendationRecord:
    """Stores recommendation runs for history and audit tracking."""

    @staticmethod
    def save(user_id: int, scholarship_id: int, score: float, explanation: dict, db_path=None):
        query = """
            INSERT INTO recommendations (user_id, scholarship_id, score, explanation_json)
            VALUES (?, ?, ?, ?)
        """
        execute_db(query, (user_id, scholarship_id, float(score), json.dumps(explanation)), db_path=db_path)

    @staticmethod
    def list_by_user(user_id: int, limit: int = 20, db_path=None):
        query = """
            SELECT r.*, s.name, s.provider, s.amount, s.deadline, s.official_url
            FROM recommendations r
            JOIN scholarships s ON r.scholarship_id = s.id
            WHERE r.user_id = ?
            ORDER BY r.created_at DESC, r.score DESC
            LIMIT ?
        """
        rows = query_db(query, (user_id, limit), db_path=db_path)
        results = []
        for r in rows:
            item = dict(r)
            if item.get("explanation_json"):
                try:
                    item["explanation"] = json.loads(item["explanation_json"])
                except Exception:
                    item["explanation"] = {}
            results.append(item)
        return results
