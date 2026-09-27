from typing import List

from pydantic import BaseModel, Field, field_validator


class PromptRequest(BaseModel):
    story_prompt: str = Field(
        ...,
        min_length=5,
        max_length=2000
    )

    character_name: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    setting: str = Field(
        ...,
        min_length=1,
        max_length=200
    )

    tone: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    art_style: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    @field_validator("*")
    @classmethod
    def clean_values(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Field cannot be empty")

        return value


class Panel(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    image_prompt: str
    narration: str = ""
    dialogue: List[str] = Field(default_factory=list)
    image_path: str = ""


class ComicResponse(BaseModel):
    panels: List[Panel]
    pdf_path: str