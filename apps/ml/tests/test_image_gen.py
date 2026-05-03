import os
import pytest
from PIL import Image
from routes.image_gen import build_instagram_image


def test_build_instagram_image_creates_file(session_dir, property_data, cover_image):
    out = build_instagram_image(
        session_dir=str(session_dir),
        property_data=property_data,
        cover_path=cover_image,
    )
    assert os.path.exists(out)
    assert out.endswith(".png")


def test_instagram_image_dimensions(session_dir, property_data, cover_image):
    out = build_instagram_image(
        session_dir=str(session_dir),
        property_data=property_data,
        cover_path=cover_image,
    )
    with Image.open(out) as img:
        assert img.size == (1080, 1080), f"Tamaño esperado 1080x1080, got {img.size}"
        assert img.mode == "RGB"


def test_instagram_image_without_cover(session_dir, property_data):
    out = build_instagram_image(
        session_dir=str(session_dir),
        property_data=property_data,
        cover_path="",  # no cover
    )
    assert os.path.exists(out)
    with Image.open(out) as img:
        assert img.size == (1080, 1080)


def test_instagram_image_minimal_data(session_dir, cover_image):
    minimal = {
        "tipo": "Departamento",
        "operacion": "Renta",
        "precio": "18,000",
        "ciudad": "",
        "estado": "CDMX",
        "recamaras": "",
        "banos": "",
        "metros_construidos": "",
        "estacionamientos": "",
        "agente_nombre": "",
    }
    out = build_instagram_image(
        session_dir=str(session_dir),
        property_data=minimal,
        cover_path=cover_image,
    )
    assert os.path.exists(out)


def test_instagram_output_path(session_dir, property_data, cover_image):
    from pathlib import Path
    out = build_instagram_image(
        session_dir=str(session_dir),
        property_data=property_data,
        cover_path=cover_image,
    )
    assert Path(out) == session_dir / "instagram.png"
