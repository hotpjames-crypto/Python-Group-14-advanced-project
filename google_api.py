# This file name is google_api.py
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()  # This is to access the .env file holding the API key

API_KEY = os.getenv("GEMINI_API_KEY")  # kept the same env var name you were using
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "poolside/laguna-xs-2.1:free"

class AIRequestError(Exception):
    pass

def _call_openrouter(prompt_content):
    if not API_KEY:
        raise AIRequestError(
            "No API key found. Add GEMINI_API_KEY=your_key to a .env file next to these scripts."
        )

    try:
        response = requests.post(
            url=API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": MODEL,
                "messages": [
                    {"role": "user", "content": prompt_content}
                ]
            }),
            timeout=30,
        )
    except requests.exceptions.RequestException as e:
        raise AIRequestError(f"Could not reach OpenRouter: {e}")

    try:
        result = response.json()
    except ValueError:
        raise AIRequestError("OpenRouter returned an unreadable response.")

    if "error" in result:
        raise AIRequestError(f"API Error: {result['error']}")

    try:
        return result["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise AIRequestError("Unexpected response format from OpenRouter.")


def generate_travel_guide(country_data):
    country_json = json.dumps(country_data)
    prompt_content = (
        f"Using {country_json}, create a simple travel, study, or relocation guide "
        f"for someone planning to visit or move there. In addition, provide a "
        f"'Before You Travel' checklist."
    )
    return _call_openrouter(prompt_content)


def generate_comparison(country_a, country_b):
    prompt_content = (
        f"Compare {country_a} and {country_b} based on their "
        f"details (capital, currency, languages, population, region, timezone), "
        f"give a detailed difference between the two countries specifying which is best for travel, study and relocation(with valid reasons to boot)"
    )
    return _call_openrouter(prompt_content)

