# engine/vectorizer.py
"""
Vectorizer module for PRISM Engine.
Converts raw student and parent form data into normalized numerical vectors
for downstream algorithmic processing.
"""
import numpy as np
from typing import Union

RIASEC_KEYS = ["realistic", "investigative", "artistic", "social", "enterprising", "conventional"]
APTITUDE_KEYS = ["logical", "verbal", "spatial", "interpersonal"]
DOMAINS_ALL = [
    "engineering", "medicine", "design", "commerce", "law",
    "social_science", "pure_science", "arts", "management", "education",
    "agriculture", "emerging_tech"
]
LOCATION_MAP = {"own_city": 0.0, "own_state": 0.33, "any_india": 0.66, "abroad": 1.0}
WORK_STYLE_ALL = ["research", "practice", "business", "creative"]


def normalize_minmax(vector: Union[list, np.ndarray], min_val: float = 1.0, max_val: float = 5.0) -> np.ndarray:
    """
    Scale a Likert-scale vector (default 1–5) to the [0, 1] range via min-max normalization.

    Parameters
    ----------
    vector : list or np.ndarray
        Input values to normalize.
    min_val : float
        Minimum possible value of the scale (default 1.0).
    max_val : float
        Maximum possible value of the scale (default 5.0).

    Returns
    -------
    np.ndarray
        Normalized array in [0, 1]. Returns a zero vector if min_val == max_val
        to avoid division by zero.
    """
    arr = np.array(vector, dtype=float)
    denom = max_val - min_val
    if denom == 0.0:
        return np.zeros_like(arr)
    return np.clip((arr - min_val) / denom, 0.0, 1.0)


def build_student_vector(form: dict) -> dict:
    """
    Convert a raw student form submission into a normalized numerical vector dictionary.

    Parameters
    ----------
    form : dict
        Raw student form data. Expected keys:
        - name (str): student's name.
        - riasec (list[float]): 6 scores on 1–5 scale (Realistic, Investigative,
          Artistic, Social, Enterprising, Conventional).
        - aptitude (list[float]): 4 scores on 1–5 scale (Logical, Verbal, Spatial,
          Interpersonal).
        - domain_prefs (dict): mapping domain name → 1–5 score. Missing domains default to 1.0.
        - risk_appetite (float): 1–5 scalar.
        - location (str): one of "own_city", "own_state", "any_india", "abroad".
        - work_style (list[str]): subset of WORK_STYLE_ALL indicating preferred styles.

    Returns
    -------
    dict
        Normalized vector dict with keys:
        - name (str)
        - riasec (np.ndarray, shape (6,), values in [0, 1])
        - aptitude (np.ndarray, shape (4,), values in [0, 1])
        - domain_prefs (np.ndarray, shape (12,), values in [0, 1])
        - risk_appetite (float, [0, 1])
        - location_openness (float, [0, 1])
        - work_style_vec (np.ndarray, shape (4,), binary 0 or 1)
    """
    # --- RIASEC (6 dims) ---
    riasec_raw = list(form.get("riasec", [1.0] * 6))
    # Pad or truncate to exactly 6 elements
    riasec_raw = (riasec_raw + [1.0] * 6)[:6]
    riasec_vec = normalize_minmax(riasec_raw)

    # --- Aptitude (4 dims) ---
    aptitude_raw = list(form.get("aptitude", [1.0] * 4))
    aptitude_raw = (aptitude_raw + [1.0] * 4)[:4]
    aptitude_vec = normalize_minmax(aptitude_raw)

    # --- Domain preferences (12 dims, canonical order) ---
    domain_dict = form.get("domain_prefs", {})
    domain_raw = [float(domain_dict.get(d, 1.0)) for d in DOMAINS_ALL]
    domain_vec = normalize_minmax(domain_raw)

    # --- Risk appetite (scalar) ---
    risk_raw = float(form.get("risk_appetite", 1.0))
    risk_norm = float(normalize_minmax([risk_raw])[0])

    # --- Location openness ---
    location_key = form.get("location", "own_city")
    location_val = LOCATION_MAP.get(location_key, 0.0)

    # --- Work style (binary multi-hot, 4 dims) ---
    selected_styles = set(form.get("work_style", []))
    work_style_vec = np.array(
        [1.0 if ws in selected_styles else 0.0 for ws in WORK_STYLE_ALL],
        dtype=float
    )

    return {
        "name": form.get("name", ""),
        "riasec": riasec_vec,
        "aptitude": aptitude_vec,
        "domain_prefs": domain_vec,
        "risk_appetite": risk_norm,
        "location_openness": location_val,
        "work_style_vec": work_style_vec,
    }


def build_parent_vector(form: dict) -> dict:
    """
    Convert a raw parent form submission into a normalized numerical vector dictionary.

    Parameters
    ----------
    form : dict
        Raw parent form data. Expected keys:
        - domain_prefs (dict): mapping domain name → 1–5 score. Missing domains default to 1.0.
        - risk_appetite (float): 1–5 scalar.
        - location (str): one of "own_city", "own_state", "any_india", "abroad".
        - budget_max_no_loan (float): max budget in INR without taking a loan.
        - loan_tolerance (float): maximum tolerable loan amount in INR.
        - priority_weights (dict): keys prestige/salary/stability/passion, summing to ~1.0.

    Returns
    -------
    dict
        Normalized vector dict with keys:
        - domain_prefs (np.ndarray, shape (12,), values in [0, 1])
        - risk_appetite (float, [0, 1])
        - location_openness (float, [0, 1])
        - budget_max_no_loan (float)
        - loan_tolerance (float)
        - priority_weights (dict)
    """
    # --- Domain preferences ---
    domain_dict = form.get("domain_prefs", {})
    domain_raw = [float(domain_dict.get(d, 1.0)) for d in DOMAINS_ALL]
    domain_vec = normalize_minmax(domain_raw)

    # --- Risk appetite ---
    risk_raw = float(form.get("risk_appetite", 1.0))
    risk_norm = float(normalize_minmax([risk_raw])[0])

    # --- Location openness ---
    location_key = form.get("location", "own_city")
    location_val = LOCATION_MAP.get(location_key, 0.0)

    # --- Financial constraints (kept as raw INR) ---
    budget_max_no_loan = float(form.get("budget_max_no_loan", 0.0))
    loan_tolerance = float(form.get("loan_tolerance", 0.0))

    # --- Priority weights (pass through, validated) ---
    default_weights = {"prestige": 0.25, "salary": 0.25, "stability": 0.25, "passion": 0.25}
    priority_weights = form.get("priority_weights", default_weights)
    # Ensure all four keys exist; fill missing with 0.0
    for k in default_weights:
        priority_weights.setdefault(k, 0.0)

    return {
        "domain_prefs": domain_vec,
        "risk_appetite": risk_norm,
        "location_openness": location_val,
        "budget_max_no_loan": budget_max_no_loan,
        "loan_tolerance": loan_tolerance,
        "priority_weights": priority_weights,
    }
