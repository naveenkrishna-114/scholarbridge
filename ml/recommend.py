from typing import Dict, Any, List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from ml.preprocessing import DataPreprocessor

class MLSimilarityEngine:
    """Content-based TF-IDF and Cosine Similarity recommendation model."""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            max_features=500,
            sublinear_tf=True
        )
        self.is_fitted = False
        self.scholarship_matrix = None
        self.scholarship_ids = []

    def fit(self, scholarships: List[Dict[str, Any]]):
        """Fit vectorizer on scholarship descriptions and requirements."""
        if not scholarships:
            return self

        corpus = [DataPreprocessor.create_scholarship_document(s) for s in scholarships]
        self.scholarship_ids = [s["id"] for s in scholarships]
        
        # Guard against completely empty corpus
        if all(not text.strip() for text in corpus):
            corpus = ["general scholarship education student" for _ in corpus]

        self.scholarship_matrix = self.vectorizer.fit_transform(corpus)
        self.is_fitted = True
        return self

    def compute_similarity(
        self,
        student: Dict[str, Any],
        scholarships: List[Dict[str, Any]]
    ) -> Dict[int, float]:
        """
        Compute cosine similarity between student representation and a candidate list of scholarships.
        Returns a dict mapping scholarship_id -> similarity score in [0.0, 1.0].
        """
        if not scholarships:
            return {}

        # If not fitted or candidate set differs, fit on candidates
        corpus = [DataPreprocessor.create_scholarship_document(s) for s in scholarships]
        try:
            matrix = self.vectorizer.fit_transform(corpus)
            student_doc = DataPreprocessor.create_student_document(student)
            
            if not student_doc.strip():
                return {s["id"]: 0.5 for s in scholarships}

            student_vector = self.vectorizer.transform([student_doc])
            similarities = cosine_similarity(student_vector, matrix).flatten()

            results = {}
            for i, sch in enumerate(scholarships):
                sim = float(similarities[i]) if i < len(similarities) else 0.0
                # Normalize cosine similarity to [0.0, 1.0] range
                norm_sim = min(1.0, max(0.0, (sim + 1.0) / 2.0 if sim < 0 else sim))
                results[sch["id"]] = round(norm_sim, 3)

            return results
        except Exception:
            # Fallback to uniform neutral score
            return {s["id"]: 0.5 for s in scholarships}
