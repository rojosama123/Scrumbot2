from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chatbot_pdf2 import enviar_a_llama

# Importa StaticFiles y Path para servir frontend estático
from fastapi.staticfiles import StaticFiles
from pathlib import Path

class Pregunta(BaseModel):
    mensaje: str

app = FastAPI()

# Permitir el acceso desde React (ajusta el origen si usas otro puerto)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Cambia al puerto que uses si es necesario
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(pregunta: Pregunta):
    respuesta = enviar_a_llama(pregunta.mensaje)
    return {"respuesta": respuesta}

# --------------------------------------------
# Montar la carpeta build del frontend React para servir la web
frontend_path = Path(__file__).parent / "scrum-chatbot-frontend" / "build"
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
# --------------------------------------------
