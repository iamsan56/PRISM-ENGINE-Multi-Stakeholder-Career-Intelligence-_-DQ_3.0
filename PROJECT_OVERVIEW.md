# PRISM Engine: Multi-Stakeholder Career Intelligence 🚀
**Data Quest 3.0 Submission**

## 📖 1. The Problem
Traditional career counseling fails because it operates in a vacuum. It asks students what they want, but completely ignores the harsh realities of the Indian education landscape: **Parental constraints**. 

When a student's dream career clashes with a family's financial capacity, risk appetite, or geographic mobility limits, it leads to dropped-out degrees, severe educational debt, and family conflict.

## 💡 2. The PRISM Solution
**PRISM (Parent-Student Relational Intelligence & Scoring Matrix)** is a deterministic assessment engine combined with Generative AI. It treats career selection not as a single-player game, but as a **multi-stakeholder negotiation**.

Think of PRISM as a bridge:
* **Student Side:** Evaluates psychometrics (RIASEC), aptitude, and domain interests.
* **Parent Side:** Evaluates strict constraints (Max budget, loan tolerance, distance radius, risk appetite).
* **The Engine:** Mathematically calculates feasibility, generates a conflict index, and finds the highest-utility compromise pathway for both parties.

---

## 🏗️ 3. System Architecture

The project is built on a modern, decoupled architecture:

### A. Presentation Layer (React + Vite + Tailwind)
* **Gamified Ingestion:** A duolingo-style vertical node flow that collects psychometric data without feeling like an exam.
* **Decision Dashboard:** Heavy data visualization using Recharts (Radar charts for psychometrics, Quadrant scatter plots for Cost vs. Value).
* **Hyper-Local Mapping:** Integrated OpenStreetMap (via Leaflet and Nominatim API) to render realistic institution options dynamically based on the user's GPS coordinates.

### B. Gateway Layer (FastAPI)
* A high-performance Python API that ingests JSON payloads, runs strict Pydantic validation, and routes data to the mathematical engine.

### C. Deterministic Evaluation Engine (NumPy)
The core intelligence of PRISM relies on pure mathematics, avoiding the hallucinations of LLMs for critical scoring:
1. **Vectorization:** Converts qualitative survey answers into standardized vectors (0.0 to 1.0).
2. **Fit Scorer (Cosine Similarity):** Measures the angular distance between the student's vector and the canonical vectors of 30 industry pathways.
3. **Financial Solver (Deficit Amortization):** Checks gross fees against available scholarships, computes net deficit, calculates monthly EMI (at 8.5% PA), and projects ROI payback periods.
4. **PSCI (Parent-Student Conflict Index):** Calculates the weighted Euclidean distance across risk, cost, and mobility between the student and parent profiles.
5. **MAUT Ranker:** Uses Multi-Attribute Utility Theory to blend Fit (45%), Affordability (35%), and Market Demand (20%) into a final composite score.

### D. AI & Explainability Layer (Gemini 1.5 Flash)
* **PRISM Counselor:** Raw mathematical outputs (like `composite_score: 0.87`) are passed as hidden context to the Gemini API. The LLM acts as an empathetic counselor, translating the math into warm, actionable advice, SWOT analyses, and mediation strategies.

### E. Data & Knowledge Layer
* **Taxonomy:** 30 canonical careers mapped to 12 unified domains.
* **Scholarships:** 12 active Indian financial aid schemes (e.g., PM Vidya Lakshmi, NSP, AICTE) mapped to strict eligibility domains.
* **Demand Indices:** Sourced from NASSCOM and NCS (National Career Service) datasets.

---

## ⚙️ 4. The User Flow

1. **The Crisis (Start):** The user enters the Gamified Assessment Flow, presented with realistic situational questions to extract RIASEC and Aptitude traits.
2. **The Constraints:** The flow asks for strict financial budgets and mobility limits (Parental data).
3. **The Engine Runs:** Data is shipped to the FastAPI backend where matrices are calculated.
4. **The Reveal (Dashboard):** 
   * The user sees their **Top 3 Realistic Pathways**.
   * They review the **Cost vs. Value Quadrant** (highlighting careers in the "Golden" or "Danger" zones).
   * They review the **Student-Parent Alignment** card, detailing exact conflict severity and PRISM's recommended compromise careers.
   * They explore the **Interactive Map** showing real colleges near them offering that specific degree.
5. **Counseling:** The user chats with the AI assistant to ask follow-up questions about exams or skill gaps.

---

## 🎯 5. Core Metrics Delivered
Rather than outputting generic text, PRISM delivers 5 hard metrics:
1. **Career Fit Score:** Does it suit the student?
2. **Financial Feasibility:** Can the family afford it (Net EMI)?
3. **PSCI:** How far apart are the student and parent?
4. **Compromise Success:** The highest MAUT-ranked career that exists in *both* the student's and parent's top quartiles.
5. **ROI Multiplier:** Lifetime earning potential vs. Educational debt.
