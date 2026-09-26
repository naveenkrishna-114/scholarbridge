import os
import sys
import pickle
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from models.scholarship import Scholarship
from ml.recommend import MLSimilarityEngine
MODEL_FILE = BASE_DIR / "ml" / "tfidf_model.pkl"

def train_and_persist_model(db_path: Optional[str] = None):
    """
    Train TF-IDF similarity model on current active scholarship records and persist to disk.
    """
    scholarships = Scholarship.list_all(status="ACTIVE", db_path=db_path)
    print(f"Training TF-IDF model on {len(scholarships)} active scholarships...")

    engine = MLSimilarityEngine()
    engine.fit(scholarships)

    os.makedirs(os.path.dirname(MODEL_FILE), exist_ok=True)
    with open(MODEL_FILE, "wb") as f:
        pickle.dump(engine, f)

    print(f"Model successfully saved to {MODEL_FILE}")
    return engine

def load_or_train_model(db_path: Optional[str] = None) -> MLSimilarityEngine:
    """
    Load persisted model from disk, or train a new one if not yet cached.
    """
    if MODEL_FILE.exists():
        try:
            with open(MODEL_FILE, "rb") as f:
                engine = pickle.load(f)
                return engine
        except Exception as e:
            print(f"Failed to load cached model: {e}. Retraining...")

    return train_and_persist_model(db_path=db_path)

if __name__ == "__main__":
    train_and_persist_model()
