import os
import uuid
import json
import shutil
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from openai import AsyncOpenAI
from dotenv import load_dotenv

from .pdf_gen import build_pdf
from .image_gen import build_instagram_image

load_dotenv()

router = APIRouter()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@router.post("/generate")
async def generate(
    tipo: str = Form(...),
    operacion: str = Form(...),
    direccion: str = Form(...),
    ciudad: str = Form(...),
    estado: str = Form(...),
    precio: str = Form(...),
    recamaras: str = Form(""),
    banos: str = Form(""),
    metros_construidos: str = Form(""),
    metros_terreno: str = Form(""),
    estacionamientos: str = Form(""),
    amenidades: str = Form(""),          # JSON array string
    descripcion_agente: str = Form(...),
    agente_nombre: str = Form(...),
    agente_telefono: str = Form(...),
    agente_email: str = Form(...),
    portada: UploadFile = File(...),
    extras: List[UploadFile] = File(default=[]),
):
    session_id = str(uuid.uuid4())[:8]
    session_dir = Path("generated") / session_id
    photos_dir = session_dir / "photos"
    photos_dir.mkdir(parents=True, exist_ok=True)

    # Save cover photo
    cover_path = photos_dir / f"portada{Path(portada.filename).suffix}"
    with open(cover_path, "wb") as f:
        shutil.copyfileobj(portada.file, f)

    # Save extra photos
    extra_paths = []
    for i, extra in enumerate(extras):
        if extra.filename:
            ext = Path(extra.filename).suffix
            p = photos_dir / f"extra_{i}{ext}"
            with open(p, "wb") as f:
                shutil.copyfileobj(extra.file, f)
            extra_paths.append(str(p))

    amenidades_list = json.loads(amenidades) if amenidades else []

    property_data = {
        "tipo": tipo,
        "operacion": operacion,
        "direccion": direccion,
        "ciudad": ciudad,
        "estado": estado,
        "precio": precio,
        "recamaras": recamaras,
        "banos": banos,
        "metros_construidos": metros_construidos,
        "metros_terreno": metros_terreno,
        "estacionamientos": estacionamientos,
        "amenidades": amenidades_list,
        "descripcion_agente": descripcion_agente,
        "agente_nombre": agente_nombre,
        "agente_telefono": agente_telefono,
        "agente_email": agente_email,
    }

    # Generate text with OpenAI
    description, instagram_copy = await _generate_text(property_data)

    # Generate PDF
    pdf_path = build_pdf(
        session_dir=str(session_dir),
        property_data=property_data,
        description=description,
        cover_path=str(cover_path),
        extra_paths=extra_paths,
    )

    # Generate Instagram image
    image_path = build_instagram_image(
        session_dir=str(session_dir),
        property_data=property_data,
        cover_path=str(cover_path),
    )

    # Save session data for video generation
    session_json = session_dir / "data.json"
    session_json.write_text(
        json.dumps({
            **property_data,
            "description": description,
            "instagram_copy": instagram_copy,
            "cover_path": str(cover_path),
            "extra_paths": extra_paths,
        }, ensure_ascii=False),
        encoding="utf-8",
    )

    return JSONResponse({
        "session_id": session_id,
        "description": description,
        "instagram_copy": instagram_copy,
        "pdf_url": f"/generated/{session_id}/listado.pdf",
        "image_url": f"/generated/{session_id}/instagram.png",
    })


async def _generate_text(data: dict) -> tuple[str, str]:
    amenidades_str = ", ".join(data["amenidades"]) if data["amenidades"] else "ninguna especificada"
    specs = []
    if data["recamaras"]:
        specs.append(f"{data['recamaras']} recámaras")
    if data["banos"]:
        specs.append(f"{data['banos']} baños")
    if data["metros_construidos"]:
        specs.append(f"{data['metros_construidos']} m² construidos")
    if data["metros_terreno"]:
        specs.append(f"{data['metros_terreno']} m² de terreno")
    if data["estacionamientos"]:
        specs.append(f"{data['estacionamientos']} estacionamientos")

    prompt = f"""Eres un experto en marketing inmobiliario en México con 15 años de experiencia.
Genera DOS piezas de contenido para esta propiedad en JSON con las claves "descripcion" e "instagram_copy".

DATOS DE LA PROPIEDAD:
- Tipo: {data['tipo']} en {data['operacion']}
- Ubicación: {data['direccion']}, {data['ciudad']}, {data['estado']}
- Precio: ${data['precio']} MXN
- Características: {', '.join(specs) if specs else 'no especificadas'}
- Amenidades: {amenidades_str}
- Notas del agente: {data['descripcion_agente']}

INSTRUCCIONES:
1. "descripcion": Descripción profesional y atractiva de 150-200 palabras. Tono cálido pero profesional. Destaca los puntos únicos. En español mexicano.
2. "instagram_copy": Copy para Instagram de máximo 220 caracteres + 15 hashtags relevantes del sector inmobiliario en México (#BienesRaices, #CasaEnVenta, etc.) separados por espacios. En español.

Responde SOLO con el JSON, sin markdown, sin explicaciones."""

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.8,
    )

    result = json.loads(response.choices[0].message.content)
    return result.get("descripcion", ""), result.get("instagram_copy", "")
