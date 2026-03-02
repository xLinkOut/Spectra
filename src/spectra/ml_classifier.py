"""Optional lightweight ML classifier for local mode (TF-IDF + Logistic Regression)."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("spectra.ml")


def train_classifier(training_data: list[tuple[str, str]]) -> Any | None:
    """Train a TF-IDF + LogisticRegression classifier from labeled transaction data.

    Parameters
    ----------
    training_data:
        List of (description, category) tuples from the user's history.

    Returns
    -------
    A fitted sklearn Pipeline, or None if not enough data or scikit-learn not installed.
    """
    if len(training_data) < 20:
        logger.info("Not enough training data (%d samples, need ≥20) — skipping ML", len(training_data))
        return None

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import Pipeline
    except ImportError:
        logger.info("scikit-learn not installed — ML classifier disabled. Install with: pip install scikit-learn")
        return None

    descriptions, categories = zip(*training_data)

    # Need at least 2 distinct categories
    unique_cats = set(categories)
    if len(unique_cats) < 2:
        logger.info("Only 1 category in training data — ML classifier not useful")
        return None

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            sublinear_tf=True,
            strip_accents="unicode",
            lowercase=True,
        )),
        ("clf", LogisticRegression(
            max_iter=1000,
            C=1.0,
            class_weight="balanced",
        )),
    ])

    pipeline.fit(list(descriptions), list(categories))
    logger.info("ML classifier trained on %d samples, %d categories", len(descriptions), len(unique_cats))
    return pipeline


def predict(classifier: Any, description: str) -> tuple[str, float]:
    """Predict category for a description.

    Returns
    -------
    (category, confidence) — confidence is the max class probability.
    """
    proba = classifier.predict_proba([description])[0]
    max_idx = proba.argmax()
    confidence = proba[max_idx]
    category = classifier.classes_[max_idx]
    return category, float(confidence)
