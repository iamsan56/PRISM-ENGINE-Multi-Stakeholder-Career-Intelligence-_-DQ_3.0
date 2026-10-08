# PRISM Engine 🚀
**Career, Cost & Family Fit Decision Console**

PRISM is a deterministic assessment engine combined with Generative AI that bridges the gap between a student's psychometric potential and their family's financial realities. Instead of just recommending careers, PRISM evaluates feasibility, calculates ROI, and acts as a mediator to find compromise pathways that satisfy both students and parents.

## Features
- **Gamified Assessment Flow**: Psychometric evaluation mapping to RIASEC and Aptitude dimensions.
- **Financial Constraints Engine**: Evaluates maximum family budget, loan tolerance, and calculates exact EMIs vs Career ROI.
- **PSCI (Parent-Student Conflict Index)**: Mathematically models the gap in expectations and outputs compromise pathways.
- **Hyper-Local Targeting**: Integrated OpenStreetMap/Leaflet to find relevant colleges based on actual GPS coordinates.
- **AI Explanability**: Powered by Gemini 1.5 Flash to synthesize results into conversational, actionable guidance.

## Tech Stack
- **Frontend:** React, Vite, Tailwind CSS, Recharts, Framer Motion, Leaflet
- **Backend:** Python, FastAPI, NumPy (Engine logic), Google Generative AI (Gemini)

## Setup & Installation

### 1. Backend (Python)
```bash
# Clone repository
git clone https://github.com/yourusername/prism-engine.git
cd prism-engine

# Install dependencies
pip install -r requirements.txt

# Environment variables
cp .env.example .env
# Open .env and add your GEMINI_API_KEY

# Run the FastAPI server
python -m uvicorn api.main:app --port 8000 --reload
```

### 2. Frontend (React)
Open a second terminal window:
```bash
cd frontend

# Install Node modules
npm install

# Run the Vite development server
npm run dev
```

Navigate to `http://localhost:5173` in your browser to launch the PRISM console.

## Project Structure
* `/api` - FastAPI routes and Gemini AI agent integration.
* `/engine` - The core deterministic mathematical algorithms (vectorization, financial solver, market blender).
* `/data` - Static JSON databases mapping canonical careers, Indian scholarships, exams, and market demand indices.
* `/frontend` - The React application featuring the gamified assessment and dark-mode Results Dashboard.
