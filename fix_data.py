import json

# 1. Fix careers.json
with open(r"D:\Projects\Data_Quest_3.0\data\careers.json", "r") as f:
    data = json.load(f)

new_careers = []
for c in data["careers"]:
    # The engine expects `base_fee_inr` and `expected_entry_salary_inr`. We'll just use the private fee.
    fee = c.get("typical_fees_inr", {}).get("private", 1500000) if isinstance(c.get("typical_fees_inr"), dict) else c.get("base_fee_inr", 1500000)
    sal = c.get("salary_inr", {}).get("entry", 400000) if isinstance(c.get("salary_inr"), dict) else c.get("expected_entry_salary_inr", 400000)
    
    new_c = {
        "career_id": c.get("id", c.get("career_id")),
        "name": c.get("label", c.get("name")),
        "riasec": c.get("riasec_vector", c.get("riasec")),
        "aptitude": c.get("aptitude_vector", c.get("aptitude")),
        "domain": c.get("domains", [""])[0] if isinstance(c.get("domains"), list) else c.get("domain", ""),
        "base_fee_inr": fee,
        "expected_entry_salary_inr": sal,
        "growth_outlook": c.get("growth_outlook", "medium"),
        "exam_ids": c.get("exams", c.get("exam_ids", [])),
    }
    new_careers.append(new_c)

with open(r"D:\Projects\Data_Quest_3.0\data\careers.json", "w") as f:
    json.dump({"careers": new_careers}, f, indent=2)


# 2. Fix scholarships.json
with open(r"D:\Projects\Data_Quest_3.0\data\scholarships.json", "r") as f:
    scholars = json.load(f)

new_scholars = []
for s in scholars:
    new_s = s.copy()
    new_s["amount_inr"] = s.get("benefit_inr", s.get("amount_inr", 0))
    new_s["eligibility_domains"] = s.get("eligibility", {}).get("domains", s.get("eligibility_domains", []))
    new_scholars.append(new_s)

with open(r"D:\Projects\Data_Quest_3.0\data\scholarships.json", "w") as f:
    json.dump(new_scholars, f, indent=2)


# 3. Fix exams.json
with open(r"D:\Projects\Data_Quest_3.0\data\exams.json", "r") as f:
    exams = json.load(f)

new_exams = []
for e in exams:
    new_e = e.copy()
    new_e["exam_id"] = e.get("id", e.get("exam_id"))
    new_exams.append(new_e)

with open(r"D:\Projects\Data_Quest_3.0\data\exams.json", "w") as f:
    json.dump(new_exams, f, indent=2)

print("Data structures completely fixed and aligned!")
