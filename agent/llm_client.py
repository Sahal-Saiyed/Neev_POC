import json
import requests
from config import get_setting, require_setting


LLM_API_KEY = require_setting("LLM_API_KEY")

LLM_BASE_URL = get_setting(
    "LLM_BASE_URL",
    "https://openrouter.ai/api/v1/chat/completions"
)

LLM_MODEL = get_setting(
    "LLM_MODEL",
    "openai/gpt-4o-mini"
)


def call_llm(messages):
    if not LLM_API_KEY:
        raise Exception("LLM_API_KEY missing in .env")

    if not LLM_BASE_URL:
        raise Exception("LLM_BASE_URL missing in .env")

    if not LLM_MODEL:
        raise Exception("LLM_MODEL missing in .env")

    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": 0.1
    }

    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        LLM_BASE_URL,
        headers=headers,
        json=payload,
        timeout=60
    )

    if response.status_code != 200:
        raise Exception(f"LLM API error: {response.status_code} - {response.text}")

    data = response.json()
    return data["choices"][0]["message"]["content"]


def extract_json_from_text(text: str):
    text = text.strip()

    if text.startswith("```"):
        text = (
            text.replace("```json", "")
            .replace("```JSON", "")
            .replace("```", "")
            .strip()
        )

    try:
        return json.loads(text)
    except Exception:
        pass

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:
        json_text = text[start:end + 1]

        try:
            return json.loads(json_text)
        except Exception:
            pass

    raise ValueError(f"LLM did not return valid JSON. Raw response: {text}")