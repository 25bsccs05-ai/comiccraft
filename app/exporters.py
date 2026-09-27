from datetime import datetime
from pathlib import Path

from fpdf import FPDF


BASE_DIR = Path(
    __file__
).resolve().parent.parent

EXPORT_DIR = (
    BASE_DIR /
    "static" /
    "exports"
)

if not EXPORT_DIR.exists():
    EXPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def clean_text(text):

    replacements = {

        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
        "\u00a0": " "
    }

    for old, new in replacements.items():

        text = text.replace(
            old,
            new
        )

    return (
        text
        .encode(
            "latin-1",
            "replace"
        )
        .decode(
            "latin-1"
        )
    )


def save_pdf(
    layout,
    title="ComicCraft"
):

    filename = (
        "comiccraft_"
        + datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )
        + ".pdf"
    )

    output_path = (
        EXPORT_DIR /
        filename
    )

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4"
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    for panel in layout:

        pdf.add_page()

        pdf.set_font(
            "Helvetica",
            "B",
            18
        )

        pdf.cell(
            0,
            12,
            clean_text(
                f"Panel {panel['panel_number']}: "
                f"{panel['title']}"
            ),
            ln=True
        )

        image_url = panel[
            "image_path"
        ]

        image_name = Path(
            image_url
        ).name

        image_path = (
            BASE_DIR /
            "static" /
            "panels" /
            image_name
        )

        if image_path.exists():

            pdf.image(
                str(image_path),
                x=15,
                y=30,
                w=180
            )

        pdf.ln(105)

        pdf.set_font(
            "Helvetica",
            "I",
            10
        )

        pdf.multi_cell(
            0,
            6,
            clean_text(
                panel[
                    "scene_description"
                ]
            )
        )

        pdf.ln(3)

        pdf.set_font(
            "Helvetica",
            "",
            11
        )

        pdf.multi_cell(
            0,
            6,
            clean_text(
                panel.get(
                    "narration",
                    ""
                )
            )
        )

        dialogue = panel.get(
            "dialogue",
            []
        )

        if dialogue:

            pdf.ln(2)

            pdf.set_font(
                "Helvetica",
                "B",
                11
            )

            pdf.cell(
                0,
                6,
                "Dialogue:",
                ln=True
            )

            pdf.set_font(
                "Helvetica",
                "",
                11
            )

            for line in dialogue:

                pdf.multi_cell(
                    0,
                    6,
                    clean_text(
                        "- " + line
                    )
                )

    pdf.output(
        str(output_path)
    )

    return (
        f"/static/exports/"
        f"{filename}"
    )