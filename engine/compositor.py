"""
Compositor module for PRISM Engine.
Orchestrates the full PRISM pipeline: vectorization → conflict analysis →
fit scoring → financial solving → market blending → SWOT → roadmap.
"""
import sys
import os
import copy
from typing import List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.vectorizer import build_student_vector, build_parent_vector, DOMAINS_ALL
from engine.fit_scorer import career_fit_score, rank_careers_by_fit
from engine.financial_solver import solve_financial_constraint
from engine.conflict_engine import compute_conflict_index, find_compromise_careers
from engine.market_blender import blend_scores

_RIASEC_LABELS = ["Realistic", "Investigative", "Artistic", "Social", "Enterprising", "Conventional"]
_APTITUDE_LABELS = ["Logical-Mathematical", "Verbal-Linguistic", "Spatial", "Interpersonal"]

_DOMAIN_THREATS = {
    "engineering":    "Rapid AI automation of entry-level coding and engineering roles.",
    "emerging_tech":  "High skill obsolescence — tech stacks change every 2-3 years.",
    "medicine":       "Long study duration (5–9 years) and extremely high seat competition.",
    "design":         "Highly competitive creative market with uncertain early-career income.",
    "arts":           "Income instability in early years; portfolio-dependent career growth.",
    "commerce":       "Volatile market conditions and increasing fintech disruption.",
    "law":            "Saturated entry-level job market; long path to seniority.",
    "social_science": "Limited high-paying roles; dependent on government/NGO funding.",
    "pure_science":   "Research funding constraints and limited private-sector pathways.",
    "management":     "High competition for top MBA programmes and leadership roles.",
    "education":      "Lower salary ceilings and dependence on institutional budgets.",
    "agriculture":    "Climate volatility and policy uncertainty affecting sector growth.",
}
_DEFAULT_THREAT = "Rapidly evolving industry landscape requires continuous upskilling."


def build_swot(student_vec: dict, top_careers: List[dict]) -> dict:
    """Build a SWOT analysis from student vector and top career results."""
    riasec = list(student_vec.get("riasec", []))
    aptitude = list(student_vec.get("aptitude", []))

    strengths: List[str] = []
    weaknesses: List[str] = []

    # RIASEC strengths/weaknesses
    for i, val in enumerate(riasec):
        if i >= len(_RIASEC_LABELS):
            break
        v = float(val)
        if v > 0.6:
            strengths.append(f"{_RIASEC_LABELS[i]} orientation — strong psychometric signal")
        elif v < 0.3:
            weaknesses.append(f"Low {_RIASEC_LABELS[i]} score — this domain may be less natural")

    # Aptitude strengths/weaknesses
    for i, val in enumerate(aptitude):
        if i >= len(_APTITUDE_LABELS):
            break
        v = float(val)
        if v > 0.6:
            strengths.append(f"High {_APTITUDE_LABELS[i]} aptitude")
        elif v < 0.3:
            weaknesses.append(f"Developing {_APTITUDE_LABELS[i]} aptitude — needs upskilling")

    # Fallbacks so cards are never empty
    if not strengths:
        strengths.append("Balanced, adaptable psychometric profile")
    if not weaknesses:
        weaknesses.append("No critical psychometric blind-spots detected — well-rounded profile")

    # Opportunities from top 3 careers
    opportunities: List[str] = []
    for blend_result in top_careers[:3]:
        career_id = str(blend_result.get("career_id", ""))
        label = (
            blend_result.get("fit_detail", {}).get("career_label")
            or career_id.replace("_", " ").title()
        )
        score = blend_result.get("composite_score", 0.0)
        opportunities.append(f"{label} (composite score: {score:.2f})")

    # Threats from top career domains
    threats: List[str] = []
    seen_threats: set = set()
    for blend_result in top_careers[:5]:
        domain_raw = (
            blend_result.get("fit_detail", {}).get("domain", "")
            or blend_result.get("financial_detail", {}).get("domain", "")
            or ""
        )
        # Normalize: handle lists or strings
        if isinstance(domain_raw, list):
            domains = [d.lower().strip() for d in domain_raw]
        else:
            domains = [domain_raw.lower().strip()]

        for domain in domains:
            for key, threat in _DOMAIN_THREATS.items():
                if key in domain and threat not in seen_threats:
                    threats.append(threat)
                    seen_threats.add(threat)
                    break

    if not threats:
        threats.append(_DEFAULT_THREAT)

    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "opportunities": opportunities,
        "threats": threats,
    }


def build_roadmap(career_id, careers, exams, scholarships) -> dict:
    """Build an exam/scholarship roadmap for a specific career."""
    career = next(
        (c for c in careers if str(c.get("career_id", "")) == str(career_id)),
        None,
    )
    if career is None:
        return {
            "career": career_id,
            "career_id": str(career_id),
            "steps": [],
            "scholarships": [],
            "geo_hotspots": [],
            "alt_pathways": [],
            "interdisciplinary": [],
        }

    career_name = career.get("name", career_id.replace("_", " ").title())

    career_exam_ids = {str(eid) for eid in career.get("exam_ids", [])}
    relevant_exams = [e for e in exams if str(e.get("exam_id", "")) in career_exam_ids]

    raw_domains = career.get("domains", None)
    if raw_domains is None:
        single = career.get("domain", "")
        career_domains = {single.strip().lower()} if single else set()
    else:
        career_domains = {d.strip().lower() for d in raw_domains}

    def _scholarship_score(sch: dict) -> int:
        elig = {d.strip().lower() for d in sch.get("eligibility_domains", [])}
        if "all" in elig:
            return 1
        if elig & career_domains:
            return 2  # Domain-specific → ranked higher
        return 0

    sorted_scholarships = sorted(scholarships, key=_scholarship_score, reverse=True)
    top_scholarships = sorted_scholarships[:5]  # Increased to 5

    return {
        "career": career_name,
        "career_id": str(career_id),
        "steps": relevant_exams,
        "scholarships": top_scholarships,
        "geo_hotspots": career.get("geo_hotspots", []),
        "alt_pathways": career.get("alt_pathways", []),
        "interdisciplinary": career.get("interdisciplinary", []),
    }


def run_prism(
    student_form: dict,
    parent_form: dict,
    careers: List[dict],
    demand_index: dict,
    scholarships: List[dict],
    exams: List[dict],
    institution_type: str = "private",
) -> dict:
    """Execute the complete PRISM Engine pipeline end-to-end."""
    _PIPELINE_WEIGHTS = {"fit": 0.45, "affordability": 0.35, "demand": 0.20}

    # Stage 1: Vectorize
    student_vec = build_student_vector(student_form)
    parent_vec = build_parent_vector(parent_form)

    # Stage 2: Conflict
    conflict = compute_conflict_index(student_vec, parent_vec)

    # Stage 3 & 4: Fit + Financial + Blend + Sort
    blend_results: List[dict] = []
    for career in careers:
        fit = career_fit_score(student_vec, career)
        financial = solve_financial_constraint(
            parent_vec, career, scholarships, institution_type=institution_type
        )
        blended = blend_scores(fit, financial, demand_index, weights=_PIPELINE_WEIGHTS)

        # Attach domain to both sub-dicts for SWOT domain lookup
        raw_domains = career.get("domains", career.get("domain", ""))
        blended["financial_detail"]["domain"] = raw_domains
        blended["fit_detail"]["domain"] = raw_domains
        blended["fit_detail"]["career_label"] = career.get("name", "")
        blended["fit_detail"]["geo_hotspots"] = career.get("geo_hotspots", [])
        blended["fit_detail"]["skills"] = career.get("skills", [])
        blend_results.append(blended)

    blend_results.sort(key=lambda r: r["composite_score"], reverse=True)
    student_results = blend_results

    # Stage 5: Parent proxy rankings
    parent_sv_proxy = copy.deepcopy(student_vec)
    parent_sv_proxy["domain_prefs"] = parent_vec["domain_prefs"].copy()
    parent_sv_proxy["risk_appetite"] = parent_vec["risk_appetite"]
    parent_fit_results = rank_careers_by_fit(parent_sv_proxy, careers)

    # Stage 6: Compromise careers
    compromise_career_ids = find_compromise_careers(
        student_results=student_results,
        parent_results=parent_fit_results,
        top_n=5,
    )

    # Stage 7: SWOT
    swot = build_swot(student_vec, top_careers=student_results[:5])

    # Stage 8: Roadmap for top career
    top_career_id = student_results[0]["career_id"] if student_results else ""
    roadmap = build_roadmap(top_career_id, careers, exams, scholarships)

    # Stage 9: Assemble output
    return {
        "student_name": student_vec.get("name", ""),
        "top_careers": student_results[:10],
        "compromise_careers": compromise_career_ids,
        "conflict": conflict,
        "swot": swot,
        "roadmap": roadmap,
        "metadata": {
            "institution_type_analyzed": institution_type,
            "total_careers_evaluated": len(careers),
            "weights_used": _PIPELINE_WEIGHTS,
        },
    }
