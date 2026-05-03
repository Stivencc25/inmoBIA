import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from fastapi import APIRouter

router = APIRouter()

BRAND_COLOR = HexColor("#1a3c5e")
ACCENT_COLOR = HexColor("#e8a020")
LIGHT_BG = HexColor("#f8f9fa")


def build_pdf(session_dir: str, property_data: dict, description: str,
              cover_path: str, extra_paths: list) -> str:
    out_path = Path(session_dir) / "listado.pdf"
    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=letter,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    story = []

    # ── Header bar ───────────────────────────────────────────────────────────
    header_data = [[
        Paragraph(
            f'<font color="white" size="18"><b>ListaPro</b></font>',
            ParagraphStyle("hdr", parent=styles["Normal"], alignment=TA_LEFT)
        ),
        Paragraph(
            f'<font color="white" size="10">{property_data["agente_nombre"]}<br/>'
            f'{property_data["agente_telefono"]} | {property_data["agente_email"]}</font>',
            ParagraphStyle("hdr2", parent=styles["Normal"], alignment=TA_RIGHT)
        ),
    ]]
    header_table = Table(header_data, colWidths=["50%", "50%"])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BRAND_COLOR),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (0, -1), 12),
        ("RIGHTPADDING", (-1, 0), (-1, -1), 12),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.3 * cm))

    # ── Cover photo ──────────────────────────────────────────────────────────
    if cover_path and os.path.exists(cover_path):
        page_width = letter[0] - 3.6 * cm
        img = Image(cover_path, width=page_width, height=5.5 * inch)
        img.hAlign = "CENTER"
        story.append(img)

    story.append(Spacer(1, 0.4 * cm))

    # ── Title and price ───────────────────────────────────────────────────────
    operacion_label = "EN VENTA" if "venta" in property_data["operacion"].lower() else "EN RENTA"
    badge_style = ParagraphStyle(
        "badge",
        parent=styles["Normal"],
        textColor=white,
        backColor=ACCENT_COLOR,
        borderPadding=(4, 8, 4, 8),
        fontSize=10,
        fontName="Helvetica-Bold",
    )
    story.append(Paragraph(f" {operacion_label} ", badge_style))
    story.append(Spacer(1, 0.2 * cm))

    title_style = ParagraphStyle(
        "title", parent=styles["Normal"],
        fontSize=20, fontName="Helvetica-Bold", textColor=BRAND_COLOR,
        spaceAfter=4,
    )
    story.append(Paragraph(
        f'{property_data["tipo"]} — {property_data["ciudad"]}, {property_data["estado"]}',
        title_style
    ))

    price_style = ParagraphStyle(
        "price", parent=styles["Normal"],
        fontSize=24, fontName="Helvetica-Bold", textColor=ACCENT_COLOR,
        spaceAfter=4,
    )
    story.append(Paragraph(f'${property_data["precio"]} MXN', price_style))

    addr_style = ParagraphStyle(
        "addr", parent=styles["Normal"],
        fontSize=10, textColor=HexColor("#555555"),
    )
    story.append(Paragraph(property_data["direccion"], addr_style))
    story.append(Spacer(1, 0.4 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=HexColor("#dddddd")))
    story.append(Spacer(1, 0.4 * cm))

    # ── Key specs ─────────────────────────────────────────────────────────────
    specs = []
    def spec(label, value, unit=""):
        if value:
            specs.append((label, f"{value}{unit}"))

    spec("Recámaras", property_data["recamaras"])
    spec("Baños", property_data["banos"])
    spec("M² Construidos", property_data["metros_construidos"], " m²")
    spec("M² Terreno", property_data["metros_terreno"], " m²")
    spec("Estacionamientos", property_data["estacionamientos"])

    if specs:
        spec_label_style = ParagraphStyle(
            "sl", parent=styles["Normal"],
            fontSize=8, textColor=HexColor("#888888"), fontName="Helvetica",
        )
        spec_value_style = ParagraphStyle(
            "sv", parent=styles["Normal"],
            fontSize=14, fontName="Helvetica-Bold", textColor=BRAND_COLOR,
        )
        cols = []
        for label, value in specs:
            cols.append([
                Paragraph(label, spec_label_style),
                Paragraph(value, spec_value_style),
            ])

        # Group in rows of 3
        rows = [cols[i:i+3] for i in range(0, len(cols), 3)]
        for row in rows:
            while len(row) < 3:
                row.append(["", ""])
            t_data = [[c[0] for c in row], [c[1] for c in row]]
            t = Table(t_data, colWidths=["33%", "33%", "33%"])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
                ("BOX", (0, 0), (-1, -1), 0.5, HexColor("#dddddd")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, HexColor("#dddddd")),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ]))
            story.append(t)
            story.append(Spacer(1, 0.15 * cm))

        story.append(Spacer(1, 0.3 * cm))

    # ── Description ───────────────────────────────────────────────────────────
    section_title = ParagraphStyle(
        "st", parent=styles["Normal"],
        fontSize=12, fontName="Helvetica-Bold", textColor=BRAND_COLOR,
        spaceAfter=6, borderPadding=(0, 0, 4, 0),
    )
    body_style = ParagraphStyle(
        "body", parent=styles["Normal"],
        fontSize=10, leading=15, textColor=HexColor("#333333"),
    )
    story.append(Paragraph("Descripción", section_title))
    story.append(Paragraph(description or property_data.get("descripcion_agente", ""), body_style))
    story.append(Spacer(1, 0.4 * cm))

    # ── Amenidades ────────────────────────────────────────────────────────────
    if property_data.get("amenidades"):
        story.append(Paragraph("Amenidades", section_title))
        amenidades_str = "  •  ".join(property_data["amenidades"])
        story.append(Paragraph(f"• {amenidades_str}", body_style))
        story.append(Spacer(1, 0.4 * cm))

    # ── Extra photos ──────────────────────────────────────────────────────────
    valid_extras = [p for p in extra_paths if p and os.path.exists(p)]
    if valid_extras:
        story.append(Paragraph("Galería de Fotos", section_title))
        page_width = letter[0] - 3.6 * cm
        photo_width = (page_width - 0.4 * cm) / 3
        photo_height = photo_width * 0.75

        rows_data = []
        row = []
        for i, ep in enumerate(valid_extras[:9]):
            row.append(Image(ep, width=photo_width, height=photo_height))
            if len(row) == 3:
                rows_data.append(row)
                row = []
        if row:
            while len(row) < 3:
                row.append("")
            rows_data.append(row)

        gallery_table = Table(rows_data, colWidths=[photo_width] * 3,
                              rowHeights=[photo_height] * len(rows_data))
        gallery_table.setStyle(TableStyle([
            ("INNERGRID", (0, 0), (-1, -1), 2, white),
            ("BOX", (0, 0), (-1, -1), 0, white),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("LEFTPADDING", (0, 0), (-1, -1), 2),
            ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ]))
        story.append(gallery_table)
        story.append(Spacer(1, 0.4 * cm))

    # ── Agent footer ──────────────────────────────────────────────────────────
    footer_data = [[
        Paragraph(
            f'<font color="white" size="11"><b>{property_data["agente_nombre"]}</b><br/>'
            f'Tel: {property_data["agente_telefono"]}<br/>'
            f'Email: {property_data["agente_email"]}</font>',
            ParagraphStyle("footer", parent=styles["Normal"], alignment=TA_LEFT)
        )
    ]]
    footer_table = Table(footer_data, colWidths=["100%"])
    footer_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BRAND_COLOR),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(footer_table)

    doc.build(story)
    return str(out_path)
