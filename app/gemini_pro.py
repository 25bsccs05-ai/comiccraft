import json
import os
import re

from typing import Any, Dict, List

from dotenv import load_dotenv

from google import genai
from google.genai import types


def get_client():

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing."
        )

    return genai.Client(
        api_key=api_key
    )


def extract_json(text: str) -> Any:

    text = text.strip()

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    try:

        return json.loads(text)

    except json.JSONDecodeError:

        match = re.search(
            r"\[[\s\S]*\]",
            text
        )

        if not match:
            raise ValueError(
                "Invalid JSON returned by Gemini."
            )

        return json.loads(
            match.group(0)
        )


def generate_story(
    outline: List[Dict[str, Any]],
    character_name: str,
    tone: str,
    art_style: str
) -> List[Dict[str, Any]]:

    model = os.getenv(
        "GEMINI_PRO_MODEL",
        "gemini-2.5-pro"
    )

    outline_json = json.dumps(
        outline,
        indent=2,
        ensure_ascii=False
    )

    prompt = f"""
Create the narration and dialogue for a five-panel comic.

Main character:
{character_name}

Tone:
{tone}

Art style:
{art_style}

Comic outline:

{outline_json}

Return ONLY valid JSON.

Create exactly five objects.

Each object must contain:

panel_number
narration
dialogue

Narration should contain 1 to 3 short sentences.

Dialogue should be an array with up to 3 short dialogue lines.

Keep the story continuous from panel to panel.
"""

    client = get_client()

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.85,
            max_output_tokens=3500,
            response_mime_type="application/json"
        )
    )

    if not response.text:

        raise RuntimeError(
            "Gemini returned an empty story."
        )

    data = extract_json(
        response.text
    )

    if len(data) != 5:

        raise ValueError(
            "Story must contain exactly 5 panels."
        )

    result = []

    for index, item in enumerate(
        data,
        start=1
    ):

        dialogue = item.get(
            "dialogue",
            []
        )

        if not isinstance(
            dialogue,
            list
        ):

            dialogue = [
                str(dialogue)
            ]

        result.append({

            "panel_number": index,

            "narration": str(
                item.get(
                    "narration",
                    ""
                )
            ),

            "dialogue": [
                str(line)
                for line in dialogue[:3]
            ]
        })

    return result