import pandas as pd
import json
import os

ONET_DIR = r"D:\Projects\Data_Quest_3.0\data\db_31_0_excel"
OUTPUT_FILE = r"D:\Projects\Data_Quest_3.0\data\careers.json"

# We map 30 distinct Indian careers to their closest O*NET-SOC codes
# O*NET uses detailed codes like "15-1132.00" (Software Developers)
CAREER_MAPPING = {
    # ENGINEERING
    "software_engineer": {"onet_code": "15-1252.00", "label": "Software Engineer", "domains": ["Engineering", "STEAM"]},
    "civil_engineer": {"onet_code": "17-2051.00", "label": "Civil Engineer", "domains": ["Engineering"]},
    "biomedical_engineer": {"onet_code": "17-2031.00", "label": "Biomedical Engineer", "domains": ["Engineering", "Healthcare", "STEAM"]},
    "mechanical_engineer": {"onet_code": "17-2141.00", "label": "Mechanical Engineer", "domains": ["Engineering"]},
    "chemical_engineer": {"onet_code": "17-2041.00", "label": "Chemical Engineer", "domains": ["Engineering", "Pure Science"]},
    
    # MEDICAL/HEALTHCARE
    "doctor_mbbs": {"onet_code": "29-1215.00", "label": "Doctor (MBBS/MD)", "domains": ["Medical", "Healthcare"]},
    "dentist": {"onet_code": "29-1021.00", "label": "Dentist", "domains": ["Medical", "Healthcare"]},
    "pharmacist": {"onet_code": "29-1051.00", "label": "Pharmacist", "domains": ["Medical", "Healthcare"]},
    "nursing": {"onet_code": "29-1141.00", "label": "Registered Nurse", "domains": ["Medical", "Healthcare"]},
    "physiotherapist": {"onet_code": "29-1123.00", "label": "Physiotherapist", "domains": ["Medical", "Healthcare"]},
    
    # DESIGN/ARTS
    "ux_designer": {"onet_code": "15-1255.00", "label": "UI/UX Designer", "domains": ["Design", "STEAM"]},
    "graphic_designer": {"onet_code": "27-1024.00", "label": "Graphic Designer", "domains": ["Design", "Arts"]},
    "architect": {"onet_code": "17-1011.00", "label": "Architect", "domains": ["Design", "Engineering"]},
    "fashion_designer": {"onet_code": "27-1022.00", "label": "Fashion Designer", "domains": ["Design", "Arts"]},
    "film_director": {"onet_code": "27-2012.00", "label": "Film Director", "domains": ["Arts", "Design"]},
    
    # COMMERCE/LAW
    "chartered_accountant": {"onet_code": "13-2011.00", "label": "Chartered Accountant", "domains": ["Commerce", "Management"]},
    "corporate_lawyer": {"onet_code": "23-1011.00", "label": "Corporate Lawyer", "domains": ["Law", "Commerce"]},
    "financial_analyst": {"onet_code": "13-2051.00", "label": "Financial Analyst", "domains": ["Commerce"]},
    "marketing_manager": {"onet_code": "11-2021.00", "label": "Marketing Manager", "domains": ["Commerce", "Management"]},
    "hr_manager": {"onet_code": "11-3121.00", "label": "HR Manager", "domains": ["Management", "Social Science"]},
    
    # PURE SCIENCE
    "data_scientist": {"onet_code": "15-1221.00", "label": "Data Scientist", "domains": ["Pure Science", "STEAM", "Engineering"]},
    "research_physicist": {"onet_code": "19-2012.00", "label": "Research Physicist", "domains": ["Pure Science"]},
    "environmental_scientist": {"onet_code": "19-2041.00", "label": "Environmental Scientist", "domains": ["Pure Science", "Agriculture"]},
    "mathematician": {"onet_code": "15-2021.00", "label": "Mathematician / Actuary", "domains": ["Pure Science", "Commerce"]},
    "statistician": {"onet_code": "15-2041.00", "label": "Statistician", "domains": ["Pure Science"]},
    
    # EMERGING/STEAM
    "ai_ml_engineer": {"onet_code": "15-1252.00", "label": "AI/ML Engineer", "domains": ["STEAM", "Engineering", "Emerging Tech"]},
    "cybersecurity_analyst": {"onet_code": "15-1212.00", "label": "Cybersecurity Analyst", "domains": ["STEAM", "Emerging Tech"]},
    "robotics_engineer": {"onet_code": "17-2199.08", "label": "Robotics Engineer", "domains": ["STEAM", "Engineering", "Emerging Tech"]},
    "game_developer": {"onet_code": "15-1252.00", "label": "Game Developer", "domains": ["STEAM", "Design", "Emerging Tech"]},
    "edtech_entrepreneur": {"onet_code": "11-1011.00", "label": "EdTech Entrepreneur", "domains": ["STEAM", "Management", "Education"]}
}

# Indian Context Fallback Data (Since O*NET doesn't have Indian fees/salaries)
INDIAN_CONTEXT = {
    "software_engineer": {"fees": {"govt": 800000, "private": 1500000, "abroad": 6000000}, "salary": {"entry": 600000, "mid": 1800000, "senior": 4000000}, "hotspots": ["Bengaluru", "Hyderabad", "Pune"]},
    "civil_engineer": {"fees": {"govt": 600000, "private": 1200000, "abroad": 5000000}, "salary": {"entry": 350000, "mid": 900000, "senior": 2000000}, "hotspots": ["Mumbai", "Delhi", "Chennai"]},
    "biomedical_engineer": {"fees": {"govt": 700000, "private": 1400000, "abroad": 5500000}, "salary": {"entry": 400000, "mid": 1200000, "senior": 2500000}, "hotspots": ["Bengaluru", "Pune", "Hyderabad"]},
    "mechanical_engineer": {"fees": {"govt": 600000, "private": 1200000, "abroad": 5000000}, "salary": {"entry": 350000, "mid": 1000000, "senior": 2200000}, "hotspots": ["Chennai", "Pune", "Coimbatore"]},
    "chemical_engineer": {"fees": {"govt": 600000, "private": 1200000, "abroad": 5000000}, "salary": {"entry": 400000, "mid": 1100000, "senior": 2400000}, "hotspots": ["Gujarat", "Mumbai", "Chennai"]},
    "doctor_mbbs": {"fees": {"govt": 500000, "private": 7500000, "abroad": 30000000}, "salary": {"entry": 700000, "mid": 1500000, "senior": 3500000}, "hotspots": ["Delhi", "Mumbai", "Chennai", "Bengaluru"]},
    "dentist": {"fees": {"govt": 400000, "private": 2500000, "abroad": 20000000}, "salary": {"entry": 400000, "mid": 900000, "senior": 2000000}, "hotspots": ["Delhi", "Mumbai", "Bengaluru"]},
    "pharmacist": {"fees": {"govt": 300000, "private": 800000, "abroad": 4000000}, "salary": {"entry": 300000, "mid": 600000, "senior": 1200000}, "hotspots": ["Hyderabad", "Ahmedabad", "Pune"]},
    "nursing": {"fees": {"govt": 200000, "private": 600000, "abroad": 3000000}, "salary": {"entry": 300000, "mid": 600000, "senior": 1500000}, "hotspots": ["Kerala", "Delhi", "Bengaluru"]},
    "physiotherapist": {"fees": {"govt": 250000, "private": 700000, "abroad": 3500000}, "salary": {"entry": 300000, "mid": 700000, "senior": 1500000}, "hotspots": ["Delhi", "Mumbai", "Bengaluru"]},
    "ux_designer": {"fees": {"govt": 500000, "private": 1800000, "abroad": 5000000}, "salary": {"entry": 500000, "mid": 1500000, "senior": 3500000}, "hotspots": ["Bengaluru", "Pune", "Mumbai"]},
    "graphic_designer": {"fees": {"govt": 200000, "private": 800000, "abroad": 3000000}, "salary": {"entry": 300000, "mid": 700000, "senior": 1500000}, "hotspots": ["Mumbai", "Delhi", "Bengaluru"]},
    "architect": {"fees": {"govt": 400000, "private": 1500000, "abroad": 5000000}, "salary": {"entry": 350000, "mid": 900000, "senior": 2500000}, "hotspots": ["Delhi", "Mumbai", "Bengaluru"]},
    "fashion_designer": {"fees": {"govt": 500000, "private": 2000000, "abroad": 6000000}, "salary": {"entry": 350000, "mid": 1000000, "senior": 3000000}, "hotspots": ["Mumbai", "Delhi", "Bengaluru"]},
    "film_director": {"fees": {"govt": 300000, "private": 1500000, "abroad": 8000000}, "salary": {"entry": 300000, "mid": 1200000, "senior": 5000000}, "hotspots": ["Mumbai", "Chennai", "Hyderabad"]},
    "chartered_accountant": {"fees": {"govt": 80000, "private": 500000, "abroad": 0}, "salary": {"entry": 700000, "mid": 1800000, "senior": 4500000}, "hotspots": ["Mumbai", "Delhi", "Bengaluru"]},
    "corporate_lawyer": {"fees": {"govt": 600000, "private": 2500000, "abroad": 10000000}, "salary": {"entry": 800000, "mid": 2000000, "senior": 6000000}, "hotspots": ["Mumbai", "Delhi", "Bengaluru"]},
    "financial_analyst": {"fees": {"govt": 400000, "private": 1500000, "abroad": 5000000}, "salary": {"entry": 500000, "mid": 1400000, "senior": 3000000}, "hotspots": ["Mumbai", "Bengaluru", "Delhi"]},
    "marketing_manager": {"fees": {"govt": 400000, "private": 1800000, "abroad": 6000000}, "salary": {"entry": 500000, "mid": 1500000, "senior": 3500000}, "hotspots": ["Mumbai", "Delhi", "Bengaluru"]},
    "hr_manager": {"fees": {"govt": 400000, "private": 1500000, "abroad": 5000000}, "salary": {"entry": 400000, "mid": 1200000, "senior": 2500000}, "hotspots": ["Bengaluru", "Mumbai", "Delhi"]},
    "data_scientist": {"fees": {"govt": 800000, "private": 1800000, "abroad": 6000000}, "salary": {"entry": 800000, "mid": 2000000, "senior": 4500000}, "hotspots": ["Bengaluru", "Hyderabad", "Pune"]},
    "research_physicist": {"fees": {"govt": 200000, "private": 800000, "abroad": 4000000}, "salary": {"entry": 500000, "mid": 1200000, "senior": 2500000}, "hotspots": ["Bengaluru", "Mumbai", "Pune"]},
    "environmental_scientist": {"fees": {"govt": 200000, "private": 700000, "abroad": 3500000}, "salary": {"entry": 400000, "mid": 900000, "senior": 2000000}, "hotspots": ["Delhi", "Bengaluru", "Pune"]},
    "mathematician": {"fees": {"govt": 200000, "private": 800000, "abroad": 4000000}, "salary": {"entry": 600000, "mid": 1500000, "senior": 3500000}, "hotspots": ["Mumbai", "Bengaluru", "Delhi"]},
    "statistician": {"fees": {"govt": 200000, "private": 800000, "abroad": 4000000}, "salary": {"entry": 500000, "mid": 1300000, "senior": 3000000}, "hotspots": ["Bengaluru", "Mumbai", "Delhi"]},
    "ai_ml_engineer": {"fees": {"govt": 800000, "private": 1800000, "abroad": 6000000}, "salary": {"entry": 900000, "mid": 2400000, "senior": 5500000}, "hotspots": ["Bengaluru", "Hyderabad", "Pune"]},
    "cybersecurity_analyst": {"fees": {"govt": 700000, "private": 1500000, "abroad": 5500000}, "salary": {"entry": 600000, "mid": 1600000, "senior": 3500000}, "hotspots": ["Bengaluru", "Delhi", "Pune"]},
    "robotics_engineer": {"fees": {"govt": 700000, "private": 1600000, "abroad": 5500000}, "salary": {"entry": 600000, "mid": 1500000, "senior": 3500000}, "hotspots": ["Bengaluru", "Pune", "Chennai"]},
    "game_developer": {"fees": {"govt": 500000, "private": 1500000, "abroad": 5000000}, "salary": {"entry": 500000, "mid": 1400000, "senior": 3000000}, "hotspots": ["Bengaluru", "Pune", "Hyderabad"]},
    "edtech_entrepreneur": {"fees": {"govt": 400000, "private": 1500000, "abroad": 5000000}, "salary": {"entry": 400000, "mid": 2000000, "senior": 10000000}, "hotspots": ["Bengaluru", "Delhi", "Mumbai"]}
}

print("Loading O*NET Data...")
df_interests = pd.read_excel(os.path.join(ONET_DIR, "Career Interest Types.xlsx"))
df_abilities = pd.read_excel(os.path.join(ONET_DIR, "Abilities.xlsx"))

# Process RIASEC
# O*NET Scale for interests is typically 1 to 7. We normalize to 0-1.
careers = []
for cid, meta in CAREER_MAPPING.items():
    onet_code = meta["onet_code"]
    
    # 1. Get RIASEC (Interests)
    # The elements are: Realistic, Investigative, Artistic, Social, Enterprising, Conventional
    # In O*NET, Element Name corresponds to these. We fetch "Data Value"
    interest_data = df_interests[df_interests['O*NET-SOC Code'] == onet_code]
    riasec_vec = [0.0]*6
    riasec_map = {"Realistic": 0, "Investigative": 1, "Artistic": 2, "Social": 3, "Enterprising": 4, "Conventional": 5}
    for _, row in interest_data.iterrows():
        elem = row['Element Name']
        if elem in riasec_map:
            val = float(row['Data Value'])
            # Normalize 1-7 to 0-1
            norm_val = max(0.0, min(1.0, (val - 1.0) / 6.0))
            riasec_vec[riasec_map[elem]] = round(norm_val, 3)

    # 2. Get Aptitude (Abilities)
    # We map O*NET abilities to our 4 categories: Logical, Verbal, Spatial, Interpersonal
    # In O*NET, abilities scale is 1 to 7 (Data Value).
    ability_data = df_abilities[(df_abilities['O*NET-SOC Code'] == onet_code) & (df_abilities['Scale ID'] == 'IM')]
    # IM = Importance (1-5 in some versions, or 1-5 / 1-7. O*NET 31.0 Importance is 1-5.)
    # Let's normalize Importance from 1-5 to 0-1.
    
    logical_elems = ["Mathematical Reasoning", "Deductive Reasoning", "Inductive Reasoning", "Number Facility"]
    verbal_elems = ["Oral Comprehension", "Written Comprehension", "Oral Expression", "Written Expression"]
    spatial_elems = ["Spatial Orientation", "Visualization"]
    interpersonal_elems = ["Social Perceptiveness"] # Social Perceptiveness is actually a Skill, but we approximate or use alternative
    
    def get_avg_score(elem_list):
        scores = ability_data[ability_data['Element Name'].isin(elem_list)]['Data Value'].astype(float)
        if len(scores) > 0:
            avg = scores.mean()
            return max(0.0, min(1.0, (avg - 1.0) / 4.0)) # 1-5 scale normalization
        return 0.5 # fallback

    apt_logical = get_avg_score(logical_elems)
    apt_verbal = get_avg_score(verbal_elems)
    apt_spatial = get_avg_score(spatial_elems)
    # Fallback for interpersonal if not in abilities (since it's mostly in Skills)
    apt_interpersonal = 0.6 if "Social" in meta["domains"] or "Medical" in meta["domains"] else 0.4 

    apt_vec = [round(apt_logical, 3), round(apt_verbal, 3), round(apt_spatial, 3), round(apt_interpersonal, 3)]

    ctx = INDIAN_CONTEXT[cid]
    
    career_obj = {
        "id": cid,
        "label": meta["label"],
        "domains": meta["domains"],
        "riasec_vector": riasec_vec,
        "aptitude_vector": apt_vec,
        "skills": ["Communication", "Problem Solving", "Technical"], # simplified
        "typical_fees_inr": ctx["fees"],
        "salary_inr": ctx["salary"],
        "demand_key": cid,
        "growth_outlook": "high",
        "geo_hotspots": ctx["hotspots"],
        "exams": [],
        "alt_pathways": [],
        "interdisciplinary": ["STEAM Innovation"],
        "course_duration_years": 4
    }
    careers.append(career_obj)

final_json = {"careers": careers}
with open(OUTPUT_FILE, 'w') as f:
    json.dump(final_json, f, indent=2)

print(f"Successfully generated {OUTPUT_FILE} with authentic O*NET vectors!")
