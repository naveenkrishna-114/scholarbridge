from datetime import datetime, date
from typing import Tuple, Dict, Any, List

def _safe_float(val, default=None):
    if val is None or val == "":
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

def _safe_int(val, default=None):
    if val is None or val == "":
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default

class EligibilityService:
    """Evaluates hard rule-based constraints between student profile and scholarship criteria."""

    @staticmethod
    def _is_expired(scholarship: Dict[str, Any]) -> bool:
        """Check if scholarship status is marked EXPIRED or past deadline."""
        if scholarship.get("status") == "EXPIRED":
            return True
        deadline_str = scholarship.get("deadline")
        if deadline_str:
            try:
                deadline_dt = datetime.strptime(str(deadline_str).strip(), "%Y-%m-%d").date()
                if deadline_dt < date.today():
                    return True
            except (ValueError, TypeError):
                pass
        return False

    @classmethod
    def evaluate(cls, student: Dict[str, Any], scholarship: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Evaluate full eligibility for a student against a single scholarship.
        Returns:
            is_eligible (bool)
            details (dict with passed_criteria, failed_criteria, verification_items)
        """
        passed = []
        failed = []
        verification = []

        # 1. Active status & deadline check
        if cls._is_expired(scholarship):
            failed.append("Scholarship deadline has passed or record is inactive.")
            return False, {
                "passed_criteria": passed,
                "failed_criteria": failed,
                "verification_items": ["Scholarship is expired"]
            }

        # 2. Academic Performance check
        min_pct = _safe_float(scholarship.get("min_percentage"), 0.0)
        student_pct = _safe_float(student.get("percentage"))
        if min_pct is not None and min_pct > 0.0:
            if student_pct is None:
                failed.append("Academic percentage is missing in student profile.")
            elif student_pct < min_pct:
                failed.append(f"Academic percentage ({student_pct}%) is below minimum required ({min_pct}%).")
            else:
                passed.append(f"Minimum academic percentage satisfied ({student_pct}% >= {min_pct}%).")
        else:
            passed.append("No minimum academic percentage constraint.")

        # 3. Income Ceiling check
        max_inc = _safe_float(scholarship.get("max_income"), 10000000.0)
        student_inc = _safe_float(student.get("income"))
        if max_inc is not None and max_inc > 0:
            if student_inc is None:
                failed.append("Annual family income is missing in student profile.")
            elif student_inc > max_inc:
                failed.append(f"Family income (₹{student_inc:,.0f}) exceeds maximum ceiling (₹{max_inc:,.0f}).")
            else:
                passed.append(f"Income requirement satisfied (₹{student_inc:,.0f} <= ₹{max_inc:,.0f}).")
        else:
            passed.append("No family income ceiling restriction.")

        # 4. State / Domicile check
        req_state = (scholarship.get("state") or "ALL").strip()
        student_state = (student.get("state") or "").strip()
        if req_state.upper() != "ALL":
            if not student_state or student_state.lower() != req_state.lower():
                failed.append(f"State domicile requirement not met (Required: {req_state}, Student: {student_state or 'None'}).")
            else:
                passed.append(f"State domicile matched ({student_state}).")
        else:
            passed.append("Applicable across All India.")

        # 5. Course / Degree check
        req_course = (scholarship.get("course") or "ALL").strip()
        student_course = (student.get("course") or "").strip()
        if req_course.upper() != "ALL":
            if not student_course or student_course.lower() != req_course.lower():
                failed.append(f"Course requirement not met (Required: {req_course}, Student: {student_course or 'None'}).")
            else:
                passed.append(f"Course requirement matched ({student_course}).")
        else:
            passed.append("Open to all courses and academic disciplines.")

        # 6. Year of Study check
        req_year = _safe_int(scholarship.get("year"))
        student_year = _safe_int(student.get("year"))
        if req_year is not None:
            if student_year is None or student_year != req_year:
                failed.append(f"Study year requirement not met (Required Year: {req_year}, Student Year: {student_year if student_year is not None else 'Unspecified'}).")
            else:
                passed.append(f"Year of study matched (Year {student_year}).")
        else:
            passed.append("Open to any year of study.")

        # 7. Category / Social reservation check
        req_cat = (scholarship.get("category") or "ALL").strip()
        student_cat = (student.get("category") or "General").strip()
        if req_cat.upper() != "ALL":
            if student_cat.lower() != req_cat.lower():
                failed.append(f"Social category criteria not met (Required: {req_cat}, Student: {student_cat}).")
            else:
                passed.append(f"Category requirement matched ({student_cat}).")
        else:
            passed.append("Open to all categories (General / Reserved).")

        # 8. Gender criteria check
        req_gender = (scholarship.get("gender") or "ALL").strip()
        student_gender = (student.get("gender") or "ALL").strip()
        if req_gender.upper() != "ALL":
            if student_gender.upper() != "ALL" and student_gender.lower() != req_gender.lower():
                failed.append(f"Gender requirement not met (Required: {req_gender}, Student: {student_gender}).")
            elif student_gender.upper() == "ALL" or not student_gender:
                verification.append(f"Verify gender criteria: scholarship is designated for {req_gender}.")
            else:
                passed.append(f"Gender criteria satisfied ({student_gender}).")
        else:
            passed.append("No gender restrictions.")

        # 9. Age Boundary check
        age_min = _safe_int(scholarship.get("age_min"))
        age_max = _safe_int(scholarship.get("age_max"))
        student_age = _safe_int(student.get("age"))
        if age_min is not None:
            if student_age is not None:
                if student_age < age_min:
                    failed.append(f"Age {student_age} is below minimum required age {age_min}.")
            else:
                verification.append(f"Verify age is >= {age_min} years.")

        if age_max is not None:
            if student_age is not None:
                if student_age > age_max:
                    failed.append(f"Age {student_age} exceeds maximum allowed age {age_max}.")
            else:
                verification.append(f"Verify age is <= {age_max} years.")

        # 10. Verification Items & Disclaimers
        if scholarship.get("deadline"):
            verification.append(f"Check current deadline on official source ({scholarship['deadline']}).")
        if scholarship.get("other_requirements"):
            verification.append(f"Specific provider terms: {scholarship['other_requirements']}")
        if scholarship.get("official_url"):
            verification.append("Verify latest criteria on provider's official portal.")

        is_eligible = (len(failed) == 0)
        return is_eligible, {
            "passed_criteria": passed,
            "failed_criteria": failed,
            "verification_items": verification
        }

    @classmethod
    def filter_eligible(cls, student: Dict[str, Any], scholarships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter a list of scholarships down to only eligible opportunities with eligibility metadata."""
        eligible_results = []
        for sch in scholarships:
            is_eligible, details = cls.evaluate(student, sch)
            if is_eligible:
                item = dict(sch)
                item["eligibility_details"] = details
                eligible_results.append(item)
        return eligible_results
