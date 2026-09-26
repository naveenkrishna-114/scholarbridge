import csv
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from database.db import init_db, get_db_path
from models.user import User, StudentProfile
from models.scholarship import Scholarship

def seed_database(db_path=None):
    """Seed the database with initial schema and sample CSV datasets."""
    target_db = db_path or get_db_path()
    print(f"Initializing database at: {target_db}")
    init_db(target_db)

    # 1. Seed Scholarships from CSV
    scholarships_csv = BASE_DIR / "data" / "scholarships.csv"
    if scholarships_csv.exists():
        with open(scholarships_csv, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                status_val = (row.get("status") or "ACTIVE").strip().upper()
                cleaned_row = {
                    "name": row["name"].strip(),
                    "provider": row["provider"].strip(),
                    "description": row.get("description", "").strip(),
                    "amount": float(row["amount"]) if row.get("amount") else None,
                    "course": row.get("course", "ALL").strip(),
                    "min_percentage": float(row["min_percentage"]) if row.get("min_percentage") else 0.0,
                    "max_income": float(row["max_income"]) if row.get("max_income") else 10000000.0,
                    "state": row.get("state", "ALL").strip(),
                    "category": row.get("category", "ALL").strip(),
                    "gender": row.get("gender", "ALL").strip(),
                    "year": int(row["year"]) if row.get("year") else None,
                    "age_min": int(row["age_min"]) if row.get("age_min") else None,
                    "age_max": int(row["age_max"]) if row.get("age_max") else None,
                    "other_requirements": row.get("other_requirements", "").strip(),
                    "start_date": row.get("start_date", "").strip() or None,
                    "deadline": row.get("deadline", "").strip() or None,
                    "official_url": row["official_url"].strip(),
                    "source_url": row.get("source_url", "").strip() or None,
                    "last_verified": row.get("last_verified", "").strip() or None,
                    "status": status_val
                }
                existing_sch = Scholarship.list_all(status=None, search=cleaned_row["name"], db_path=target_db)
                matching = next((s for s in existing_sch if s["name"].lower() == cleaned_row["name"].lower()), None)
                if matching:
                    Scholarship.update(matching["id"], cleaned_row, db_path=target_db)
                else:
                    Scholarship.create(cleaned_row, db_path=target_db)
                count += 1
            print(f"Loaded / synchronized {count} sample scholarships in database.")

    # 2. Seed Users & Profiles from CSV
    students_csv = BASE_DIR / "data" / "sample_students.csv"
    if students_csv.exists():
        with open(students_csv, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                email_clean = row["email"].strip().lower()
                user = User.get_by_email(email_clean, db_path=target_db)
                if not user:
                    user = User.create(
                        name=row["name"].strip(),
                        email=email_clean,
                        password="Password123!",
                        role=row.get("role", "student").strip(),
                        db_path=target_db
                    )
                if row.get("role", "").strip() != "admin":
                    StudentProfile.upsert(
                        user_id=user["id"],
                        profile_data={
                            "age": int(row["age"]) if row.get("age") and row["age"].strip() else None,
                            "gender": row.get("gender", "").strip() or None,
                            "state": row.get("state", "").strip(),
                            "district": row.get("district", "").strip() or None,
                            "course": row.get("course", "").strip(),
                            "branch": row.get("branch", "").strip() or None,
                            "year": int(row["year"]),
                            "percentage": float(row["percentage"]),
                            "cgpa": float(row["cgpa"]) if row.get("cgpa") and row["cgpa"].strip() else None,
                            "income": float(row["income"]),
                            "category": row.get("category", "General").strip(),
                            "disability_status": row.get("disability_status", "No").strip(),
                            "achievements": row.get("achievements", "").strip()
                        },
                        db_path=target_db
                    )
                count += 1
            print(f"Loaded {count} sample users and profiles.")

if __name__ == "__main__":
    seed_database()
