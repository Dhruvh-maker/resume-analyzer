"""
Resume analysis service using Mistral AI.
Sends resume text to Mistral with a structured prompt and parses the JSON response.
"""

import json
import logging
import os

from dotenv import load_dotenv
from mistralai import Mistral

from models import AnalysisResult, ComparisonResult, MatchResult, RewriteResult

load_dotenv()
logger = logging.getLogger(__name__)

# ── Mistral client setup ──────────────────────────────────────────────
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
if not MISTRAL_API_KEY:
    raise RuntimeError("MISTRAL_API_KEY is not set. Add it to your .env file.")

client = Mistral(api_key=MISTRAL_API_KEY)
MODEL = "mistral-small-latest"  # Fast, cheap, great for structured tasks


# ── System prompt ─────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert resume reviewer and career coach with 15+ years of experience in tech recruiting.

Your job is to analyze the provided resume text and return a detailed, structured evaluation.

You MUST respond with ONLY valid JSON matching this exact schema (no markdown, no explanation, just JSON):
{
  "overall_score": <int 0-100>,
  "summary": "<2-3 sentence executive summary>",
  "category_scores": {
    "skills_relevance": <int 0-100>,
    "experience_quality": <int 0-100>,
    "education": <int 0-100>,
    "formatting": <int 0-100>,
    "impact_metrics": <int 0-100>
  },
  "extracted_skills": ["skill1", "skill2", ...],
  "strengths": ["strength1", "strength2", ...],
  "weaknesses": ["weakness1", "weakness2", ...],
  "suggestions": ["actionable suggestion1", "actionable suggestion2", ...],
  "ats_tips": ["ATS optimization tip1", "ATS optimization tip2", ...]
}

Scoring guidelines:
- 90-100: Exceptional, ready for top-tier companies
- 75-89: Strong, minor improvements needed
- 60-74: Average, several areas need work
- 40-59: Below average, needs significant revision
- 0-39: Poor, major overhaul required

Be specific, actionable, and honest. Reference actual content from the resume.
Each list should have 3-6 items. Skills list can have up to 15 items."""


def _build_user_prompt(resume_text: str, job_role: str | None = None) -> str:
    """Build the user prompt with optional job-role targeting."""
    prompt = f"Here is the resume text to analyze:\n\n---\n{resume_text}\n---"
    if job_role:
        prompt += (
            f"\n\nThe candidate is targeting the role of: **{job_role}**. "
            "Tailor your analysis and suggestions specifically for this role. "
            "Evaluate how well-suited the resume is for this position."
        )
    else:
        prompt += "\n\nProvide a general analysis suitable for a tech industry role."
    return prompt


async def analyze_resume(resume_text: str, job_role: str | None = None) -> AnalysisResult:
    """
    Analyze a resume using Mistral AI and return structured results.

    Args:
        resume_text: Extracted text content from the resume PDF.
        job_role: Optional target job role for tailored analysis.

    Returns:
        AnalysisResult with scores, feedback, and suggestions.

    Raises:
        RuntimeError: If Mistral API call fails or returns invalid JSON.
    """
    user_prompt = _build_user_prompt(resume_text, job_role)

    logger.info(f"Sending resume ({len(resume_text)} chars) to Mistral for analysis...")

    try:
        response = await client.chat.complete_async(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,          # Low temp for consistent structured output
            response_format={"type": "json_object"},  # Force JSON mode
        )
    except Exception as e:
        logger.error(f"Mistral API call failed: {e}")
        raise RuntimeError(f"AI analysis failed: {str(e)}") from e

    # Parse the response
    raw_content = response.choices[0].message.content
    logger.info(f"Received response ({len(raw_content)} chars) from Mistral.")

    try:
        data = json.loads(raw_content)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Mistral response as JSON: {raw_content[:500]}")
        raise RuntimeError("AI returned invalid JSON. Please try again.") from e

    # Validate with Pydantic
    try:
        result = AnalysisResult(**data)
    except Exception as e:
        logger.error(f"Pydantic validation failed: {e}")
        raise RuntimeError(f"AI response didn't match expected format: {str(e)}") from e

    logger.info(f"Analysis complete — Overall score: {result.overall_score}/100")
    return result


# ── Shared helper ─────────────────────────────────────────────────────
async def _call_mistral(system_prompt: str, user_prompt: str, model_class: type):
    """Shared helper to call Mistral, parse JSON, validate with Pydantic."""
    try:
        response = await client.chat.complete_async(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
    except Exception as e:
        logger.error(f"Mistral API call failed: {e}")
        raise RuntimeError(f"AI analysis failed: {str(e)}") from e

    raw = response.choices[0].message.content
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError("AI returned invalid JSON. Please try again.") from e

    try:
        return model_class(**data)
    except Exception as e:
        raise RuntimeError(f"AI response format error: {str(e)}") from e


# ══════════════════════════════════════════════════════════════════════
# Feature 1: Resume Comparison
# ══════════════════════════════════════════════════════════════════════
COMPARE_PROMPT = """You are an expert recruiter comparing two resumes side-by-side.

Respond with ONLY valid JSON matching this schema:
{
  "winner": "A" or "B",
  "summary": "<2-3 sentence comparison>",
  "resume_a": {
    "name": "<candidate name or 'Resume A'>",
    "overall_score": <int 0-100>,
    "top_skills": ["skill1", ...],
    "experience_years": "<e.g. '3-4 years'>",
    "strongest_area": "<best aspect>",
    "weakest_area": "<biggest gap>"
  },
  "resume_b": { ...same structure... },
  "detailed_comparison": ["point1", "point2", ...],
  "recommendation": "<who to hire and why>"
}

Be specific. Reference actual content from both resumes. Give 4-6 comparison points."""


async def compare_resumes(text_a: str, text_b: str) -> ComparisonResult:
    """Compare two resumes side-by-side."""
    logger.info("Comparing two resumes...")
    user_prompt = f"RESUME A:\n---\n{text_a}\n---\n\nRESUME B:\n---\n{text_b}\n---"
    return await _call_mistral(COMPARE_PROMPT, user_prompt, ComparisonResult)


# ══════════════════════════════════════════════════════════════════════
# Feature 2: JD Matching
# ══════════════════════════════════════════════════════════════════════
MATCH_PROMPT = """You are an expert ATS system and recruiter analyzing how well a resume matches a job description.

Respond with ONLY valid JSON matching this schema:
{
  "match_percentage": <int 0-100>,
  "fit_summary": "<2-3 sentence assessment>",
  "matched_skills": ["skill1", "skill2", ...],
  "missing_skills": ["skill1", "skill2", ...],
  "matched_requirements": ["requirement the candidate meets", ...],
  "gaps": ["area where candidate falls short", ...],
  "suggestions_to_improve": ["how to tailor resume for this JD", ...]
}

Be honest and specific. A 100% match is extremely rare. Reference actual skills and requirements."""


async def match_job_description(resume_text: str, jd_text: str) -> MatchResult:
    """Analyze how well a resume matches a job description."""
    logger.info("Matching resume against job description...")
    user_prompt = f"RESUME:\n---\n{resume_text}\n---\n\nJOB DESCRIPTION:\n---\n{jd_text}\n---"
    return await _call_mistral(MATCH_PROMPT, user_prompt, MatchResult)


# ══════════════════════════════════════════════════════════════════════
# Feature 3: AI Rewrite
# ══════════════════════════════════════════════════════════════════════
REWRITE_PROMPT = """You are an expert resume writer who transforms weak bullet points into powerful, impactful ones.

Rules for rewriting:
- Use strong action verbs (Led, Architected, Optimized, Spearheaded)
- Add quantifiable metrics where possible (%, $, time saved)
- Follow the XYZ formula: Accomplished [X] as measured by [Y], by doing [Z]
- Keep each bullet concise (1-2 lines max)

Respond with ONLY valid JSON matching this schema:
{
  "rewrites": [
    {
      "original": "<exact original text>",
      "rewritten": "<improved version>",
      "explanation": "<why this is better, 1 sentence>"
    },
    ...
  ],
  "general_tips": ["tip1", "tip2", "tip3"]
}

Provide 3-5 general writing tips."""


async def rewrite_bullets(bullet_text: str, context: str | None = None) -> RewriteResult:
    """Rewrite weak resume bullet points into strong ones."""
    logger.info("Rewriting bullet points...")
    user_prompt = f"Here are the bullet points to improve:\n\n{bullet_text}"
    if context:
        user_prompt += f"\n\nContext about the candidate's role/industry: {context}"
    return await _call_mistral(REWRITE_PROMPT, user_prompt, RewriteResult)

