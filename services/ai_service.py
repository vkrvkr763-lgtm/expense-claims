import json
import re

from google import genai
from config import GEMINI_API_KEY


# Create Gemini client
client = None

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)


def fallback_extract(text):

    text_lower = text.lower()

    amount = None
    date = None
    merchant = None
    category = "Other"

    # Extract amount
    amount_match = re.search(
        r'(?:rs\.?|inr|₹|amount|total)\s*[:\-]?\s*(\d+(?:\.\d+)?)',
        text_lower
    )

    if amount_match:
        amount = float(amount_match.group(1))

    # Extract date
    date_match = re.search(
        r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
        text
    )

    if date_match:
        date = date_match.group(1).replace("/", "-")

    # First line as merchant
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if lines:
        merchant = lines[0]

    # Category detection
    if any(
        word in text_lower
        for word in ["restaurant", "food", "meal", "cafe", "swiggy"]
    ):
        category = "Meals"

    elif any(
        word in text_lower
        for word in ["taxi", "uber", "ola", "cab"]
    ):
        category = "Taxi"

    elif any(
        word in text_lower
        for word in ["flight", "hotel", "train", "travel"]
    ):
        category = "Travel"

    elif any(
        word in text_lower
        for word in ["stationery", "office", "supplies"]
    ):
        category = "Supplies"

    return {
        "amount": amount,
        "expense_date": date,
        "merchant": merchant,
        "category": category,
        "description": text[:500]
    }


def extract_receipt(text):

    if not text:
        return fallback_extract("")

    # Gemini unavailable → fallback
    if client is None:
        print("Gemini API key not configured.")
        return fallback_extract(text)

    prompt = f"""
You are an expense receipt extraction system.

Extract information from the receipt text below.

Return ONLY valid JSON.
Do not return markdown.
Do not explain anything.

Required structure:

{{
    "amount": number,
    "expense_date": "YYYY-MM-DD",
    "merchant": "string",
    "category": "Travel | Meals | Supplies | Taxi | Other",
    "description": "short description"
}}

If a value cannot be determined, use null.

Receipt:

{text}
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.7-flash",
            contents=prompt
        )

        content = response.text.strip()

        # Remove accidental markdown fences
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

        result = json.loads(content)

        return result

    except Exception as e:

        print("GEMINI EXTRACTION ERROR:", repr(e))

        # Keep application working if AI fails
        return fallback_extract(text)