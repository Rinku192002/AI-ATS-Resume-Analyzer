import os
import json
import re
from dotenv import load_dotenv
from google import genai

# ==========================
# Load API Key
# ==========================
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise Exception("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)


# ==========================
# Resume Analysis
# ==========================
def analyze_resume(resume_text):

    prompt = f"""
You are an Expert ATS Resume Analyzer.

Analyze the resume and return ONLY VALID JSON.

{{
    "ats_score": 85,
    "technical_skills": [],
    "missing_skills": [],
    "experience_level": "",
    "job_role_fit": [],
    "strengths": [],
    "improvements": [],
    "summary": ""
}}

Resume:
{resume_text}
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text.strip()

        print("\n========== GEMINI ATS RESPONSE ==========")
        print(text)
        print("=========================================\n")

        text = re.sub(r"```json|```", "", text).strip()

        return json.loads(text)

    except Exception as e:

        print("ATS ERROR :", e)

        return {
            "ats_score": 0,
            "technical_skills": [],
            "missing_skills": [],
            "experience_level": "",
            "job_role_fit": [],
            "strengths": [],
            "improvements": [],
            "summary": "",
            "error": str(e)
        }


# ==========================
# Resume vs Job Description
# ==========================
def match_resume_with_job(resume_text, job_description):

    prompt = f"""
Compare the Resume with Job Description.

Return ONLY VALID JSON.

{{
    "match_score": 0,
    "matching_skills": [],
    "missing_skills": [],
    "recommendation": "",
    "job_fit_level": ""
}}

Resume:
{resume_text}

Job Description:
{job_description}
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text.strip()

        print("\n========== GEMINI JOB MATCH ==========")
        print(text)
        print("======================================\n")

        text = re.sub(r"```json|```", "", text).strip()

        return json.loads(text)

    except Exception as e:

        print("JOB MATCH ERROR :", e)

        return {
            "match_score": 0,
            "matching_skills": [],
            "missing_skills": [],
            "recommendation": "",
            "job_fit_level": "",
            "error": str(e)
        }


# ==========================
# Extract Score
# ==========================
def extract_score(text):

    if isinstance(text, dict):

        if "ats_score" in text:
            try:
                return int(str(text["ats_score"]).replace("%", "").replace("/100", "").strip())
            except:
                return 0

        if "match_score" in text:
            try:
                return int(str(text["match_score"]).replace("%", "").strip())
            except:
                return 0

    if isinstance(text, str):

        match = re.search(r'(\d{1,3})', text)

        if match:
            return min(int(match.group(1)), 100)

    return 0