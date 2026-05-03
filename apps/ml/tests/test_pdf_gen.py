import os
import pytest
from routes.pdf_gen import build_pdf


def test_build_pdf_creates_file(session_dir, property_data, cover_image, extra_images):
    pdf_path = build_pdf(
        session_dir=str(session_dir),
        property_data=property_data,
        description="Hermosa casa en zona residencial con excelente ubicación.",
        cover_path=cover_image,
        extra_paths=extra_images,
    )
    assert os.path.exists(pdf_path), "El PDF no fue creado"
    assert pdf_path.endswith(".pdf")
    assert os.path.getsize(pdf_path) > 1024, "El PDF parece vacío"


def test_build_pdf_without_extras(session_dir, property_data, cover_image):
    pdf_path = build_pdf(
        session_dir=str(session_dir),
        property_data=property_data,
        description="Descripción de prueba.",
        cover_path=cover_image,
        extra_paths=[],
    )
    assert os.path.exists(pdf_path)


def test_build_pdf_minimal_fields(session_dir, tmp_path):
    minimal = {
        "tipo": "Terreno",
        "operacion": "Venta",
        "direccion": "Calle Sin Nombre",
        "ciudad": "CDMX",
        "estado": "Ciudad de México",
        "precio": "1,000,000",
        "recamaras": "",
        "banos": "",
        "metros_construidos": "",
        "metros_terreno": "500",
        "estacionamientos": "",
        "amenidades": [],
        "descripcion_agente": "Terreno plano.",
        "agente_nombre": "Juan Pérez",
        "agente_telefono": "55 1234 5678",
        "agente_email": "juan@test.mx",
    }
    pdf_path = build_pdf(
        session_dir=str(session_dir),
        property_data=minimal,
        description="",
        cover_path="",  # no cover
        extra_paths=[],
    )
    assert os.path.exists(pdf_path)


def test_build_pdf_output_path(session_dir, property_data, cover_image):
    from pathlib import Path
    pdf_path = build_pdf(
        session_dir=str(session_dir),
        property_data=property_data,
        description="Test.",
        cover_path=cover_image,
        extra_paths=[],
    )
    assert Path(pdf_path) == session_dir / "listado.pdf"
