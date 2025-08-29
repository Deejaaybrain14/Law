import os
from fastapi import FastAPI, Header, HTTPException, Query
from typing import Optional
from db import get_eventos_por_rol, get_plazos_por_rol
API_KEY = os.getenv("API_KEY", "dev-key")  # ponla en .env para producción

app = FastAPI(title="PJUD Tracker API")

def auth(x_api_key: Optional[str]):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/eventos")
def eventos(rol: str = Query(...), limit: int = 50, x_api_key: Optional[str] = Header(None)):
    auth(x_api_key)
    rows = get_eventos_por_rol(rol)[:limit]
    return rows

@app.get("/plazos")
def plazos(rol: str = Query(...), x_api_key: Optional[str] = Header(None)):
    auth(x_api_key)
    return get_plazos_por_rol(rol)
