from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from engine.compositor import run_prism
from api.data_store import load_prism_data
from api.gemini_agent import get_prism_counsel
from api.live_market import scrape_live_market

app = FastAPI(title="PRISM Engine API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For hackathon local dev
    allow_methods=["*"],
    allow_headers=["*"],
)

prism_data = load_prism_data()
careers = prism_data["careers"]
demand = prism_data["demand"]
scholarships = prism_data["scholarships"]
exams = prism_data["exams"]

class AnalyzeRequest(BaseModel):
    student_form: dict
    parent_form: dict
    institution_type: str = "private"

class ChatRequest(BaseModel):
    engine_output: dict
    student_profile: dict
    parent_profile: dict
    user_message: str
    language: str = "English"
    history: list = Field(default_factory=list)

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    return run_prism(req.student_form, req.parent_form, careers, demand, scholarships, exams, req.institution_type)

@app.post("/chat")
def chat(req: ChatRequest):
    return get_prism_counsel(req.engine_output, req.student_profile, req.parent_profile, req.user_message, req.language, req.history)

@app.get("/careers")
def list_careers():
    return [{"id": c.get("career_id"), "label": c.get("name", c.get("career_id", ""))} for c in careers]

@app.get("/health")
def health():
    return {"status": "ok", "careers_loaded": len(careers), "data_source": prism_data["source"]}

@app.get("/live-market/{career_id}")
def live_market(career_id: str):
    career = next((c for c in careers if c.get("career_id") == career_id), {})
    return scrape_live_market(career_id, career.get("name"))
