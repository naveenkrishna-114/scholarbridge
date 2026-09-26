from typing import Dict, Any, List, Optional, Tuple
from config import Config
from services.eligibility_service import EligibilityService
from services.explanation_service import ExplanationService
from models.scholarship import Scholarship, RecommendationRecord
from ml.recommend import MLSimilarityEngine

def _safe_float(val, default=0.0):
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

class RecommendationService:
    """Hybrid recommendation engine combining rule-based pruning and weighted multi-attribute ranking."""

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or Config.RECOMMENDATION_WEIGHTS

    def calculate_score(
        self,
        student: Dict[str, Any],
        scholarship: Dict[str, Any]
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate a multi-attribute match score in [0.0, 1.0] along with sub-score breakdown.
        """
        breakdown = {}

        # 1. Course Match Score (25%)
        sch_course = (scholarship.get("course") or "ALL").strip()
        stud_course = (student.get("course") or "").strip()
        if sch_course.upper() != "ALL" and stud_course.lower() == sch_course.lower():
            breakdown["course"] = 1.0
        elif sch_course.upper() == "ALL":
            breakdown["course"] = 0.8
        else:
            breakdown["course"] = 0.4

        # 2. Academic Merit Score (25%)
        pct = _safe_float(student.get("percentage"), 0.0)
        min_pct = _safe_float(scholarship.get("min_percentage"), 0.0)
        # Base scale on student percentage
        base_merit = min(1.0, max(0.0, pct / 100.0))
        # Bonus for exceeding minimum threshold
        if min_pct > 0 and pct >= min_pct:
            surplus_ratio = min(0.2, (pct - min_pct) / 100.0)
            breakdown["academic_performance"] = min(1.0, base_merit + surplus_ratio)
        else:
            breakdown["academic_performance"] = base_merit

        # 3. Financial Need Score (20%)
        # Lower family income indicates higher need
        stud_income = _safe_float(student.get("income"), 0.0)
        max_income = _safe_float(scholarship.get("max_income"), 1000000.0)
        if max_income > 0:
            need_ratio = 1.0 - min(1.0, stud_income / max_income)
            breakdown["income"] = round(0.5 + (0.5 * need_ratio), 3)
        else:
            breakdown["income"] = 0.7

        # 4. Social Category Score (10%)
        sch_cat = (scholarship.get("category") or "ALL").strip()
        stud_cat = (student.get("category") or "General").strip()
        if sch_cat.upper() != "ALL" and stud_cat.lower() == sch_cat.lower():
            breakdown["category"] = 1.0
        elif sch_cat.upper() == "ALL":
            breakdown["category"] = 0.8
        else:
            breakdown["category"] = 0.5

        # 5. State Domicile Score (10%)
        sch_state = (scholarship.get("state") or "ALL").strip()
        stud_state = (student.get("state") or "").strip()
        if sch_state.upper() != "ALL" and stud_state.lower() == sch_state.lower():
            breakdown["state"] = 1.0
        elif sch_state.upper() == "ALL":
            breakdown["state"] = 0.8
        else:
            breakdown["state"] = 0.5

        # 6. Study Year Score (5%)
        sch_year = _safe_int(scholarship.get("year"))
        stud_year = _safe_int(student.get("year"))
        if sch_year is not None and stud_year is not None and sch_year == stud_year:
            breakdown["year"] = 1.0
        elif sch_year is None:
            breakdown["year"] = 0.85
        else:
            breakdown["year"] = 0.5

        # 7. Other Attributes (Gender / Achievements) (5%)
        sch_gender = (scholarship.get("gender") or "ALL").strip()
        stud_gender = (student.get("gender") or "").strip()
        other_score = 0.8
        if sch_gender.upper() != "ALL" and stud_gender.lower() == sch_gender.lower():
            other_score = 1.0
        if student.get("achievements"):
            other_score = min(1.0, other_score + 0.1)
        breakdown["other"] = other_score

        # Weighted total sum
        total_score = 0.0
        for criterion, weight in self.weights.items():
            total_score += breakdown.get(criterion, 0.5) * weight

        total_score = min(1.0, max(0.0, total_score))
        return total_score, breakdown

    def get_recommendations(
        self,
        student: Dict[str, Any],
        user_id: Optional[int] = None,
        save_history: bool = True,
        db_path: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate ranked scholarship recommendations for a student:
        1. Fetch all ACTIVE scholarships.
        2. Filter out clearly ineligible scholarships.
        3. Rank remaining candidates using multi-attribute score.
        4. Synthesize explanations and optionally record history.
        """
        all_scholarships = Scholarship.list_all(status="ACTIVE", db_path=db_path)
        # First filter clearly ineligible opportunities
        eligible_candidates = EligibilityService.filter_eligible(student, all_scholarships)
        if not eligible_candidates:
            return []

        # Compute ML TF-IDF Cosine Similarity across eligible candidates
        ml_engine = MLSimilarityEngine()
        ml_similarities = ml_engine.compute_similarity(student, eligible_candidates)

        ranked_recommendations = []
        for sch in eligible_candidates:
            eligibility_details = sch.get("eligibility_details", {})
            rule_score, breakdown = self.calculate_score(student, sch)
            ml_sim = ml_similarities.get(sch["id"], 0.5)

            # Hybrid score: 75% multi-attribute criteria + 25% ML semantic similarity
            hybrid_score = min(1.0, max(0.0, (0.75 * rule_score) + (0.25 * ml_sim)))
            breakdown["ml_similarity"] = round(ml_sim, 3)

            explanation = ExplanationService.generate(
                student=student,
                scholarship=sch,
                score=hybrid_score,
                score_breakdown=breakdown,
                eligibility_details=eligibility_details
            )

            rec_item = dict(sch)
            rec_item["match_score"] = round(hybrid_score, 3)
            rec_item["rule_score"] = round(rule_score, 3)
            rec_item["ml_score"] = round(ml_sim, 3)
            rec_item["match_percentage"] = explanation["match_percentage"]
            rec_item["explanation"] = explanation

            ranked_recommendations.append(rec_item)

        # Sort descending by hybrid match score, secondary sort by award amount
        ranked_recommendations.sort(
            key=lambda x: (x["match_score"], x.get("amount") or 0.0),
            reverse=True
        )

        # Optionally persist recommendation history for audit & analytics
        if save_history and user_id:
            for rec in ranked_recommendations[:10]:
                try:
                    RecommendationRecord.save(
                        user_id=user_id,
                        scholarship_id=rec["id"],
                        score=rec["match_score"],
                        explanation=rec["explanation"],
                        db_path=db_path
                    )
                except Exception:
                    pass

        return ranked_recommendations
