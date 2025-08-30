# ingesta_email.py — cron-ready (silencioso)
import os, re, hashlib, logging
from datetime import datetime
from pathlib import Path
from imapclient import IMAPClient
import mailparser
from dotenv import load_dotenv
from db import upsert_case_event

# === Cargar .env desde la carpeta del script ===
SCRIPT_DIR = Path(__file__).resolve().parent
load_dotenv(SCRIPT_DIR / ".env")

IMAP_HOST   = os.getenv("IMAP_HOST")
IMAP_USER   = os.getenv("IMAP_USER")
IMAP_PASS   = os.getenv("IMAP_PASS")
IMAP_FOLDER = os.getenv("IMAP_FOLDER", "INBOX")
LIMIT       = int(os.getenv("INGEST_LIMIT", "100"))  # tope de mensajes a procesar por corrida
LOG_FILE    = os.getenv("INGEST_LOG_FILE", "")       # ej: /tmp/ingesta_email.log

# === Logging (silencioso si no defines LOG_FILE) ===
if LOG_FILE:
    logging.basicConfig(filename=LOG_FILE,
                        level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("ingesta_email")

if not IMAP_HOST or not IMAP_USER or not IMAP_PASS:
    msg = "Faltan IMAP_HOST / IMAP_USER / IMAP_PASS (revisa .env)"
    (log.error(msg) if LOG_FILE else None)
    raise SystemExit(msg)

# Detecta Rol/RIT/RUC en asunto/cuerpo
ROL_RX = re.compile(r'(RIT|Rol|RUC)\s*[:#]?\s*([A-Z\-]*\d{1,6}-\d{4})', re.I)

def pull_and_ingest(limit: int = LIMIT) -> dict:
    inserted = skipped = 0

    with IMAPClient(IMAP_HOST, ssl=True, port=993, timeout=30) as server:
        server.login(IMAP_USER, IMAP_PASS)
        server.select_folder(IMAP_FOLDER)

        # Ajusta el filtro a tu casuística:
        # - por remitente pjud.cl o asunto con "Notific" (puedes cambiar a ["ALL"] o a una etiqueta)
        uids = server.search(['OR', 'FROM', 'pjud.cl', 'SUBJECT', 'Notific'])
        if not uids:
            return {"inserted": 0, "skipped": 0}

        uids = uids[-limit:]  # últimos N
        fetched = server.fetch(uids, ['RFC822'])

        for uid, data in fetched.items():
            try:
                mp = mailparser.parse_from_bytes(data[b'RFC822'])
                asunto = (mp.subject or "").strip()
                cuerpo = (mp.body or "").strip()
                fecha  = mp.date or datetime.utcnow()

                m = ROL_RX.search(asunto + " " + cuerpo)
                rol = m.group(2) if m else None

                # Dedupe: raw_hash estable por asunto+fecha
                raw = f"email|{asunto}|{fecha.isoformat()}"
                raw_hash = hashlib.sha256(raw.encode()).hexdigest()

                ok = upsert_case_event({
                    "rol": rol,
                    "tribunal": None,
                    "tipo": "notificación",
                    "titulo": asunto or "Notificación PJUD",
                    "detalle": (cuerpo[:2000] if cuerpo else None),
                    "fecha": fecha.isoformat(),
                    "fuente": "ojv_email",
                    "raw_hash": raw_hash
                })
                if ok:
                    inserted += 1
                else:
                    skipped += 1

            except Exception as e:
                (log.exception(f"Error procesando UID {uid}: {e}") if LOG_FILE else None)
                # seguimos con el siguiente

    return {"inserted": inserted, "skipped": skipped}

if __name__ == "__main__":
    res = pull_and_ingest()
    if os.getenv("INGEST_LOG_FILE"):
        log.info("Ingesta finalizada: %s", res)
    if os.getenv("PRINT_SUMMARY"):
        print(res)
