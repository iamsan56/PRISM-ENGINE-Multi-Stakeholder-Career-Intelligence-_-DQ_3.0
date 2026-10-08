# engine/conflict_engine.py
"""
Conflict Engine module for PRISM Engine.
Measures the degree of misalignment between student preferences and parent
expectations across domain, risk, and location dimensions.
"""
import math
import numpy as np
from typing import List

# Dimension weights (must sum to 1.0)
_WEIGHTS = {
    "domain": 0.50,
    "risk": 0.30,
    "location": 0.20,
}

# Number of domain dimensions (from vectorizer.DOMAINS_ALL)
_N_DOMAINS = 12

# Severity thresholds
_LOW_THRESHOLD = 0.2
_HIGH_THRESHOLD = 0.5


def compute_conflict_index(student_vec: dict, parent_vec: dict) -> dict:
    """
    Compute a scalar conflict index representing the degree of misalignment
    between student and parent preference vectors.

    Dimensions:
    - domain   : L2 norm of (student_domain_prefs − parent_domain_prefs)
                 normalised by √12 so the raw score is in [0, 1].
    - risk     : |student_risk_appetite − parent_risk_appetite|
    - location : |student_location_openness − parent_location_openness|

    Weighted composite: domain×0.50 + risk×0.30 + location×0.20

    Parameters
    ----------
    student_vec : dict
        Normalized student vector from ``build_student_vector``.
    parent_vec : dict
        Normalized parent vector from ``build_parent_vector``.

    Returns
    -------
    dict
        {
            "conflict_index": float,         # [0, 1], rounded to 4 dp
            "severity": str,                 # "LOW" | "MODERATE" | "HIGH"
            "per_dimension": {
                "domain": float,
                "risk": float,
                "location": float,
            },
            "weights_used": dict,
            "resolution_hint": str,
            "detailed_narrative": str,
        }
    """
    # ── Domain conflict ───────────────────────────────────────────────────
    s_domain = np.array(student_vec.get("domain_prefs", np.zeros(_N_DOMAINS)), dtype=float)
    p_domain = np.array(parent_vec.get("domain_prefs", np.zeros(_N_DOMAINS)), dtype=float)
    # Max possible L2 norm between two unit-normalised 12-D vectors = √12
    domain_diff = float(np.linalg.norm(s_domain - p_domain) / np.sqrt(_N_DOMAINS))
    domain_diff = min(1.0, domain_diff)   # clamp

    # ── Risk conflict ─────────────────────────────────────────────────────
    s_risk = float(student_vec.get("risk_appetite", 0.5))
    p_risk = float(parent_vec.get("risk_appetite", 0.5))
    risk_diff = abs(s_risk - p_risk)

    # ── Location conflict ─────────────────────────────────────────────────
    s_loc = float(student_vec.get("location_openness", 0.0))
    p_loc = float(parent_vec.get("location_openness", 0.0))
    loc_diff = abs(s_loc - p_loc)

    # ── Weighted composite ────────────────────────────────────────────────
    conflict_index = (
        _WEIGHTS["domain"] * domain_diff
        + _WEIGHTS["risk"] * risk_diff
        + _WEIGHTS["location"] * loc_diff
    )
    conflict_index = round(float(conflict_index), 4)

    # ── Severity classification ───────────────────────────────────────────
    if conflict_index < _LOW_THRESHOLD:
        severity = "LOW"
    elif conflict_index < _HIGH_THRESHOLD:
        severity = "MODERATE"
    else:
        severity = "HIGH"

    # ── Resolution hint ───────────────────────────────────────────────────
    dominant_dim = max(
        {"domain": domain_diff, "risk": risk_diff, "location": loc_diff},
        key=lambda k: {"domain": domain_diff, "risk": risk_diff, "location": loc_diff}[k]
    )
    _hints = {
        "domain": (
            "Focus joint counselling sessions on overlapping career domains that "
            "satisfy both student interests and parent expectations."
        ),
        "risk": (
            "Bridge the risk gap by presenting careers with stable entry-level "
            "salaries and clear growth trajectories to reassure the parent."
        ),
        "location": (
            "Discuss hybrid options — starting locally and progressing to broader "
            "geographies — to align student ambition with parent comfort."
        ),
    }
    resolution_hint = _hints[dominant_dim]

    # ── Detailed narrative (dynamic) ──────────────────────────────────────
    narrative_parts = []

    # Domain sentence
    if domain_diff >= _HIGH_THRESHOLD:
        # Identify which domains student ranks highest vs parent
        from engine.vectorizer import DOMAINS_ALL
        s_top_idx = int(np.argmax(s_domain))
        p_top_idx = int(np.argmax(p_domain))
        s_top_domain = DOMAINS_ALL[s_top_idx].replace("_", " ")
        p_top_domain = DOMAINS_ALL[p_top_idx].replace("_", " ")
        narrative_parts.append(
            f"The student and parent have significant differences in domain preferences "
            f"(student strongly prefers {s_top_domain} while parent leans towards {p_top_domain})."
        )
    elif domain_diff >= _LOW_THRESHOLD:
        narrative_parts.append(
            "There is a moderate difference in domain preferences between student and parent, "
            "with some career areas receiving divergent scores."
        )
    else:
        narrative_parts.append(
            "Domain preferences between student and parent are broadly well-aligned."
        )

    # Risk sentence
    if risk_diff >= 0.4:
        s_risk_label = "high-risk, high-reward" if s_risk > p_risk else "stable and low-risk"
        p_risk_label = "stable and low-risk" if s_risk > p_risk else "high-risk, high-reward"
        narrative_parts.append(
            f"Their risk tolerances differ considerably: the student favours {s_risk_label} "
            f"paths while the parent prefers {p_risk_label} careers."
        )
    elif risk_diff >= 0.15:
        narrative_parts.append(
            "There is a noticeable gap in risk appetite that may require mediation."
        )
    else:
        narrative_parts.append(
            "Risk tolerance is reasonably well-matched between student and parent."
        )

    # Location sentence
    if loc_diff >= 0.4:
        narrative_parts.append(
            "Location flexibility is a significant point of contention and should be "
            "explicitly addressed in counselling."
        )
    elif loc_diff >= 0.15:
        narrative_parts.append(
            "There is some difference in location openness that could affect institution choices."
        )
    else:
        narrative_parts.append("Location flexibility is well-aligned between the two.")

    detailed_narrative = " ".join(narrative_parts)

    return {
        "conflict_index": conflict_index,
        "severity": severity,
        "per_dimension": {
            "domain": round(domain_diff, 4),
            "risk": round(risk_diff, 4),
            "location": round(loc_diff, 4),
        },
        "weights_used": dict(_WEIGHTS),
        "resolution_hint": resolution_hint,
        "detailed_narrative": detailed_narrative,
    }


def find_compromise_careers(
    student_results: List[dict],
    parent_results: List[dict],
    top_n: int = 5,
) -> List[str]:
    """
    Find career IDs that appear in the top half of BOTH student and parent
    fit-score rankings, representing mutually acceptable choices.

    Parameters
    ----------
    student_results : list[dict]
        Fit-score results list for student (from ``rank_careers_by_fit`` or
        blend results). Each dict must contain a "career_id" key.
    parent_results : list[dict]
        Fit-score results list for parent proxy.
    top_n : int
        Maximum number of compromise careers to return (default 5).

    Returns
    -------
    list[str]
        List of career_id strings appearing in the top half of both rankings.
        Empty list if no overlap or if either list is empty.
    """
    if not student_results or not parent_results:
        return []

    # Top half = first ceil(n/2) entries of each ranked list
    s_top_half = {
        str(r.get("career_id", ""))
        for r in student_results[: max(1, math.ceil(len(student_results) / 2))]
    }
    p_top_half = {
        str(r.get("career_id", ""))
        for r in parent_results[: max(1, math.ceil(len(parent_results) / 2))]
    }

    overlap = s_top_half & p_top_half
    # Preserve student ranking order for deterministic output
    ordered_overlap = [
        str(r.get("career_id", ""))
        for r in student_results
        if str(r.get("career_id", "")) in overlap
    ]

    return ordered_overlap[:top_n]

