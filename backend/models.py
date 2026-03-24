"""
Pydantic models for structured resume analysis output.
These models define the exact shape of data the AI returns.
"""

from pydantic import BaseModel, Field


class CategoryScores(BaseModel):
    """Individual category scores (0-100) for resume evaluation."""
    skills_relevance: int = Field(..., ge=0, le=100, description="How relevant and strong the listed skills are")
    experience_quality: int = Field(..., ge=0, le=100, description="Quality and depth of work experience")
    education: int = Field(..., ge=0, le=100, description="Educational background strength")
    formatting: int = Field(..., ge=0, le=100, description="Resume structure, readability, and formatting")
    impact_metrics: int = Field(..., ge=0, le=100, description="Use of quantifiable achievements and impact")


class AnalysisResult(BaseModel):
    """Complete resume analysis result returned to the client."""
    overall_score: int = Field(..., ge=0, le=100, description="Overall resume score")
    summary: str = Field(..., description="2-3 sentence executive summary of the resume")
    category_scores: CategoryScores
    extracted_skills: list[str] = Field(..., description="List of technical and soft skills found")
    strengths: list[str] = Field(..., description="Key strengths of the resume")
    weaknesses: list[str] = Field(..., description="Areas that need improvement")
    suggestions: list[str] = Field(..., description="Actionable improvement suggestions")
    ats_tips: list[str] = Field(..., description="Tips to pass Applicant Tracking Systems")


class AnalyzeRequest(BaseModel):
    """Request body for the analyze endpoint (used alongside file upload)."""
    job_role: str | None = Field(None, description="Optional target job role for tailored analysis")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    service: str = "resume-analyzer-api"


# ── Feature 1: Resume Comparison ─────────────────────────────────────
class ResumeProfile(BaseModel):
    """Brief profile of a single resume for comparison."""
    name: str = Field(..., description="Candidate name or 'Resume A'/'Resume B'")
    overall_score: int = Field(..., ge=0, le=100)
    top_skills: list[str] = Field(..., description="Top 5 skills")
    experience_years: str = Field(..., description="Estimated years of experience")
    strongest_area: str = Field(..., description="What this resume does best")
    weakest_area: str = Field(..., description="Biggest gap")


class ComparisonResult(BaseModel):
    """Side-by-side comparison of two resumes."""
    winner: str = Field(..., description="Which resume is stronger: 'A' or 'B'")
    summary: str = Field(..., description="2-3 sentence comparison summary")
    resume_a: ResumeProfile
    resume_b: ResumeProfile
    detailed_comparison: list[str] = Field(..., description="Point-by-point comparison notes")
    recommendation: str = Field(..., description="Who should be hired and why")


# ── Feature 2: JD Matching ───────────────────────────────────────────
class MatchResult(BaseModel):
    """Resume vs Job Description matching result."""
    match_percentage: int = Field(..., ge=0, le=100, description="Overall match %")
    fit_summary: str = Field(..., description="2-3 sentence fit assessment")
    matched_skills: list[str] = Field(..., description="Skills that match the JD")
    missing_skills: list[str] = Field(..., description="Skills required by JD but missing from resume")
    matched_requirements: list[str] = Field(..., description="JD requirements the candidate meets")
    gaps: list[str] = Field(..., description="Areas where candidate falls short")
    suggestions_to_improve: list[str] = Field(..., description="How to tailor resume for this JD")


# ── Feature 3: AI Rewrite ────────────────────────────────────────────
class RewriteItem(BaseModel):
    """A single bullet point rewrite."""
    original: str = Field(..., description="Original bullet point")
    rewritten: str = Field(..., description="Improved version")
    explanation: str = Field(..., description="Why this is better")


class RewriteResult(BaseModel):
    """Result of AI rewriting weak bullet points."""
    rewrites: list[RewriteItem] = Field(..., description="List of rewritten bullet points")
    general_tips: list[str] = Field(..., description="General writing tips for better bullet points")
