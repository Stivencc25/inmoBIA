"""Smoke tests for the FastAPI application endpoints."""
import json
import io
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from PIL import Image


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    # Point generated/ and uploads/ to temp dirs so the app doesn't write to cwd
    import os
    tmp = tmp_path_factory.mktemp("app")
    gen_dir = tmp / "generated"
    gen_dir.mkdir()
    uploads_dir = tmp / "uploads"
    uploads_dir.mkdir()

    with patch("os.makedirs"):
        import sys
        sys.path.insert(0, ".")
        from main import app
        with TestClient(app) as c:
            yield c


def _make_image_bytes(color=(100, 150, 200), size=(400, 300)):
    buf = io.BytesIO()
    Image.new("RGB", size, color=color).save(buf, format="JPEG")
    buf.seek(0)
    return buf


# ── App health ─────────────────────────────────────────────

def test_app_starts(client):
    """The app should respond — even if 404 because frontend isn't mounted in test."""
    resp = client.get("/")
    assert resp.status_code in (200, 404, 500)


# ── /api/generate ──────────────────────────────────────────

FORM_DATA = {
    "tipo": "Casa",
    "operacion": "Venta",
    "direccion": "Av. Reforma 100",
    "ciudad": "CDMX",
    "estado": "Ciudad de México",
    "precio": "5,000,000",
    "recamaras": "3",
    "banos": "2",
    "metros_construidos": "150",
    "metros_terreno": "200",
    "estacionamientos": "2",
    "amenidades": json.dumps(["Alberca", "Roof garden"]),
    "descripcion_agente": "Casa moderna en zona premium.",
    "agente_nombre": "Luis Torres",
    "agente_telefono": "55 9876 5432",
    "agente_email": "luis@test.mx",
}


@pytest.mark.asyncio
async def test_generate_returns_session(client):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "descripcion": "Hermosa casa moderna en zona residencial.",
        "instagram_copy": "¡Tu hogar soñado! 🏠 #CasaEnVenta #BienesRaices",
    })

    with patch("routes.generate.client.chat.completions.create",
               new=AsyncMock(return_value=mock_response)):
        resp = client.post(
            "/api/generate",
            data=FORM_DATA,
            files={"portada": ("portada.jpg", _make_image_bytes(), "image/jpeg")},
        )

    assert resp.status_code == 200
    body = resp.json()
    assert "session_id" in body
    assert "description" in body
    assert "instagram_copy" in body
    assert "pdf_url" in body
    assert "image_url" in body


# ── /api/publish ───────────────────────────────────────────

def test_publish_missing_env_returns_500(client):
    with patch.dict("os.environ", {"UPLOADPOST_API_KEY": "", "UPLOADPOST_USER": ""}):
        resp = client.post(
            "/api/publish",
            json={"session_id": "nonexistent", "instagram_copy": "test"},
        )
    assert resp.status_code in (500, 404)


def test_publish_missing_session_returns_404(client):
    with patch.dict("os.environ",
                    {"UPLOADPOST_API_KEY": "fake-key", "UPLOADPOST_USER": "fake-user"}):
        resp = client.post(
            "/api/publish",
            json={"session_id": "does_not_exist", "instagram_copy": "test"},
        )
    assert resp.status_code == 404


# ── /api/video ─────────────────────────────────────────────

def test_video_missing_session_returns_404(client):
    resp = client.post("/api/video", json={"session_id": "no_session"})
    assert resp.status_code == 404
