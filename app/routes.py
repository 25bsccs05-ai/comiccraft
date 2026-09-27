import asyncio

from pathlib import Path

from dotenv import load_dotenv

from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request
)

from fastapi.responses import (
    FileResponse,
    RedirectResponse
)

from fastapi.templating import (
    Jinja2Templates
)

from app.models import PromptRequest

from app.gemini_flash import (
    generate_outline
)

from app.gemini_pro import (
    generate_story
)

from app.image_generator import (
    generate_image
)

from app.layout_builder import (
    build_comic_layout
)

from app.exporters import (
    save_pdf
)


load_dotenv()


BASE_DIR = Path(
    __file__
).resolve().parent.parent


templates = Jinja2Templates(
    directory=str(
        BASE_DIR /
        "templates"
    )
)


router = APIRouter()


def generate_comic_sync(
    story_prompt,
    character_name,
    setting,
    tone,
    art_style
):

    # Step 1
    outline = generate_outline(
        story_prompt,
        character_name,
        setting,
        tone,
        art_style
    )

    # Step 2
    story = generate_story(
        outline,
        character_name,
        tone,
        art_style
    )

    # Step 3
    image_paths = []

    for panel in outline:

        image = generate_image(
            panel["image_prompt"],
            panel["panel_number"]
        )

        image_paths.append(
            image
        )

    # Step 4
    layout = build_comic_layout(
        outline,
        story,
        image_paths
    )

    # Step 5
    pdf_path = save_pdf(
        layout
    )

    return (
        layout,
        pdf_path
    )


@router.get("/")
async def home(
    request: Request
):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title":
                "ComicCraft",
            "error":
                None
        }
    )


@router.post("/generate")
async def generate(
    request: Request,

    story_prompt: str = Form(...),

    character_name: str = Form(...),

    setting: str = Form(...),

    tone: str = Form(...),

    art_style: str = Form(...)
):

    try:

        data = PromptRequest(

            story_prompt=story_prompt,

            character_name=character_name,

            setting=setting,

            tone=tone,

            art_style=art_style
        )

        layout, pdf_path = (
            await asyncio.to_thread(
                generate_comic_sync,

                data.story_prompt,

                data.character_name,

                data.setting,

                data.tone,

                data.art_style
            )
        )

        return templates.TemplateResponse(

            request=request,

            name="comic_preview.html",

            context={

                "title":
                    "ComicCraft Preview",

                "layout":
                    layout,

                "pdf_path":
                    pdf_path,

                "character_name":
                    data.character_name
            }
        )

    except Exception as error:

        return templates.TemplateResponse(

            request=request,

            name="index.html",

            context={

                "title":
                    "ComicCraft",

                "error":
                    str(error)
            },

            status_code=500
        )


@router.post(
    "/generate-comic/json"
)
async def generate_json(
    data: PromptRequest
):

    try:

        layout, pdf_path = (
            await asyncio.to_thread(

                generate_comic_sync,

                data.story_prompt,

                data.character_name,

                data.setting,

                data.tone,

                data.art_style
            )
        )

        return {

            "success":
                True,

            "character_name":
                data.character_name,

            "panels":
                layout,

            "pdf_path":
                pdf_path
        }

    except Exception as error:

        raise HTTPException(

            status_code=500,

            detail=str(error)
        )


@router.post(
    "/test-image"
)
async def test_image(
    prompt: str = Form(...)
):

    if not prompt.strip():

        raise HTTPException(
            status_code=400,
            detail="Prompt cannot be empty"
        )

    try:

        image_path = (
            await asyncio.to_thread(
                generate_image,
                prompt,
                0
            )
        )

        return {

            "success":
                True,

            "image_path":
                image_path
        }

    except Exception as error:

        raise HTTPException(

            status_code=500,

            detail=str(error)
        )


@router.get(
    "/download/{filename}"
)
async def download_pdf(
    filename: str
):

    filename = Path(
        filename
    ).name

    if not filename.endswith(
        ".pdf"
    ):

        raise HTTPException(
            status_code=400,
            detail="PDF only"
        )

    file_path = (
        BASE_DIR /
        "static" /
        "exports" /
        filename
    )

    if not file_path.exists():

        raise HTTPException(
            status_code=404,
            detail="PDF not found"
        )

    return FileResponse(

        path=str(file_path),

        media_type="application/pdf",

        filename=filename
    )


@router.get(
    "/export-success"
)
async def export_success(
    request: Request,
    filename: str = None
):

    return templates.TemplateResponse(

        request=request,

        name="export_success.html",

        context={

            "title":
                "Export Successful",

            "filename":
                filename
        }
    )


@router.get(
    "/go-export-success/{filename}"
)
async def go_export_success(
    filename: str
):

    filename = Path(
        filename
    ).name

    return RedirectResponse(

        url=(
            "/export-success"
            f"?filename={filename}"
        ),

        status_code=303
    )