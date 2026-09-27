import os
import re
import uuid

from pathlib import Path

from PIL import Image, ImageDraw

BASE_DIR = Path(
    __file__
).resolve().parent.parent

PANELS_DIR = (
    BASE_DIR /
    "static" /
    "panels"
)

if not PANELS_DIR.exists():
    PANELS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

PIPELINE = None


def safe_filename(text):

    text = re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        text
    )

    return text[:50]


def load_pipeline():

    global PIPELINE

    if PIPELINE is not None:

        return PIPELINE

    import torch

    from diffusers import (
        StableDiffusionPipeline
    )

    model_id = os.getenv(
        "STABLE_DIFFUSION_MODEL",
        "runwayml/stable-diffusion-v1-5"
    )

    device = os.getenv(
        "IMAGE_DEVICE",
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    dtype = (
        torch.float16
        if device == "cuda"
        else torch.float32
    )

    PIPELINE = (
        StableDiffusionPipeline
        .from_pretrained(
            model_id,
            torch_dtype=dtype
        )
    )

    PIPELINE = PIPELINE.to(
        device
    )

    return PIPELINE


def create_fallback_image(
    prompt,
    output_path
):

    image = Image.new(
        "RGB",
        (768, 512),
        "white"
    )

    draw = ImageDraw.Draw(
        image
    )

    draw.rectangle(
        (20, 20, 748, 492),
        outline="black",
        width=4
    )

    draw.text(
        (45, 50),
        "ComicCraft",
        fill="black"
    )

    draw.text(
        (45, 100),
        prompt[:500],
        fill="black"
    )

    image.save(
        output_path
    )


def generate_image(
    image_prompt: str,
    panel_number: int
):

    filename = (
        f"panel_{panel_number}_"
        f"{uuid.uuid4().hex[:8]}.png"
    )

    output_path = (
        PANELS_DIR /
        filename
    )

    mode = os.getenv(
        "IMAGE_MODE",
        "diffusers"
    )

    # Useful for testing the website first.
    if mode == "fallback":

        create_fallback_image(
            image_prompt,
            output_path
        )

        return (
            f"/static/panels/"
            f"{filename}"
        )

    pipe = load_pipeline()

    steps = int(
        os.getenv(
            "IMAGE_STEPS",
            "25"
        )
    )

    guidance = float(
        os.getenv(
            "IMAGE_GUIDANCE",
            "7.5"
        )
    )

    width = int(
        os.getenv(
            "IMAGE_WIDTH",
            "512"
        )
    )

    height = int(
        os.getenv(
            "IMAGE_HEIGHT",
            "512"
        )
    )

    prompt = (
        f"{image_prompt}. "
        "Comic book illustration, "
        "detailed characters, "
        "cinematic composition, "
        "clear scene, "
        "high quality, "
        "no text, no watermark."
    )

    negative_prompt = (
        "blurry, low quality, "
        "deformed, distorted face, "
        "extra fingers, bad hands, "
        "duplicate characters, "
        "text, watermark"
    )

    result = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=steps,
        guidance_scale=guidance,
        width=width,
        height=height
    )

    image = result.images[0]

    image.save(
        output_path
    )

    return (
        f"/static/panels/"
        f"{filename}"
    )