"""
ai_analyzer.py
Sends email content to a LOCAL Qwen model via LM Studio's local server.
No data leaves your machine — 100% offline.

LM Studio exposes an OpenAI-compatible API at http://localhost:1234.
We use the standard `openai` Python library pointed at that local address.

Per-email JSON files are saved to outputs/json/ as each email is processed,
so you can inspect intermediate results before the final Excel is written.
"""

import json
import re
from pathlib import Path
from openai import OpenAI

LM_STUDIO_BASE_URL = "http://localhost:1234/v1"

# Must match the model name shown in LM Studio → My Models tab.
MODEL_NAME = "qwen3.5-9b"

JSON_OUTPUT_DIR = "outputs/json"


def analyze_email(client: OpenAI, email_data: dict) -> dict:
    """
    Send one email to the local Qwen model and get keywords + summary back.
    Summary will be written in Bahasa Indonesia.
    Returns the original email dict enriched with 'keywords' and 'summary'.
    """
    prompt = _build_prompt(email_data)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        max_tokens=512,
        temperature=0.3,
        messages=[
            {
                "role": "system",
                "content": (
                    "Kamu adalah analis email. "
                    "Selalu jawab dengan JSON valid saja. Tidak ada teks tambahan."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    )

    raw_text = response.choices[0].message.content.strip()
    result = _parse_response(raw_text)

    return {
        **email_data,
        "keywords": result.get("keywords", ""),
        "summary": result.get("summary", ""),
    }


def analyze_all_emails(emails: list[dict]) -> list[dict]:
    """
    Analyze all emails one by one.
    Each result is saved as a JSON file immediately after processing,
    before moving on to the next email.
    """
    Path(JSON_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    client = OpenAI(base_url=LM_STUDIO_BASE_URL, api_key="lm-studio")

    results = []
    for i, email_data in enumerate(emails, 1):
        print(f"  [{i}/{len(emails)}] {email_data['subject'][:60]}...")
        try:
            enriched = analyze_email(client, email_data)
        except Exception as e:
            print(f"    ✗ Gagal: {e}")
            enriched = {
                **email_data,
                "keywords": "error",
                "summary": f"Analisis gagal: {e}",
            }

        _save_json(enriched, i)
        results.append(enriched)

    return results


def _build_prompt(email_data: dict) -> str:
    return f"""Analisis email berikut dan jawab HANYA dengan objek JSON. Tanpa penjelasan tambahan.

Email:
Subject: {email_data['subject']}
From: {email_data['sent_from']}
To: {email_data['sent_to']}
Date: {email_data['date']}
Body:
{email_data['body']}

Jawab dengan format JSON berikut:
{{
  "keywords": "kata_kunci1, kata_kunci2, kata_kunci3, kata_kunci4, kata_kunci5",
  "summary": "Satu atau dua kalimat dalam Bahasa Indonesia yang merangkum isi email ini. buat secara simple dan langsung menjelaskan substansi inti saja (straightforward)."
}}"""


def _save_json(email_data: dict, index: int):
    """Save a single analyzed email result to outputs/json/<index>_<filename>.json"""
    base_name = Path(email_data.get("filename", f"email_{index}")).stem
    safe_name = re.sub(r"[^\w\-]", "_", base_name)
    output_path = Path(JSON_OUTPUT_DIR) / f"{index:03d}_{safe_name}.json"

    # Exclude raw body and internal date_parsed field from JSON output
    exclude_keys = {"body", "date_parsed"}
    data_to_save = {k: v for k, v in email_data.items() if k not in exclude_keys}

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=2)

    print(f"    ✓ JSON → {output_path}")


def _parse_response(raw_text: str) -> dict:
    """
    Parse JSON from the model response.
    Qwen sometimes wraps output in <think>...</think> tags (thinking mode).
    We strip those before parsing.
    """
    # Remove <think>...</think> blocks if present (Qwen3 thinking mode)
    if "<think>" in raw_text:
        raw_text = raw_text.split("</think>")[-1].strip()

    # Strip markdown code fences if present
    clean = raw_text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        return {"keywords": "", "summary": clean}
