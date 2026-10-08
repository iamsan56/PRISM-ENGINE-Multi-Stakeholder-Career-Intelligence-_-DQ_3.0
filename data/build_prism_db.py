import json
import os
import sqlite3


DATA_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(DATA_DIR, "prism.db")


def read_json(name):
    with open(os.path.join(DATA_DIR, name), "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    payloads = {
        "careers": read_json("careers.json")["careers"],
        "demand": read_json("demand_index.json")["index"],
        "scholarships": read_json("scholarships.json"),
        "exams": read_json("exams.json"),
    }

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS prism_data (name TEXT PRIMARY KEY, payload TEXT NOT NULL)"
        )
        for name, payload in payloads.items():
            conn.execute(
                "INSERT OR REPLACE INTO prism_data (name, payload) VALUES (?, ?)",
                (name, json.dumps(payload, ensure_ascii=False)),
            )
        conn.commit()

    print(f"Built {DB_PATH}")


if __name__ == "__main__":
    main()
