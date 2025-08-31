# api.py
import os
from typing import Optional
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from db import get_eventos_por_rol, get_plazos_por_rol, exists_rol

API_KEY = os.getenv("API_KEY", "dev-key")  # usa .env en prod

app = FastAPI(title="PJUD Tracker API")

# CORS (para tu frontend local en Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def auth(x_api_key: Optional[str]):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/eventos")
def eventos(
    rol: str,
    limit: int = Query(50, ge=1, le=200),
    order: str = Query("desc", regex="^(asc|desc)$"),
    x_api_key: Optional[str] = Header(None),
):
    auth(x_api_key)
    if not exists_rol(rol):
        raise HTTPException(404, f"ROL {rol} no encontrado")
    return get_eventos_por_rol(rol, limit=limit, order=order)

@app.get("/plazos")
def plazos(
    rol: str,
    x_api_key: Optional[str] = Header(None),
):
    auth(x_api_key)
    if not exists_rol(rol):
        raise HTTPException(404, f"ROL {rol} no encontrado")
    return get_plazos_por_rol(rol)
