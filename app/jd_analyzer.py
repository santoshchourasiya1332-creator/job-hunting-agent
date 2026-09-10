import os
import json
from groq import Groq

def analyze_job_description(jd_text: str, candidate_skills: list) -> dict:
    client = Groq(api_key=os.getenv("GROQ_API_KEY", "dummy_key"))

    prompt = f"""
    You are an automated ATS evaluator. Compare the following Candidate Skills against the Job Description.

    Candidate Skills: {', '.join(candidate_skills)}
    Job Description: {jd_text}

    Return ONLY a JSON object with this format:
    {{
    "match_score": <integer_0_to_100>,
    "matching_skills": [<list_of_matched_skills>],
    "missing_skills": [<list_of_missing_skills>]
    }}
    Do not invent or add skills not present in Candidate Skills.
    """

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            temperature=0.1
        )
        result_text = response.choices[0].message.content
        return json.loads(result_text)
    except Exception as e:
        matched = [s for s in candidate_skills if s.lower() in jd_text.lower()]
        score = int((len(matched) / len(candidate_skills)) * 100) if candidate_skills else 0
        return {"match_score": score, "matching_skills": matched, "missing_skills": []}