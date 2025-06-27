from typing import Dict, List


def trap_score(features: Dict) -> float:
    """
    Stub for your ML trap-probability model.
    Replace with model.load(...) & model.predict_proba(...)
    """
    # e.g. return model.predict_proba([features])[0,1]
    return 0.5  # placeholder


def sentiment_score(texts: List[str]) -> float:
    """
    Stub for live-news or social-media sentiment.
    Integrate VADER, FinBERT or GPT here.
    """
    return 0.0
