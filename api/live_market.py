import json
import os
from datetime import datetime
from urllib.parse import quote_plus


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def _fallback_market(career_id: str) -> dict:
    demand_path = os.path.join(DATA_DIR, "demand_index.json")
    with open(demand_path, "r", encoding="utf-8") as file:
        demand = json.load(file)["index"]

    career_demand = demand.get(career_id, {})
    hotspots = [
        {"location": key, "score": value}
        for key, value in career_demand.items()
        if key != "national"
    ]
    hotspots.sort(key=lambda item: item["score"], reverse=True)

    return {
        "career_id": career_id,
        "source": "cached_demand_index",
        "live": False,
        "national_demand": career_demand.get("national", 0.5),
        "hotspots": hotspots[:5],
        "signals": [],
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }


def scrape_live_market(career_id: str, career_label: str | None = None) -> dict:
    """
    Lightweight BeautifulSoup scraper for demo/live-market proof.
    Falls back to PRISM's cached demand index if the network or page shape fails.
    """
    try:
        import requests
        from bs4 import BeautifulSoup

        query = quote_plus(career_label or career_id.replace("_", " "))
        url = f"https://www.ncs.gov.in/job-seeker/Pages/Search.aspx?search={query}"
        response = requests.get(url, timeout=8, headers={"User-Agent": "PRISM-Hackathon/1.0"})
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        text = " ".join(soup.get_text(" ").split())
        snippets = [text[i:i + 160] for i in range(0, min(len(text), 480), 160) if text[i:i + 160]]
        fallback = _fallback_market(career_id)

        return {
            **fallback,
            "source": "ncs.gov.in",
            "live": True,
            "query_url": url,
            "signals": snippets[:3],
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as exc:
        fallback = _fallback_market(career_id)
        fallback["error"] = f"live scrape fallback: {type(exc).__name__}"
        return fallback
