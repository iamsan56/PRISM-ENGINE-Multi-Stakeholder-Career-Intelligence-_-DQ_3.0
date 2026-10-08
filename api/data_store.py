import json
import os
import sqlite3


ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "prism.db")


def _load_json_data() -> dict:
    with open(os.path.join(DATA_DIR, "careers.json"), "r", encoding="utf-8") as file:
        careers = json.load(file)["careers"]
    with open(os.path.join(DATA_DIR, "demand_index.json"), "r", encoding="utf-8") as file:
        demand = json.load(file)["index"]
    with open(os.path.join(DATA_DIR, "scholarships.json"), "r", encoding="utf-8") as file:
        scholarships = json.load(file)
    with open(os.path.join(DATA_DIR, "exams.json"), "r", encoding="utf-8") as file:
        exams = json.load(file)
    return {
        "careers": careers,
        "demand": demand,
        "scholarships": scholarships,
        "exams": exams,
        "source": "json",
    }


def load_prism_data(db_path: str = DB_PATH) -> dict:
    if not os.path.exists(db_path):
        return _load_json_data()

    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT name, payload FROM prism_data").fetchall()
        loaded = {row["name"]: json.loads(row["payload"]) for row in rows}
        return {
            "careers": loaded["careers"],
            "demand": loaded["demand"],
            "scholarships": loaded["scholarships"],
            "exams": loaded["exams"],
            "source": "sqlite",
        }
    except Exception:
        return _load_json_data()
