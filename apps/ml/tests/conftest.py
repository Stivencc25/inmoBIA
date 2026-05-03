import os
import pytest
from pathlib import Path
from PIL import Image

# Must be set before routes are imported so AsyncOpenAI doesn't raise at import time.
os.environ.setdefault("OPENAI_API_KEY", "sk-test-00000000000000000000000000000000")


SAMPLE_PROPERTY = {
    "tipo": "Casa",
    "operacion": "Venta",
    "direccion": "Av. Chapultepec 100, Col. Americana",
    "ciudad": "Guadalajara",
    "estado": "Jalisco",
    "precio": "3,500,000",
    "recamaras": "3",
    "banos": "2.5",
    "metros_construidos": "180",
    "metros_terreno": "250",
    "estacionamientos": "2",
    "amenidades": ["Alberca", "Jardín", "Seguridad 24h"],
    "descripcion_agente": "Casa remodelada con vista al parque, cocina integral nueva.",
    "agente_nombre": "Ana García",
    "agente_telefono": "+52 33 1234 5678",
    "agente_email": "ana@inmobia.mx",
}


@pytest.fixture
def property_data():
    return dict(SAMPLE_PROPERTY)


@pytest.fixture
def session_dir(tmp_path):
    """Temporary session directory that mimics backend/generated/<id>/."""
    d = tmp_path / "abc12345"
    photos = d / "photos"
    photos.mkdir(parents=True)
    return d


@pytest.fixture
def cover_image(session_dir):
    """A small solid-color JPEG to use as cover photo in tests."""
    img = Image.new("RGB", (800, 600), color=(60, 120, 200))
    path = session_dir / "photos" / "portada.jpg"
    img.save(str(path), "JPEG")
    return str(path)


@pytest.fixture
def extra_images(session_dir):
    """Two small extra images."""
    paths = []
    colors = [(200, 80, 80), (80, 200, 80)]
    for i, color in enumerate(colors):
        img = Image.new("RGB", (640, 480), color=color)
        p = session_dir / "photos" / f"extra_{i}.jpg"
        img.save(str(p), "JPEG")
        paths.append(str(p))
    return paths
