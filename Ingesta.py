import os, sys
sys.path.append(os.path.dirname(__file__))

from hashlib import sha256
from datetime import datetime
from db import upsert_case_event

rol = "C-1234-2025"
titulo = "Se tiene por presentado"

raw = f"{rol}|2025-08-29 12:00|resolución|{titulo}"
raw_hash = sha256(raw.encode()).hexdigest()

ok = upsert_case_event({
    "rol": rol,
    "tribunal": "Santiago",
    "tipo": "resolución",
    "titulo": titulo,
    "detalle": "Detalle opcional",
    "fecha": datetime.now().isoformat(),
    "fuente": "portal",
    "raw_hash": raw_hash
})
print("Insertado:", ok)
