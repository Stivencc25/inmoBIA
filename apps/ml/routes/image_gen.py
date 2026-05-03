import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from fastapi import APIRouter

router = APIRouter()

CANVAS = (1080, 1080)
BRAND_BLUE = (26, 60, 94)
ACCENT_ORANGE = (232, 160, 32)
WHITE = (255, 255, 255)


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    font_paths = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\Arial Bold.ttf" if bold else r"C:\Windows\Fonts\Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def build_instagram_image(session_dir: str, property_data: dict, cover_path: str) -> str:
    out_path = Path(session_dir) / "instagram.png"

    # ── Background ────────────────────────────────────────────────────────────
    canvas = Image.new("RGB", CANVAS, color=(20, 20, 20))

    if cover_path and os.path.exists(cover_path):
        bg = Image.open(cover_path).convert("RGB")
        # Scale to fill (crop center)
        bg_ratio = bg.width / bg.height
        canvas_ratio = CANVAS[0] / CANVAS[1]
        if bg_ratio > canvas_ratio:
            new_h = CANVAS[1]
            new_w = int(bg_ratio * new_h)
        else:
            new_w = CANVAS[0]
            new_h = int(new_w / bg_ratio)
        bg = bg.resize((new_w, new_h), Image.LANCZOS)
        x = (new_w - CANVAS[0]) // 2
        y = (new_h - CANVAS[1]) // 2
        bg = bg.crop((x, y, x + CANVAS[0], y + CANVAS[1]))
        canvas.paste(bg)

    draw = ImageDraw.Draw(canvas)

    # ── Gradient overlay (bottom 65%) ─────────────────────────────────────────
    gradient = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    grad_draw = ImageDraw.Draw(gradient)
    gradient_start = int(CANVAS[1] * 0.30)
    for y in range(gradient_start, CANVAS[1]):
        alpha = int(210 * ((y - gradient_start) / (CANVAS[1] - gradient_start)))
        grad_draw.line([(0, y), (CANVAS[0], y)], fill=(0, 0, 0, alpha))

    canvas = canvas.convert("RGBA")
    canvas = Image.alpha_composite(canvas, gradient).convert("RGB")
    draw = ImageDraw.Draw(canvas)

    # ── TOP: badge ────────────────────────────────────────────────────────────
    operacion = property_data.get("operacion", "Venta").upper()
    badge_label = f"  EN {operacion}  "
    font_badge = _load_font(32, bold=True)
    bbox = draw.textbbox((0, 0), badge_label, font=font_badge)
    bw = bbox[2] - bbox[0] + 16
    bh = bbox[3] - bbox[1] + 16
    badge_x, badge_y = 50, 50
    draw.rounded_rectangle(
        [badge_x, badge_y, badge_x + bw, badge_y + bh],
        radius=10,
        fill=ACCENT_ORANGE,
    )
    draw.text(
        (badge_x + 8, badge_y + 8),
        badge_label,
        font=font_badge,
        fill=WHITE,
    )

    # ── BOTTOM section ────────────────────────────────────────────────────────
    bottom_y = 650

    # Price
    precio = property_data.get("precio", "")
    font_price = _load_font(72, bold=True)
    draw.text((55, bottom_y), f"${precio}", font=font_price, fill=WHITE)

    # Location
    ciudad = property_data.get("ciudad", "")
    estado = property_data.get("estado", "")
    location = f"{ciudad}, {estado}" if ciudad else estado
    font_location = _load_font(38)
    draw.text((58, bottom_y + 90), location, font=font_location,
              fill=(210, 210, 210))

    # Divider
    draw.line([(55, bottom_y + 155), (CANVAS[0] - 55, bottom_y + 155)],
              fill=(255, 255, 255, 80), width=1)

    # ── Icons row ─────────────────────────────────────────────────────────────
    icon_y = bottom_y + 175
    font_icon_val = _load_font(44, bold=True)
    font_icon_label = _load_font(26)

    stats = []
    if property_data.get("recamaras"):
        stats.append(("🛏", property_data["recamaras"], "Rec"))
    if property_data.get("banos"):
        stats.append(("🚿", property_data["banos"], "Baños"))
    if property_data.get("metros_construidos"):
        stats.append(("📐", property_data["metros_construidos"], "m²"))
    if property_data.get("estacionamientos"):
        stats.append(("🚗", property_data["estacionamientos"], "Est"))

    spacing = 220
    for i, (icon, val, label) in enumerate(stats[:4]):
        x = 55 + i * spacing
        # Value
        draw.text((x, icon_y), f"{val}", font=font_icon_val, fill=WHITE)
        # Label
        draw.text((x, icon_y + 52), label, font=font_icon_label,
                  fill=(180, 180, 180))

    # ── Agent name bottom right ───────────────────────────────────────────────
    font_agent = _load_font(28)
    agent_name = property_data.get("agente_nombre", "")
    if agent_name:
        bbox = draw.textbbox((0, 0), agent_name, font=font_agent)
        aw = bbox[2] - bbox[0]
        draw.text((CANVAS[0] - aw - 50, CANVAS[1] - 60),
                  agent_name, font=font_agent, fill=(200, 200, 200))

    canvas.save(str(out_path), "PNG", quality=95)
    return str(out_path)
