# engine/market_blender.py
"""
Market Blender module for PRISM Engine.
Combines career fit scores, financial feasibility, and live market demand
into a single composite ranking score.
"""
from typing import List, Optional

# Default blending weights
_DEFAULT_WEIGHTS = {
    "fit": 0.45,
    "affordability": 0.35,
    "demand": 0.20,
}


def _affordability_score(financial_result: dict) -> float:
    """
    Convert a financial solver result into a scalar affordability score in [0, 1].

    Rules:
    - Not affordable (status EXCEEDS_CONSTRAINT): 0.0
    - Fully affordable (loan_required == 0):      1.0
    - With loan:  1.0 - (loan_required / net_fee) * 0.5

    Parameters
    ----------
    financial_result : dict
        Output of ``solve_financial_constraint``.

    Returns
    -------
    float
        Affordability score in [0, 1].
    """
    if not financial_result.get("affordable", False):
        return 0.0

    loan_required = float(financial_result.get("loan_required", 0.0))
    net_fee = float(financial_result.get("net_fee", 0.0))

    if loan_required <= 0:
        return 1.0

    if net_fee <= 0:
        # net_fee is zero but loan is somehow required — edge case
        return 0.5

    score = 1.0 - (loan_required / net_fee) * 0.5
    return max(0.0, min(1.0, score))


def blend_scores(
    fit: dict,
    financial: dict,
    demand_index: dict,
    weights: Optional[dict] = None,
) -> dict:
    """
    Blend fit, affordability, and market demand into a single composite score.

    Parameters
    ----------
    fit : dict
        Career fit result from ``career_fit_score``.
        Must contain "career_id" and "fit_score".
    financial : dict
        Financial constraint result from ``solve_financial_constraint``.
        Must contain "affordable", "loan_required", "net_fee".
    demand_index : dict
        Nested dict mapping career_id → {"national": float, ...}.
        Demand score falls back to 0.5 if career not found.
    weights : dict or None
        Optional override of default blending weights.
        Expected keys: "fit", "affordability", "demand" (should sum to 1.0).

    Returns
    -------
    dict
        {
            "career_id": str,
            "composite_score": float,   # rounded to 4 dp
            "fit_score": float,
            "affordability_score": float,
            "demand_score": float,
            "affordable": bool,
            "financial_detail": dict,
            "fit_detail": dict,
        }
    """
    if weights is None:
        weights = _DEFAULT_WEIGHTS

    career_id = str(fit.get("career_id", financial.get("career_id", "")))

    fit_score = float(fit.get("fit_score", 0.0))
    afford_score = _affordability_score(financial)

    demand_score = float(
        demand_index.get(career_id, {}).get("national", 0.5)
    )
    demand_score = max(0.0, min(1.0, demand_score))

    # Normalise weights to guard against weights not summing to 1
    w_fit = float(weights.get("fit", _DEFAULT_WEIGHTS["fit"]))
    w_aff = float(weights.get("affordability", _DEFAULT_WEIGHTS["affordability"]))
    w_dem = float(weights.get("demand", _DEFAULT_WEIGHTS["demand"]))
    w_total = w_fit + w_aff + w_dem
    if w_total == 0.0:
        w_fit, w_aff, w_dem, w_total = (
            _DEFAULT_WEIGHTS["fit"],
            _DEFAULT_WEIGHTS["affordability"],
            _DEFAULT_WEIGHTS["demand"],
            1.0,
        )
    w_fit /= w_total
    w_aff /= w_total
    w_dem /= w_total

    composite = w_fit * fit_score + w_aff * afford_score + w_dem * demand_score

    return {
        "career_id": career_id,
        "composite_score": round(float(composite), 4),
        "fit_score": round(fit_score, 4),
        "affordability_score": round(afford_score, 4),
        "demand_score": round(demand_score, 4),
        "affordable": bool(financial.get("affordable", False)),
        "financial_detail": financial,
        "fit_detail": fit,
    }


def apply_custom_weights(results: List[dict], weights: dict) -> List[dict]:
    """
    Re-rank a list of blended career results using a new set of weights.

    Recomputes the composite score for each result using the provided weights
    and returns the list sorted in descending order of the new composite score.

    Parameters
    ----------
    results : list[dict]
        List of blend dicts from ``blend_scores``.
    weights : dict
        New weights dict with keys "fit", "affordability", "demand".

    Returns
    -------
    list[dict]
        Re-ranked list with updated "composite_score" values.
        Returns an empty list if results is empty.
    """
    if not results:
        return []

    w_fit = float(weights.get("fit", _DEFAULT_WEIGHTS["fit"]))
    w_aff = float(weights.get("affordability", _DEFAULT_WEIGHTS["affordability"]))
    w_dem = float(weights.get("demand", _DEFAULT_WEIGHTS["demand"]))
    w_total = w_fit + w_aff + w_dem
    if w_total == 0.0:
        return list(results)  # no-op if weights are all zero
    w_fit /= w_total
    w_aff /= w_total
    w_dem /= w_total

    re_ranked = []
    for r in results:
        new_composite = (
            w_fit * r.get("fit_score", 0.0)
            + w_aff * r.get("affordability_score", 0.0)
            + w_dem * r.get("demand_score", 0.0)
        )
        updated = dict(r)
        updated["composite_score"] = round(float(new_composite), 4)
        re_ranked.append(updated)

    re_ranked.sort(key=lambda x: x["composite_score"], reverse=True)
    return re_ranked
