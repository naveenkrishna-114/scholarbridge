from werkzeug.security import generate_password_hash, check_password_hash
from database.db import query_db, execute_db

class User:
    """User entity and authentication helper."""

    @staticmethod
    def hash_password(password: str) -> str:
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        return generate_password_hash(password)

    @staticmethod
    def check_password(password_hash: str, password: str) -> bool:
        return check_password_hash(password_hash, password)

    @staticmethod
    def create(name: str, email: str, password: str, role: str = "student", db_path=None):
        if not name or not name.strip():
            raise ValueError("Name cannot be empty.")
        if not email or "@" not in email:
            raise ValueError("A valid email address is required.")
        
        email_clean = email.strip().lower()
        existing = User.get_by_email(email_clean, db_path=db_path)
        if existing:
            raise ValueError(f"An account with email {email_clean} already exists.")

        pwd_hash = User.hash_password(password)
        query = """
            INSERT INTO users (name, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        """
        user_id = execute_db(query, (name.strip(), email_clean, pwd_hash, role), db_path=db_path)
        return User.get_by_id(user_id, db_path=db_path)

    @staticmethod
    def get_by_id(user_id: int, db_path=None):
        query = "SELECT id, name, email, role, created_at, updated_at FROM users WHERE id = ?"
        row = query_db(query, (user_id,), one=True, db_path=db_path)
        return dict(row) if row else None

    @staticmethod
    def get_by_email(email: str, db_path=None):
        query = "SELECT id, name, email, password_hash, role, created_at, updated_at FROM users WHERE email = ?"
        row = query_db(query, (email.strip().lower(),), one=True, db_path=db_path)
        return dict(row) if row else None


class StudentProfile:
    """Student profile data access object and validation."""

    @staticmethod
    def validate_profile_data(data: dict):
        """Validate profile input fields."""
        errors = []
        if not data.get("state"):
            errors.append("State is required.")
        if not data.get("course"):
            errors.append("Course is required.")

        try:
            year = int(data.get("year", 1))
            if year < 1 or year > 8:
                errors.append("Year of study must be between 1 and 8.")
        except (ValueError, TypeError):
            errors.append("Valid year of study is required.")

        try:
            percentage = float(data.get("percentage", -1))
            if percentage < 0.0 or percentage > 100.0:
                errors.append("Percentage must be between 0.0 and 100.0.")
        except (ValueError, TypeError):
            errors.append("Valid percentage number is required.")

        try:
            income = float(data.get("income", -1))
            if income < 0.0:
                errors.append("Annual family income must be non-negative.")
        except (ValueError, TypeError):
            errors.append("Valid annual family income is required.")

        if errors:
            raise ValueError("; ".join(errors))

    @staticmethod
    def get_by_user_id(user_id: int, db_path=None):
        query = "SELECT * FROM student_profiles WHERE user_id = ?"
        row = query_db(query, (user_id,), one=True, db_path=db_path)
        return dict(row) if row else None

    @staticmethod
    def upsert(user_id: int, profile_data: dict, db_path=None):
        StudentProfile.validate_profile_data(profile_data)
        existing = StudentProfile.get_by_user_id(user_id, db_path=db_path)

        # Clean optional numeric conversions
        age_val = None
        if profile_data.get("age") not in (None, ""):
            try:
                age_val = int(profile_data["age"])
            except (ValueError, TypeError):
                age_val = None

        cgpa_val = None
        if profile_data.get("cgpa") not in (None, ""):
            try:
                cgpa_val = float(profile_data["cgpa"])
            except (ValueError, TypeError):
                cgpa_val = None

        params = (
            age_val,
            profile_data.get("gender") or "Prefer not to say",
            (profile_data.get("state") or "").strip(),
            (profile_data.get("district") or "").strip() or None,
            (profile_data.get("course") or "").strip(),
            (profile_data.get("branch") or "").strip() or None,
            int(profile_data.get("year") or 1),
            float(profile_data.get("percentage") or 0.0),
            cgpa_val,
            float(profile_data.get("income") or 0.0),
            profile_data.get("category") or "General",
            profile_data.get("disability_status") or "No",
            (profile_data.get("achievements") or "").strip(),
        )

        if existing:
            query = """
                UPDATE student_profiles
                SET age = ?, gender = ?, state = ?, district = ?, course = ?,
                    branch = ?, year = ?, percentage = ?, cgpa = ?, income = ?,
                    category = ?, disability_status = ?, achievements = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """
            execute_db(query, params + (user_id,), db_path=db_path)
        else:
            query = """
                INSERT INTO student_profiles (
                    age, gender, state, district, course,
                    branch, year, percentage, cgpa, income,
                    category, disability_status, achievements, user_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            execute_db(query, params + (user_id,), db_path=db_path)

        return StudentProfile.get_by_user_id(user_id, db_path=db_path)
