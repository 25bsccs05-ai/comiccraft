import json
import os
import re

from typing import Any, Dict, List

from google import genai
from google.genai import types


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Please add it to your .env file."
        )

    return genai.Client(api_key=api_key)


def extract_json(text: str) -> Any:
    text = text.strip()

    text = re.sub(
        r"^(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s*$",
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
                "Gemini did not return valid JSON."
            )

        return json.loads(match.group(0))


def generate_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str
) -> List[Dict[str, Any]]:

    model = os.getenv(
        "GEMINI_FLASH_MODEL",
        "gemini-3.8-flash"
    )

    prompt = f"""
Create a creative five-panel comic outline.

Story:
{story_prompt}

Main character:
{character_name}

Setting:
{setting}

Tone:
{tone}

Art style:
{art_style}

Return ONLY valid JSON.

The JSON must contain exactly 5 objects.

Each object must contain:

panel_number
title
scene_description
image_prompt

The five panels should have:

Panel 1 - Introduction
Panel 2 - Story development
Panel 3 - Conflict or turning point
Panel 4 - Climax
Panel 5 - Ending

Keep the main character consistent throughout.
"""

    client = get_client()

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.9,
            max_output_tokens=3000,
            response_mime_type="application/json"
        )
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    data = extract_json(response.text)

    if not isinstance(data, list):
        raise ValueError(
            "Gemini response is not a list."
        )

    if len(data) != 5:
        raise ValueError(
            "Comic outline must contain exactly 5 panels."
        )

    panels = []

    for index, panel in enumerate(data, start=1):
        panels.append({
            "panel_number": index,
            "title": str(
                panel.get(
                    "title",
                    f"Panel {index}"
                )
            ),
            "scene_description": str(
                panel.get(
                    "scene_description",
                    ""
                )
            ),
            "image_prompt": str(
                panel.get(
                    "image_prompt",
                    ""
                )
            )
        })

    return panels