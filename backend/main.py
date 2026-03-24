"""
FastAPI application — Resume Analyzer API.
Endpoints: analyze, compare, match, rewrite.
"""

import logging

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from analyzer import analyze_resume, compare_resumes, match_job_description, rewrite_bullets
from models import AnalysisResult, ComparisonResult, HealthResponse, MatchResult, RewriteResult
from pdf_parser import extract_text

# ── Logging ───────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s",
)
logger = logging.getLogger(__name__)

# ── FastAPI app ───────────────────────────────────────────────────────
app = FastAPI(
    title="Resume Analyzer API",
    description="AI-powered resume analysis, comparison, JD matching, and bullet rewriting.",
    version="2.0.0",
)

# ── CORS ──────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helpers ───────────────────────────────────────────────────────────
async def _read_pdf(file: UploadFile) -> str:
    """Validate and extract text from an uploaded PDF."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum is 10MB.")

    try:
        return extract_text(contents)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


# ── Health ────────────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse()


# ── 1. Analyze ────────────────────────────────────────────────────────
@app.post("/analyze", response_model=AnalysisResult)
async def analyze(
    file: UploadFile = File(...),
    job_role: str | None = Form(None),
):
    """Upload a PDF resume and get structured AI analysis."""
    resume_text = await _read_pdf(file)
    logger.info(f"Analyze: {file.filename} ({len(resume_text)} chars)")
    try:
        return await analyze_resume(resume_text, job_role)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))


# ── 2. Compare ────────────────────────────────────────────────────────
@app.post("/compare", response_model=ComparisonResult)
async def compare(
    file_a: UploadFile = File(..., description="First resume (PDF)"),
    file_b: UploadFile = File(..., description="Second resume (PDF)"),
):
    """Upload 2 PDF resumes and get a side-by-side comparison."""
    text_a = await _read_pdf(file_a)
    text_b = await _read_pdf(file_b)
    logger.info(f"Compare: {file_a.filename} vs {file_b.filename}")
    try:
        return await compare_resumes(text_a, text_b)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))


# ── 3. JD Match ──────────────────────────────────────────────────────
@app.post("/match", response_model=MatchResult)
async def match(
    file: UploadFile = File(..., description="Resume PDF"),
    job_description: str = Form(..., description="Job description text"),
):
    """Upload a resume + paste a JD, get match percentage and gap analysis."""
    resume_text = await _read_pdf(file)
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")
    logger.info(f"JD Match: {file.filename} ({len(job_description)} char JD)")
    try:
        return await match_job_description(resume_text, job_description)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))


# ── 4. Rewrite ────────────────────────────────────────────────────────
class RewriteRequest(BaseModel):
    bullet_text: str
    context: str | None = None


@app.post("/rewrite", response_model=RewriteResult)
async def rewrite(req: RewriteRequest):
    """Send weak bullet points and get AI-powered rewrites."""
    if not req.bullet_text.strip():
        raise HTTPException(status_code=400, detail="Bullet text cannot be empty.")
    logger.info(f"Rewrite: {len(req.bullet_text)} chars")
    try:
        return await rewrite_bullets(req.bullet_text, req.context)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))


# ── Run ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

