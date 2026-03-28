# -*- coding: utf-8 -*-
import anthropic
import json


def analyze_email_for_phishing(subject: str, sender: str, body: str) -> dict:
    """
    Send email content to Claude AI and get phishing analysis with score.
    Returns a dict with: is_phishing, score, reasons, verdict
    """
    client = anthropic.Anthropic()

    prompt = f"""You are a cybersecurity expert specializing in phishing email detection.
Analyze the following email and determine if it is a phishing attempt.

EMAIL DETAILS:
--------------
From: {sender}
Subject: {subject}

Body:
{body}

--------------
Provide your analysis in the following JSON format ONLY (no extra text):
{{
  "is_phishing": true or false,
  "score": <integer from 0 to 100, where 0 = definitely safe, 100 = definitely phishing>,
  "verdict": "<one of: SAFE, SUSPICIOUS, PHISHING>",
  "confidence": "<one of: LOW, MEDIUM, HIGH>",
  "reasons": [
    "<reason 1>",
    "<reason 2>",
    "<reason 3>"
  ],
  "red_flags": [
    "<specific red flag if any, else empty list>"
  ],
  "recommendation": "<short advice for the user>"
}}

Scoring guide:
- 0-25: Likely safe, no phishing indicators
- 26-50: Some suspicious elements, proceed with caution
- 51-75: Multiple phishing indicators, likely phishing
- 76-100: Classic phishing attack, very high confidence"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = message.content[0].text.strip()

    # Clean up response if wrapped in markdown code block
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        response_text = "\n".join(lines[1:-1])

    result = json.loads(response_text)
    return result


def format_analysis_report(email_data: dict, analysis: dict) -> str:
    """Format the analysis result into a readable report."""
    score = analysis.get("score", 0)
    verdict = analysis.get("verdict", "UNKNOWN")
    is_phishing = analysis.get("is_phishing", False)
    confidence = analysis.get("confidence", "LOW")
    reasons = analysis.get("reasons", [])
    red_flags = analysis.get("red_flags", [])
    recommendation = analysis.get("recommendation", "")

    # Score bar visualization (ASCII only)
    filled = int(score / 5)
    bar = "#" * filled + "-" * (20 - filled)

    # Verdict indicator (plain text)
    if verdict == "SAFE":
        verdict_icon = "[SAFE]"
    elif verdict == "SUSPICIOUS":
        verdict_icon = "[SUSPICIOUS]"
    else:
        verdict_icon = "[PHISHING]"

    report = f"""
{'='*60}
EMAIL ANALYSIS REPORT
{'='*60}
From    : {email_data['sender']}
Subject : {email_data['subject']}
{'='*60}

{verdict_icon}
VERDICT        : {verdict}
PHISHING SCORE : [{bar}] {score}/100
IS PHISHING    : {"YES - DANGER" if is_phishing else "NO - SAFE"}
CONFIDENCE     : {confidence}

REASONS:
"""
    for i, reason in enumerate(reasons, 1):
        report += f"  {i}. {reason}\n"

    if red_flags:
        report += "\nRED FLAGS:\n"
        for flag in red_flags:
            report += f"  - {flag}\n"

    report += f"\nRECOMMENDATION:\n  {recommendation}\n"
    report += "=" * 60 + "\n"

    return report
