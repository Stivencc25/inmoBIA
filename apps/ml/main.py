from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="ListaPro API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("generated", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
app.mount("/generated", StaticFiles(directory="generated"), name="generated")

from routes.generate import router as generate_router
from routes.instagram import router as instagram_router
from routes.video_gen import router as video_router

app.include_router(generate_router, prefix="/api")
app.include_router(instagram_router, prefix="/api")
app.include_router(video_router, prefix="/api")


@app.get("/")
def index():
    return FileResponse("frontend/index.html")
