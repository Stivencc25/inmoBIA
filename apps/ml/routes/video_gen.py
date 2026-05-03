import os
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import imageio

router = APIRouter()

VIDEO_W, VIDEO_H = 1280, 720
FPS = 24
SEC_PER_PHOTO = 4
FADE_FRAMES = 18
BRAND_BLUE = (26, 60, 94)
ACCENT_ORANGE = (232, 160, 32)
WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
DARK_GRAY = (150, 150, 150)


class VideoRequest(BaseModel):
    session_id: str


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        (r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf"),
        (r"C:\Windows\Fonts\Arial Bold.ttf" if bold else r"C:\Windows\Fonts\Arial.ttf"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
         else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold
         else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def _fit_crop(img: Image.Image, w: int, h: int) -> Image.Image:
    ir = img.width / img.height
    cr = w / h
    if ir > cr:
        nh, nw = h, int(ir * h)
    else:
        nw, nh = w, int(w / ir)
    img = img.resize((nw, nh), Image.LANCZOS)
    x = (nw - w) // 2
    y = (nh - h) // 2
    return img.crop((x, y, x + w, y + h))


def _gradient_bottom(img: Image.Image, strength: float = 0.82) -> Image.Image:
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    start = int(img.height * 0.45)
    for y in range(start, img.height):
        alpha = int(255 * strength * ((y - start) / (img.height - start)))
        draw.line([(0, y), (img.width, y)], fill=(0, 0, 0, alpha))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def _fade(frames: list[np.ndarray]) -> list[np.ndarray]:
    black = np.zeros((VIDEO_H, VIDEO_W, 3), dtype=np.uint8)
    n = len(frames)
    result = []
    for i, f in enumerate(frames):
        if i < FADE_FRAMES:
            a = i / FADE_FRAMES
            result.append((a * f + (1 - a) * black).astype(np.uint8))
        elif i > n - FADE_FRAMES - 1:
            a = (n - i) / FADE_FRAMES
            result.append((a * f + (1 - a) * black).astype(np.uint8))
        else:
            result.append(f)
    return result


def _intro_frames(data: dict) -> list[np.ndarray]:
    card = Image.new("RGB", (VIDEO_W, VIDEO_H), BRAND_BLUE)
    draw = ImageDraw.Draw(card)

    cx = VIDEO_W // 2

    draw.text((cx, 110), "ListaPro", font=_font(68, bold=True),
              fill=ACCENT_ORANGE, anchor="mm")

    tipo_op = f'{data.get("tipo", "")} en {data.get("operacion", "")}'.upper()
    draw.text((cx, 215), tipo_op, font=_font(38, bold=True),
              fill=WHITE, anchor="mm")

    precio = data.get("precio", "")
    if precio:
        draw.text((cx, 315), f"${precio} MXN", font=_font(62, bold=True),
                  fill=ACCENT_ORANGE, anchor="mm")

    ciudad, estado = data.get("ciudad", ""), data.get("estado", "")
    location = f"{ciudad}, {estado}" if ciudad else estado
    draw.text((cx, 405), location, font=_font(34), fill=GRAY, anchor="mm")

    specs = []
    if data.get("recamaras"):        specs.append(f"{data['recamaras']} Rec.")
    if data.get("banos"):            specs.append(f"{data['banos']} Baños")
    if data.get("metros_construidos"): specs.append(f"{data['metros_construidos']} m²")
    if data.get("estacionamientos"): specs.append(f"{data['estacionamientos']} Est.")
    if specs:
        draw.text((cx, 470), "  |  ".join(specs), font=_font(28), fill=GRAY, anchor="mm")

    agent = data.get("agente_nombre", "")
    if agent:
        draw.text((cx, VIDEO_H - 55), agent, font=_font(26), fill=DARK_GRAY, anchor="mm")

    arr = np.array(card)
    return _fade([arr] * (FPS * 3))


def _photo_frames(path: str) -> list[np.ndarray]:
    total = FPS * SEC_PER_PHOTO
    src = _fit_crop(Image.open(path).convert("RGB"),
                    int(VIDEO_W * 1.07), int(VIDEO_H * 1.07))
    frames = []
    for i in range(total):
        t = i / total
        zoom = 1.0 + 0.07 * t
        zw = int(src.width / zoom)
        zh = int(src.height / zoom)
        x0 = int((src.width - zw) * t * 0.35)
        y0 = (src.height - zh) // 2
        frame = src.crop((x0, y0, x0 + zw, y0 + zh)).resize(
            (VIDEO_W, VIDEO_H), Image.BILINEAR)
        frames.append(np.array(frame))
    return frames


def _outro_frames(data: dict) -> list[np.ndarray]:
    card = Image.new("RGB", (VIDEO_W, VIDEO_H), BRAND_BLUE)
    draw = ImageDraw.Draw(card)
    cx = VIDEO_W // 2

    draw.text((cx, 160), "ListaPro", font=_font(52, bold=True),
              fill=ACCENT_ORANGE, anchor="mm")

    agent = data.get("agente_nombre", "")
    if agent:
        draw.text((cx, 280), agent, font=_font(44, bold=True),
                  fill=WHITE, anchor="mm")

    y = 360
    for key in ("agente_telefono", "agente_email"):
        val = data.get(key, "")
        if val:
            draw.text((cx, y), val, font=_font(30), fill=GRAY, anchor="mm")
            y += 52

    arr = np.array(card)
    return _fade([arr] * (FPS * 3))


def _build_video(photos: list[str], data: dict, out_path: str) -> None:
    all_frames: list[np.ndarray] = []
    all_frames.extend(_intro_frames(data))
    for p in photos[:8]:
        all_frames.extend(_photo_frames(p))
    all_frames.extend(_outro_frames(data))

    with imageio.get_writer(
        out_path, fps=FPS, codec="libx264",
        output_params=["-pix_fmt", "yuv420p", "-crf", "23"],
    ) as writer:
        for frame in all_frames:
            writer.append_data(frame)


@router.post("/video")
async def generate_video(req: VideoRequest):
    session_dir = Path("generated") / req.session_id
    data_file = session_dir / "data.json"

    if not data_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Sesión no encontrada. Genera el listado primero.",
        )

    data = json.loads(data_file.read_text(encoding="utf-8"))

    photos: list[str] = []
    cover = data.get("cover_path", "")
    if cover and os.path.exists(cover):
        photos.append(cover)
    for p in data.get("extra_paths", []):
        if p and os.path.exists(p):
            photos.append(p)

    if not photos:
        raise HTTPException(status_code=400, detail="No hay fotos disponibles para el video.")

    out_path = str(session_dir / "video.mp4")
    try:
        await run_in_threadpool(_build_video, photos, data, out_path)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error generando video: {exc}")

    return {"video_url": f"/generated/{req.session_id}/video.mp4"}
