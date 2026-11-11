"""
Groq AI Service
- Speech-to-Text: Groq Whisper (whisper-large-v3)
- Classification: Groq LLM (llama-3.3-70b-versatile)
"""

import json
import logging
import re

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

GROQ_API_BASE = "https://api.groq.com/openai/v1"


def transcribe_audio(audio_file_path: str) -> dict:
    api_key = settings.GROQ_API_KEY
    if not api_key:
        return {"success": False, "transcript": "", "error": "GROQ_API_KEY not configured."}

    url = f"{GROQ_API_BASE}/audio/transcriptions"
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        with open(audio_file_path, "rb") as f:
            files = {"file": (audio_file_path.split("/")[-1], f, "audio/mpeg")}
            data = {
                "model": settings.GROQ_WHISPER_MODEL,
                "response_format": "verbose_json",
                "language": "en",
            }
            response = requests.post(url, headers=headers, files=files, data=data, timeout=120)

        if response.status_code == 200:
            result = response.json()
            transcript = result.get("text", "").strip()
            logger.info(f"Transcription success. Length: {len(transcript)} chars")
            return {"success": True, "transcript": transcript, "error": ""}
        else:
            error_msg = f"Groq Whisper API error {response.status_code}: {response.text[:300]}"
            logger.error(error_msg)
            return {"success": False, "transcript": "", "error": error_msg}

    except FileNotFoundError:
        return {"success": False, "transcript": "", "error": f"Audio file not found: {audio_file_path}"}
    except requests.exceptions.Timeout:
        return {"success": False, "transcript": "", "error": "Groq Whisper API timed out (120s)."}
    except Exception as e:
        logger.exception("Transcription error")
        return {"success": False, "transcript": "", "error": str(e)}


def detect_keywords(transcript: str, keywords: list) -> list:
    if not transcript or not keywords:
        return []

    transcript_lower = transcript.lower()
    detected = []
    for kw in keywords:
        pattern = r'\b' + re.escape(kw.lower()) + r'\b'
        matches = re.findall(pattern, transcript_lower)
        if matches:
            detected.append({'keyword': kw, 'count': len(matches)})
    detected.sort(key=lambda x: x['count'], reverse=True)
    return detected


def classify_career_bucket(transcript: str) -> dict:
    api_key = settings.GROQ_API_KEY
    if not api_key:
        return {
            "bucket": "unclassified",
            "candidate_name": "",
            "reason": "GROQ_API_KEY not configured.",
            "confidence": 0.0,
            "error": "API key missing",
        }

    if not transcript.strip():
        return {
            "bucket": "unclassified",
            "candidate_name": "",
            "reason": "Empty transcript — cannot classify.",
            "confidence": 0.0,
            "error": "",
        }

    system_prompt = """You are an expert career classification AI for a telecalling system.

Analyze the given telecaller conversation transcript and:
1. Extract the candidate's name if mentioned in the conversation
2. Classify the candidate into EXACTLY ONE of these four buckets:

1. **fresher** — Recently graduated (within ~1 year). Just finished degree, no work experience, new to job market.
   Indicators: "just completed degree", "2024 graduate", "no experience", "fresher", "recently passed out"

2. **career_switcher** — Transitioning from a non-IT field to IT.
   Indicators: Working in banking/mechanical/sales/teaching etc. but now wants to move to IT/programming/software field.

3. **long_gap** — Graduated long ago (before 2020) with a significant career gap or break.
   Indicators: Passed out in 2012-2019, long break due to personal/family reasons, trying to restart career after years.

4. **short_gap** — Recent pass-out (2020-2023) with a small gap, internship, or temporary work.
   Indicators: Passed out 2021-2023, did internship, small gap of few months, freelance work.

Respond ONLY in this exact JSON format (no markdown, no extra text):
{
  "candidate_name": "Full Name or empty string if not found",
  "bucket": "fresher|career_switcher|long_gap|short_gap|unclassified",
  "reason": "Brief 1-5 sentence explanation based on specific evidence from the transcript",
  "confidence": 0.85
}

If the transcript has no relevant career information, use "unclassified" with confidence 0.1."""

    url = f"{GROQ_API_BASE}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.GROQ_LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Classify this telecaller conversation transcript:\n\n{transcript[:4000]}",
            },
        ],
        "max_tokens": 400,
        "temperature": 0.1,
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)

        if response.status_code == 200:
            data = response.json()
            raw_text = data["choices"][0]["message"]["content"].strip()
            logger.info(f"LLM raw response: {raw_text}")

            raw_text = re.sub(r"^```json\s*|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()

            try:
                result = json.loads(raw_text)
                bucket = result.get("bucket", "unclassified")
                valid_buckets = ["fresher", "career_switcher", "long_gap", "short_gap", "unclassified"]
                if bucket not in valid_buckets:
                    bucket = "unclassified"
                return {
                    "bucket": bucket,
                    "candidate_name": result.get("candidate_name", "").strip(),
                    "reason": result.get("reason", ""),
                    "confidence": float(result.get("confidence", 0.5)),
                    "error": "",
                }
            except json.JSONDecodeError:
                logger.error(f"Failed to parse LLM JSON: {raw_text}")
                return {
                    "bucket": "unclassified",
                    "candidate_name": "",
                    "reason": "LLM returned invalid JSON.",
                    "confidence": 0.0,
                    "error": f"JSON parse error: {raw_text[:200]}",
                }
        else:
            error_msg = f"Groq LLM API error {response.status_code}: {response.text[:300]}"
            logger.error(error_msg)
            return {
                "bucket": "unclassified",
                "candidate_name": "",
                "reason": "",
                "confidence": 0.0,
                "error": error_msg,
            }

    except requests.exceptions.Timeout:
        return {
            "bucket": "unclassified",
            "candidate_name": "",
            "reason": "",
            "confidence": 0.0,
            "error": "Groq LLM API timed out (60s).",
        }
    except Exception as e:
        logger.exception("Classification error")
        return {
            "bucket": "unclassified",
            "candidate_name": "",
            "reason": "",
            "confidence": 0.0,
            "error": str(e),
        }