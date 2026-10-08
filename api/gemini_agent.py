import sys
import os
import json
import google.generativeai as genai

from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _money(value):
    try:
        return f"INR {float(value):,.0f}"
    except (TypeError, ValueError):
        return "not available"


def _number(value, suffix=""):
    try:
        return f"{float(value):.2f}{suffix}"
    except (TypeError, ValueError):
        return "not available"


def _fallback_counsel(engine_output, user_message, language="English"):
    """Pure-math fallback when Gemini is unavailable."""
    careers = engine_output.get("top_careers", [])[:3]
    roadmap = engine_output.get("roadmap", {}) or {}
    conflict = engine_output.get("conflict", {}) or {}

    career_lines = []
    for index, career in enumerate(careers, start=1):
        financial = career.get("financial_detail", {}) or {}
        label = (
            career.get("fit_detail", {}).get("career_label")
            or career.get("career_id", "Career").replace("_", " ").title()
        )
        fit = _number((career.get("fit_score") or 0) * 100, "%")
        roi = _number(financial.get("roi"), "x")
        emi = _money(financial.get("monthly_emi"))
        status = str(financial.get("status", "review needed")).replace("_", " ")
        career_lines.append(f"{index}. {label}: fit {fit}, ROI {roi}, EMI {emi}, affordability {status}.")

    scholarships = roadmap.get("scholarships") or []
    scholarship_text = (
        ", ".join(s.get("name", "Scholarship") for s in scholarships[:3])
        if scholarships
        else "No exact scholarship match yet."
    )
    conflict_level = conflict.get("severity", "Unknown")
    conflict_text = conflict.get("detailed_narrative") or "Use the top-ranked affordable option as compromise."

    return {
        "response": (
            f"PRISM is answering from verified engine math (Gemini offline).\n\n"
            f"### Top Career Recommendations\n"
            + "\n".join(career_lines or ["No careers returned."])
            + f"\n\n### Financial Reality Check\nScholarships/Aid: {scholarship_text}\n\n"
            f"### Family Alignment Report\nConflict level: {conflict_level}. {conflict_text}\n\n"
            f"### Local Roadmap\nAsk: \"nearest colleges\" or open the Hyper-Local Institutions map."
        ),
        "history": [],
    }


def get_prism_counsel(
    engine_output,
    student_profile,
    parent_profile,
    user_message,
    language="English",
    history=None,
):
    if history is None:
        history = []

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if "GEMINI_API_KEY=" in api_key:
        api_key = api_key.split("GEMINI_API_KEY=")[-1].strip()
    if not api_key:
        return _fallback_counsel(engine_output, user_message, language)

    genai.configure(api_key=api_key)

    system_prompt = f"""You are PRISM Counselor, an expert AI career guidance counselor for Indian students and families.
Translate the PRISM Engine's numerical output into warm, clear, actionable guidance.

CRITICAL INSTRUCTION: Respond STRICTLY in {language}.
Structure every response as:

### 🎯 Top Career Recommendations
[List top 3 careers with fit %, ROI, and a one-line reason why]

### 💰 Financial Reality Check
[Is it affordable? EMI amount? Which scholarships apply?]

### ❤️ Family Alignment Report
[Conflict level, compromise career suggestion]

### 📍 Local Roadmap
[Demand hotspots, key exams, next steps]
"""

    try:
        model_names = [
            os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
            "gemini-1.5-flash",
        ]

        context = f"""
## Engine Output
{json.dumps(engine_output, indent=2, default=str)}

## Student Profile
{json.dumps(student_profile, indent=2, default=str)}

## Parent Profile
{json.dumps(parent_profile, indent=2, default=str)}
"""

        last_error = None
        for model_name in dict.fromkeys(model_names):
            try:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=system_prompt,
                )
                chat = model.start_chat(history=history)
                response = chat.send_message(context + "\n\nUser Question: " + user_message)
                break
            except Exception as exc:
                last_error = exc
                chat = None
                response = None
        if response is None:
            raise last_error

        return {
            "response": response.text,
            "history": [
                {"role": m.role, "parts": [p.text for p in m.parts]}
                for m in chat.history
            ],
        }

    except Exception as exc:
        error_type = type(exc).__name__
        fallback = _fallback_counsel(engine_output, user_message, language)

        # Surface API key errors clearly
        if "unauthenticated" in str(exc).lower() or "invalid" in str(exc).lower():
            fallback["response"] = (
                "🚨 GEMINI API KEY ERROR\n"
                "Your key in .env is dead or invalid.\n\n"
                "Fix:\n1. Go to https://aistudio.google.com\n"
                "2. Create a new API key\n"
                "3. Update GEMINI_API_KEY in Data_Quest_3.0/.env\n"
                "4. Restart: python -m uvicorn api.main:app --port 8000\n\n"
                "--- Fallback Engine Math Below ---\n\n"
            ) + fallback["response"]
        else:
            fallback["gemini_error"] = f"{error_type}: {str(exc)[:200]}"

        return fallback
