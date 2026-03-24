# 🤖 AI Resume Analyzer

An AI-powered resume analysis tool that parses PDF resumes and provides structured feedback using **Mistral AI**.

## 📁 Project Structure

```
resume-analyzer/
├── backend/
│   ├── main.py              # FastAPI app — API endpoints
│   ├── analyzer.py           # Mistral AI integration & prompt engineering
│   ├── pdf_parser.py         # PDF text extraction (PyPDF2)
│   ├── models.py             # Pydantic models for structured output
│   ├── requirements.txt      # Backend dependencies
│   ├── .env                  # Your API key (create from .env.example)
│   └── .env.example          # Template
├── frontend/
│   ├── app.py                # Streamlit UI
│   └── requirements.txt      # Frontend dependencies
└── README.md
```

## 🚀 Setup & Run

### 1. Get a Mistral API Key
- Go to [console.mistral.ai](https://console.mistral.ai/) and get your API key

### 2. Setup Backend
```bash
cd resume-analyzer/backend

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file with your key
copy .env.example .env
# Edit .env and add your MISTRAL_API_KEY

# Start the server
uvicorn main:app --reload
```

The API will be running at `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

### 3. Setup Frontend (in a new terminal)
```bash
cd resume-analyzer/frontend

pip install -r requirements.txt

streamlit run app.py
```

The UI will open at `http://localhost:8501`

## 🎯 Features

- **PDF Parsing** — Extract text from multi-page resumes
- **AI Analysis** — Structured scoring across 5 categories
- **Skills Extraction** — Automatically identifies technical & soft skills
- **ATS Tips** — Actionable tips to beat Applicant Tracking Systems
- **Targeted Analysis** — Optional job role for tailored feedback
- **Beautiful UI** — Dark theme with Plotly charts and styled cards

## 🧠 What You'll Learn (AI Engineering Skills)

| Concept | Where |
|---------|-------|
| REST API design | `main.py` — FastAPI endpoints, error handling |
| Prompt engineering | `analyzer.py` — System prompt, structured output |
| LLM integration | `analyzer.py` — Mistral API, JSON mode |
| Pydantic models | `models.py` — Type-safe structured output |
| File processing | `pdf_parser.py` — Binary file handling |
| Frontend-backend integration | `app.py` — API calls, state management |
