from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routes import router

BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

if not (STATIC_DIR / "panels").exists():
    (STATIC_DIR / "panels").mkdir(parents=True, exist_ok=True)
if not (STATIC_DIR / "exports").exists():
    (STATIC_DIR / "exports").mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="ComicCraft",
    description="AI Comic Story Creator using Gemini and Stable Diffusion",
    version="1.0.0"
)

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static"
)

templates = Jinja2Templates(
    directory=str(TEMPLATES_DIR)
)

app.include_router(router)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "message": "ComicCraft is running"
    }