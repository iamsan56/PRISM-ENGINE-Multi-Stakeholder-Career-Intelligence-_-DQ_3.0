"""
Fit Scorer module for PRISM Engine.
Computes career fit scores using cosine similarity across RIASEC,
aptitude, domain preference, and risk dimensions.
"""
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List
from engine.vectorizer import DOMAINS_ALL

_WEIGHTS = {
    "riasec": 0.40,
    "aptitude": 0.30,
    "domain": 0.20,
    "risk": 0.10,
}

_GROWTH_OUTLOOK_MAP = {
    "high": 1.0,
    "medium": 0.5,
    "low": 0.0,
}

def career_fit_score(student_vec: dict, career: dict) -> dict:
    # ---- RIASEC cosine similarity ----
    s_riasec = student_vec["riasec"].reshape(1, -1)
    c_riasec_raw = list(career.get("riasec", [0.0] * 6))
    c_riasec = np.array((c_riasec_raw + [0.0] * 6)[:6], dtype=float).reshape(1, -1)
    riasec_sim = float(cosine_similarity(s_riasec, c_riasec)[0, 0])
    riasec_sim = max(0.0, min(1.0, riasec_sim))

    # ---- Aptitude cosine similarity ----
    s_apt = student_vec["aptitude"].reshape(1, -1)
    c_apt_raw = list(career.get("aptitude", [0.0] * 4))
    c_apt = np.array((c_apt_raw + [0.0] * 4)[:4], dtype=float).reshape(1, -1)
    aptitude_sim = float(cosine_similarity(s_apt, c_apt)[0, 0])
    aptitude_sim = max(0.0, min(1.0, aptitude_sim))

    # ---- Domain similarity ----
    career_domain = career.get("domain", "").strip().lower()
    domain_indicator = np.array(
        [1.0 if d == career_domain else 0.0 for d in DOMAINS_ALL],
        dtype=float
    )
    s_domain = student_vec["domain_prefs"]
    s_domain_norm = np.linalg.norm(s_domain) + 1e-9
    domain_sim = float(np.dot(s_domain, domain_indicator) / s_domain_norm)
    domain_sim = max(0.0, min(1.0, domain_sim))

    # ---- Risk similarity ----
    outlook_str = career.get("growth_outlook", "medium").strip().lower()
    career_risk = _GROWTH_OUTLOOK_MAP.get(outlook_str, 0.5)
    student_risk = float(student_vec.get("risk_appetite", 0.5))
    risk_sim = max(0.0, 1.0 - abs(student_risk - career_risk))

    # ---- Weighted composite ----
    fit = (
        _WEIGHTS["riasec"] * riasec_sim
        + _WEIGHTS["aptitude"] * aptitude_sim
        + _WEIGHTS["domain"] * domain_sim
        + _WEIGHTS["risk"] * risk_sim
    )

    return {
        "career_id": str(career.get("career_id", "")),
        "fit_score": round(float(fit), 4),
        "breakdown": {
            "riasec": round(riasec_sim, 4),
            "aptitude": round(aptitude_sim, 4),
            "domain": round(domain_sim, 4),
            "risk": round(risk_sim, 4),
        },
    }

def rank_careers_by_fit(student_vec: dict, careers: List[dict]) -> List[dict]:
    if not careers: return []
    results = [career_fit_score(student_vec, career) for career in careers]
    results.sort(key=lambda r: r["fit_score"], reverse=True)
    return results
