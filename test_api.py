import requests
import json

payload = {
  "student_form": {
    "name": "Student",
    "riasec": [1, 1, 1, 1, 1, 1],
    "aptitude": [1, 1, 1, 1],
    "domain_prefs": {"engineering": 1, "medicine": 1, "design": 1, "commerce": 1, "pure_science": 1, "steam": 1, "emerging_tech": 1},
    "location": "own_city",
    "risk_appetite": 3,
    "work_style": ["research"]
  },
  "parent_form": {
    "domain_prefs": {"engineering": 1, "medicine": 1, "design": 1, "commerce": 1, "pure_science": 1, "steam": 1, "emerging_tech": 1},
    "location": "own_city",
    "risk_appetite": 3,
    "budget_max_no_loan": 500000,
    "loan_tolerance": 200000,
    "priority_weights": {"prestige": 0.3, "salary": 0.4, "stability": 0.2, "passion": 0.1}
  },
  "institution_type": "private"
}

try:
    print("Testing /analyze endpoint...")
    res = requests.post("http://localhost:8000/analyze", json=payload)
    print("Status:", res.status_code)
    print("Response keys:", res.json().keys() if res.status_code == 200 else res.text)
    
    if res.status_code == 200:
        engine_out = res.json()
        print("Top career name:", engine_out.get("top_careers", [{}])[0].get("career_id"))
        
        print("\nTesting /chat endpoint...")
        chat_payload = {
            "engine_output": engine_out,
            "student_profile": {"name": "Student"},
            "parent_profile": {},
            "user_message": "hello",
            "history": []
        }
        chat_res = requests.post("http://localhost:8000/chat", json=chat_payload)
        print("Chat Status:", chat_res.status_code)
        if chat_res.status_code != 200:
            print("Chat Error:", chat_res.text)
except Exception as e:
    print("Error connecting:", e)
