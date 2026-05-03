import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()


class PublishRequest(BaseModel):
    session_id: str
    instagram_copy: str


@router.post("/publish")
async def publish_to_instagram(req: PublishRequest):
    api_key = os.getenv("UPLOADPOST_API_KEY", "")
    user_id = os.getenv("UPLOADPOST_USER", "")

    if not api_key or not user_id:
        raise HTTPException(
            status_code=500,
            detail="UPLOADPOST_API_KEY y UPLOADPOST_USER no configurados en .env"
        )

    image_path = Path("generated") / req.session_id / "instagram.png"
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Imagen no encontrada. Genera el listado primero.")

    async with httpx.AsyncClient(timeout=60) as client:
        with open(image_path, "rb") as f:
            response = await client.post(
                "https://api.upload-post.com/api/upload",
                headers={"Authorization": f"Apikey {api_key}"},
                data={
                    "user": user_id,
                    "platform[]": "instagram",
                    "title": req.instagram_copy,
                },
                files={"imagen": (image_path.name, f, "image/png")},
            )

    if response.status_code == 200:
        return {"success": True, "message": "¡Publicado en Instagram exitosamente!", "data": response.json()}
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Error de upload-post: {response.text}"
        )
