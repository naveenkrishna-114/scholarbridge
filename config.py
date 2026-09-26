import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    DATABASE_PATH = os.environ.get(
        "DATABASE_PATH", str(BASE_DIR / "database" / "scholarships.db")
    )
    TESTING = False
    DEBUG = False

    # Configurable Recommendation Weights (from Master Spec)
    RECOMMENDATION_WEIGHTS = {
        "course": float(os.environ.get("WEIGHT_COURSE", 0.25)),
        "academic_performance": float(os.environ.get("WEIGHT_ACADEMIC", 0.25)),
        "income": float(os.environ.get("WEIGHT_INCOME", 0.20)),
        "category": float(os.environ.get("WEIGHT_CATEGORY", 0.10)),
        "state": float(os.environ.get("WEIGHT_STATE", 0.10)),
        "year": float(os.environ.get("WEIGHT_YEAR", 0.05)),
        "other": float(os.environ.get("WEIGHT_OTHER", 0.05)),
    }

    # Security & Session Settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True

class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    DATABASE_PATH = ":memory:"

class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = "https"

config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
