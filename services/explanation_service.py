from typing import Dict, Any, List

def _safe_float(val, default=None):
    if val is None or val == "":
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

class ExplanationService:
    """Generates human-readable, transparent explanations for scholarship recommendations."""

    DISCLAIMER = (
        "This recommendation is an informational match based on your profile details. "
        "It does not guarantee official scholarship approval or funding. "
        "Please verify all requirements, deadlines, and guidelines on the provider's official portal."
    )

    @classmethod
    def generate(
        cls,
        student: Dict[str, Any],
        scholarship: Dict[str, Any],
        score: float,
        score_breakdown: Dict[str, float],
        eligibility_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesize detailed reasons why a scholarship was recommended and highlight verification items.
        """
        reasons = []

        # Course match reason
        sch_course = scholarship.get("course", "ALL")
        stud_course = student.get("course", "")
        if sch_course != "ALL" and stud_course.lower() == sch_course.lower():
            reasons.append(f"Direct course match for {stud_course}")
        elif sch_course == "ALL":
            reasons.append("Open to all degree programs including yours")

        # Academic performance reason
        min_pct = _safe_float(scholarship.get("min_percentage"), 0.0)
        stud_pct = _safe_float(student.get("percentage"), 0.0)
        if stud_pct is not None and stud_pct > 0:
            if min_pct and min_pct > 0:
                surplus = stud_pct - min_pct
                if surplus >= 15.0:
                    reasons.append(f"Strong academic merit ({stud_pct}% significantly exceeds the {min_pct}% minimum)")
                else:
                    reasons.append(f"Satisfies minimum academic criterion ({stud_pct}% >= {min_pct}%)")
            else:
                reasons.append(f"Strong academic score ({stud_pct}%)")

        # Income reason
        max_inc = _safe_float(scholarship.get("max_income"))
        stud_inc = _safe_float(student.get("income"))
        if max_inc is not None and stud_inc is not None:
            if stud_inc <= max_inc:
                reasons.append(f"Meets household income criteria (₹{stud_inc:,.0f} is within the ₹{max_inc:,.0f} limit)")

        # State match reason
        sch_state = scholarship.get("state", "ALL")
        stud_state = student.get("state", "")
        if sch_state != "ALL" and stud_state.lower() == sch_state.lower():
            reasons.append(f"Domicile preference matched for {stud_state} residents")
        elif sch_state == "ALL":
            reasons.append("Nationwide scholarship open to all states")

        # Category reason
        sch_cat = scholarship.get("category", "ALL")
        stud_cat = student.get("category", "General")
        if sch_cat != "ALL" and stud_cat.lower() == sch_cat.lower():
            reasons.append(f"Special reservation quota matched for {stud_cat} category")

        # Gender reason
        sch_gender = scholarship.get("gender", "ALL")
        stud_gender = student.get("gender", "")
        if sch_gender != "ALL" and stud_gender.lower() == sch_gender.lower():
            reasons.append(f"Designated initiative for {stud_gender} applicants")

        # Collect verification items from eligibility service
        verification_items = list(eligibility_details.get("verification_items", []))
        if scholarship.get("deadline"):
            verification_items.append(f"Verify application deadline: {scholarship['deadline']}")

        # Deduplicate verification items
        seen = set()
        dedup_verification = []
        for item in verification_items:
            if item not in seen:
                seen.add(item)
                dedup_verification.append(item)

        return {
            "match_score": round(score, 3),
            "match_percentage": min(100, max(0, round(score * 100))),
            "reasons": reasons,
            "score_breakdown": score_breakdown,
            "verification_items": dedup_verification,
            "official_url": scholarship.get("official_url"),
            "disclaimer": cls.DISCLAIMER
        }
