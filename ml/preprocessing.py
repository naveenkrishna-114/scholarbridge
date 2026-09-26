import re
from typing import Dict, Any, List

class DataPreprocessor:
    """Preprocesses and extracts structured features from student profiles and scholarship data."""

    @staticmethod
    def clean_text(text: str) -> str:
        """Sanitize and normalize string text."""
        if not text:
            return ""
        # Lowercase and remove excessive whitespace and special characters
        cleaned = re.sub(r"[^\w\s]", " ", str(text).lower())
        return " ".join(cleaned.split())

    @classmethod
    def create_student_document(cls, student: Dict[str, Any]) -> str:
        """
        Assemble a rich textual representation of a student profile for semantic vectorization.
        """
        tokens = []

        course = student.get("course") or ""
        branch = student.get("branch") or ""
        state = student.get("state") or ""
        category = student.get("category") or ""
        gender = student.get("gender") or ""
        achievements = student.get("achievements") or ""

        if course:
            tokens.append(f"course_{cls.clean_text(course)}")
            tokens.append(cls.clean_text(course))
        if branch:
            tokens.append(f"branch_{cls.clean_text(branch)}")
            tokens.append(cls.clean_text(branch))
        if state:
            tokens.append(f"state_{cls.clean_text(state)}")
            tokens.append(cls.clean_text(state))
        if category and category.lower() != "general":
            tokens.append(f"category_{cls.clean_text(category)}")
            tokens.append(cls.clean_text(category))
        if gender and gender.lower() != "all":
            tokens.append(f"gender_{cls.clean_text(gender)}")

        # Academic bands
        pct = float(student.get("percentage") or 0.0)
        if pct >= 85.0:
            tokens.append("distinction high_merit excellence topper")
        elif pct >= 75.0:
            tokens.append("first_class merit high_performance")
        elif pct >= 60.0:
            tokens.append("good_academic_record pass_with_merit")

        # Income bands
        inc = float(student.get("income") or 0.0)
        if inc <= 250000.0:
            tokens.append("low_income economically_weaker_section need_based high_need")
        elif inc <= 600000.0:
            tokens.append("middle_income moderate_need financial_aid")

        if achievements:
            tokens.append(cls.clean_text(achievements))

        return " ".join(tokens)

    @classmethod
    def create_scholarship_document(cls, scholarship: Dict[str, Any]) -> str:
        """
        Assemble a rich textual representation of a scholarship for semantic vectorization.
        """
        tokens = [
            cls.clean_text(scholarship.get("name")),
            cls.clean_text(scholarship.get("provider")),
            cls.clean_text(scholarship.get("description")),
            cls.clean_text(scholarship.get("other_requirements"))
        ]

        course = scholarship.get("course") or "ALL"
        state = scholarship.get("state") or "ALL"
        category = scholarship.get("category") or "ALL"
        gender = scholarship.get("gender") or "ALL"

        if course.upper() != "ALL":
            tokens.append(f"course_{cls.clean_text(course)}")
            tokens.append(cls.clean_text(course))
        if state.upper() != "ALL":
            tokens.append(f"state_{cls.clean_text(state)}")
            tokens.append(cls.clean_text(state))
        if category.upper() != "ALL":
            tokens.append(f"category_{cls.clean_text(category)}")
            tokens.append(cls.clean_text(category))
        if gender.upper() != "ALL":
            tokens.append(f"gender_{cls.clean_text(gender)}")
            tokens.append(cls.clean_text(gender))

        # Minimum percentage tags
        min_pct = float(scholarship.get("min_percentage") or 0.0)
        if min_pct >= 75.0:
            tokens.append("high_merit distinction excellence")
        elif min_pct >= 60.0:
            tokens.append("merit first_class")

        # Income limitation tags
        max_inc = float(scholarship.get("max_income") or 10000000.0)
        if max_inc <= 300000.0:
            tokens.append("economically_weaker_section need_based low_income")
        elif max_inc <= 800000.0:
            tokens.append("financial_aid moderate_need")

        return " ".join(filter(None, tokens))
