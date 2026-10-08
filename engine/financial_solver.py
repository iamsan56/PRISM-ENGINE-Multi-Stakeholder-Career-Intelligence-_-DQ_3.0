# engine/financial_solver.py
"""
Financial Solver module for PRISM Engine.
Computes EMI, ROI, payback period, and affordability status for career–institution
combinations given parent financial constraints and available scholarships.
"""
import math
from typing import List, Dict, Any

# ── Module-level financial constants ─────────────────────────────────────────
LOAN_INTEREST_RATE = 0.085        # 8.5% p.a. reducing-balance
LOAN_TENURE_YEARS = 7             # default loan repayment tenure
DISCOUNT_RATE = 0.06              # 6% discount rate for NPV
SALARY_GROWTH_RATE = 0.07         # 7% assumed annual salary growth
LIVING_EXPENSE_INR = 250_000      # ₹2.5 L assumed annual living expense

# Fee multipliers relative to a career's base_fee_inr
_FEE_MULTIPLIER = {
    "govt": 0.30,     # ~30% of private
    "private": 1.00,  # reference
    "abroad": 3.00,   # ~3× private
}


# ── Core financial computations ───────────────────────────────────────────────

def monthly_emi(principal: float, annual_rate: float, years: int) -> float:
    """
    Compute the monthly EMI for a reducing-balance (amortising) loan.

    Formula: EMI = P * r * (1+r)^n / ((1+r)^n - 1)
    where r = monthly interest rate, n = total months.

    Parameters
    ----------
    principal : float
        Loan principal in INR.
    annual_rate : float
        Annual interest rate as a decimal (e.g. 0.085 for 8.5%).
    years : int
        Loan tenure in years.

    Returns
    -------
    float
        Monthly EMI in INR. Returns 0.0 if principal <= 0.
    """
    if principal <= 0:
        return 0.0

    monthly_rate = annual_rate / 12.0
    n = int(years) * 12

    if monthly_rate == 0.0:
        return principal / n if n > 0 else 0.0

    factor = (1 + monthly_rate) ** n
    emi = principal * monthly_rate * factor / (factor - 1)
    return float(emi)


def compute_roi(
    total_course_cost: float,
    expected_entry_salary: float,
    years_to_break_even: int = 10,
) -> float:
    """
    Compute the Return-on-Investment ratio as discounted salary sum over N years
    divided by total course cost.

    Salary is assumed to grow at SALARY_GROWTH_RATE per annum, and future salaries
    are discounted at DISCOUNT_RATE.

    Parameters
    ----------
    total_course_cost : float
        Total cost of education in INR (post-aid/scholarship).
    expected_entry_salary : float
        Expected annual salary at career entry (INR p.a.).
    years_to_break_even : int
        Number of years over which to evaluate ROI (default 10).

    Returns
    -------
    float
        ROI ratio. Returns math.inf if total_course_cost == 0 (free education).
    """
    if total_course_cost == 0:
        return math.inf

    discounted_salary_sum = 0.0
    for yr in range(1, years_to_break_even + 1):
        salary_yr = expected_entry_salary * ((1 + SALARY_GROWTH_RATE) ** (yr - 1))
        discounted_salary_sum += salary_yr / ((1 + DISCOUNT_RATE) ** yr)

    return discounted_salary_sum / total_course_cost


def payback_years(
    total_course_cost: float,
    expected_entry_salary: float,
    living_expense_inr: float = LIVING_EXPENSE_INR,
) -> float:
    """
    Estimate the number of years until cumulative net annual income covers the
    total course cost.

    Net annual income = expected_entry_salary - living_expense_inr.
    Salary grows at SALARY_GROWTH_RATE each year.

    Parameters
    ----------
    total_course_cost : float
        Total educational cost in INR.
    expected_entry_salary : float
        Starting annual salary in INR.
    living_expense_inr : float
        Annual living expense to subtract from salary (default LIVING_EXPENSE_INR).

    Returns
    -------
    float
        Number of years to break even. Returns math.inf if net annual income <= 0
        or cost cannot ever be covered.
    """
    net_annual_initial = expected_entry_salary - living_expense_inr
    if net_annual_initial <= 0:
        return math.inf

    cumulative = 0.0
    for yr in range(1, 51):  # cap at 50 years
        net_yr = net_annual_initial * ((1 + SALARY_GROWTH_RATE) ** (yr - 1))
        cumulative += net_yr
        if cumulative >= total_course_cost:
            return float(yr)

    return math.inf


# ── Main constraint solver ────────────────────────────────────────────────────

def solve_financial_constraint(
    parent_vec: dict,
    career: dict,
    scholarships: List[dict],
    institution_type: str = "private",
) -> dict:
    """
    Determine affordability and compute financial metrics for a specific
    career–institution combination given the parent's financial profile.

    Parameters
    ----------
    parent_vec : dict
        Normalized parent vector from ``build_parent_vector``.
    career : dict
        Career profile. Expected keys: career_id, base_fee_inr,
        expected_entry_salary_inr, domains (list[str]) or domain (str).
    scholarships : list[dict]
        Available scholarship dicts. Each scholarship should have keys:
        amount_inr (float), eligibility_domains (list[str]).
    institution_type : str
        One of "govt", "private", "abroad". Fee multiplied by _FEE_MULTIPLIER.

    Returns
    -------
    dict
        Full financial analysis result dict.
    """
    # ── Resolve career domain(s) ───────────────────────────────────────────
    raw_domains = career.get("domains", None)
    if raw_domains is None:
        single = career.get("domain", "")
        career_domains = [single.strip().lower()] if single else []
    else:
        career_domains = [d.strip().lower() for d in raw_domains]

    career_id = str(career.get("career_id", ""))
    base_fee = float(career.get("base_fee_inr", 0.0))
    entry_salary = float(career.get("expected_entry_salary_inr", 0.0))

    # ── Compute gross fee for chosen institution type ─────────────────────
    multiplier = _FEE_MULTIPLIER.get(institution_type, 1.0)
    gross_fee = base_fee * multiplier

    # ── Filter applicable scholarships ───────────────────────────────────
    applicable_scholarships = []
    for sch in scholarships:
        elig = [d.strip().lower() for d in sch.get("eligibility_domains", [])]
        if "all" in elig or any(cd in elig for cd in career_domains):
            applicable_scholarships.append(sch)

    # ── Sum scholarship aid (cap each at gross_fee) ───────────────────────
    total_aid = 0.0
    for sch in applicable_scholarships:
        aid = min(float(sch.get("amount_inr", 0.0)), gross_fee)
        total_aid += aid

    total_aid = min(total_aid, gross_fee)   # total aid cannot exceed course cost
    net_fee = max(0.0, gross_fee - total_aid)

    # ── Loan required = net_fee minus what parents can pay without loan ───
    budget_no_loan = float(parent_vec.get("budget_max_no_loan", 0.0))
    loan_required = max(0.0, net_fee - budget_no_loan)
    loan_tolerance = float(parent_vec.get("loan_tolerance", 0.0))

    # ── EMI, ROI, Payback ─────────────────────────────────────────────────
    emi = monthly_emi(loan_required, LOAN_INTEREST_RATE, LOAN_TENURE_YEARS)
    roi = compute_roi(net_fee if net_fee > 0 else gross_fee, entry_salary)
    pb_years = payback_years(net_fee if net_fee > 0 else gross_fee, entry_salary)

    # ── Affordability status ──────────────────────────────────────────────
    if loan_required <= 0:
        status = "FULLY_AFFORDABLE"
    elif loan_required <= loan_tolerance * 0.5:
        status = "AFFORDABLE_WITH_SMALL_LOAN"
    elif loan_required <= loan_tolerance:
        status = "AFFORDABLE_WITH_SIGNIFICANT_LOAN"
    else:
        status = "EXCEEDS_CONSTRAINT"

    affordable = status != "EXCEEDS_CONSTRAINT"

    return {
        "career_id": career_id,
        "institution_type": institution_type,
        "gross_fee": round(gross_fee, 2),
        "total_aid": round(total_aid, 2),
        "net_fee": round(net_fee, 2),
        "loan_required": round(loan_required, 2),
        "loan_tolerance": round(loan_tolerance, 2),
        "monthly_emi": round(emi, 2),
        "roi": round(roi, 4) if roi != math.inf else "inf",
        "payback_years": round(pb_years, 2) if pb_years != math.inf else "inf",
        "status": status,
        "affordable": affordable,
        "scholarships_applied": len(applicable_scholarships),
    }


def get_best_institution_pathway(
    parent_vec: dict,
    career: dict,
    scholarships: List[dict],
) -> dict:
    """
    Evaluate all three institution types (govt, private, abroad) for a career
    and recommend the optimal pathway based on affordability and cost.

    Strategy: recommend the cheapest type that is still affordable.
    If none is affordable, fall back to "govt" (least expensive option).

    Parameters
    ----------
    parent_vec : dict
        Normalized parent vector from ``build_parent_vector``.
    career : dict
        Career profile dict.
    scholarships : list[dict]
        Available scholarship dicts.

    Returns
    -------
    dict
        {
            "recommended_type": "govt" | "private" | "abroad",
            "all_results": {
                "govt": {...},
                "private": {...},
                "abroad": {...},
            },
            "is_any_affordable": bool,
        }
    """
    inst_types = ["govt", "private", "abroad"]
    all_results: Dict[str, Any] = {}

    for itype in inst_types:
        all_results[itype] = solve_financial_constraint(
            parent_vec, career, scholarships, institution_type=itype
        )

    # Pick cheapest affordable institution type (govt < private < abroad by fee)
    affordable_types = [t for t in inst_types if all_results[t]["affordable"]]
    is_any_affordable = len(affordable_types) > 0

    if is_any_affordable:
        # Among affordable options, pick the one with lowest loan_required
        recommended_type = min(
            affordable_types,
            key=lambda t: all_results[t]["loan_required"],
        )
    else:
        recommended_type = "govt"   # least bad fallback

    return {
        "recommended_type": recommended_type,
        "all_results": all_results,
        "is_any_affordable": is_any_affordable,
    }
