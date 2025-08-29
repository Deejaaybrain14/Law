title: "MVP: Seguidor de Causas - Poder Judicial de Chile"
author: "Bea / Equipo"


# Objetivo

Este documento describe y encapsula un **MVP** para un software que hace **seguimiento de causas del Poder Judicial de Chile**, con conectores a la **consulta pública** (sin login) y opción de ingesta de **notificaciones por correo** (IMAP). Incluye arquitectura, esquema de datos, y todo el código base para levantar el sistema con Docker.

> **Nota legal**: usa este software solo para las causas del estudio/cliente autorizadas y respetando condiciones de uso y tratamiento de datos personales. Evita automatizar flujos de autenticación estatal (p. ej. ClaveÚnica).

# Arquitectura

- **Frontend**: (fuera de alcance del MVP – se puede agregar luego).
- **API**: FastAPI (Python).
- **Workers**: Celery + Redis para tareas recurrentes de ingesta.
- **DB**: PostgreSQL.
- **Conectores**:
  - **Portal público PJUD** via Playwright (headless Chromium).
  - **IMAP** para parsear notificaciones (asuntos/cuerpo) y asociarlas a causas.
- **Utilidades**: cálculo de **plazos hábiles** con feriados de Chile (API pública gov).
- **Despliegue**: `docker-compose` + `Dockerfile` (instala Playwright y dependencias).

# Estructura de carpetas

```
pjud-tracker/
├─ docker-compose.yml
├─ Dockerfile
├─ requirements.txt
├─ .env.example
├─ migrations/
│  └─ init.sql
└─ app/
   ├─ __init__.py
   ├─ config.py
   ├─ db.py
   ├─ models.py
   ├─ schemas.py
   ├─ main.py
   ├─ tasks.py
   ├─ feriados.py
   └─ ingest/
      ├─ portal.py
      └─ email.py
```
# **1) Objetivo y alcance**

- **Qué hace:** centraliza causas por **RUT/rol/tribunal**, detecta **novedades** (resoluciones, estados, escritos, audiencias), **notifica** (email/WhatsApp/app), agenda **plazos**, guarda **documentos** y permite **reportes**.  
- **Para quién:** **multi-abogado** y **multi-cliente** (**multi-tenant**), con **control de acceso por rol**.  

---

# **2) Arquitectura (alto nivel)**

- **Frontend:** Web (**React/Vue**) + app móvil opcional.  
- **Backend API:** Python (**FastAPI/Django Rest**) o Node (**NestJS**) con autenticación **JWT/OAuth2**.  
- **Ingesta de datos (módulos):**
  - **Conectores** a portales judiciales (**API oficial** si existe; si no, scraping con **Playwright/Scrapy** + colas).  
  - **Ingesta de emails** (parseo de notificaciones del tribunal).  
  - **OCR/PDF** para resoluciones y escritos.  
- **Procesamiento:** worker **asíncrono** (**Celery/RQ/Sidekiq**) para scraping, normalización y dif de cambios.  
- **Storage:** **PostgreSQL** (datos), **S3/MinIO** (archivos), **Redis** (colas/cache).  
- **Notificaciones:** **email** (SMTP/SendGrid), **WhatsApp/Telegram** (Twilio/Telegram Bot), **push**.  
- **Observabilidad:** logs + métricas + auditoría.  

---

# **3) Flujo de trabajo**

- **Alta de causa:** rol + tribunal + cliente (o importación masiva CSV/Excel).  
- **Monitoreo:**  
  Scheduler corre conectores (cada X minutos/horas por tribunal) → obtiene estado/actuaciones/documentos → **normaliza** → guarda **solo cambios (hash)**.  
- **Reglas y alertas:**  
  “Si entra nueva **resolución** con texto que contenga *traslado*, crear **plazo 5 días** y notificar responsable”.  
- **Calendario y plazos:**  
  Genera eventos **iCal/Google Calendar** (lectura/escritura si conectas OAuth).  
- **Bandeja de novedades:**  
  Vista por **abogado/cliente** con filtros y búsquedas (**texto completo sobre OCR**).  

---

# **4) Módulo de ingesta (scraping/API)**

- **Primero:** busca si hay **API oficial** o endpoints JSON.  
- Si no: **Playwright** (headless) para portales con login, captcha visual simple (evitar romper TOS), y paginación.  
- **Buenas prácticas:** **backoff**, **rotación IP** si el portal lo permite, y **respetar términos de uso**.  
- Si el portal **prohíbe scraping**, evalúa **convenio** o **parsing de emails oficiales** como fuente principal.  

---

# **5) Procesamiento de documentos y búsqueda**

- **OCR:** Tesseract o PaddleOCR. Para PDFs escaneados: **ocrmypdf**.  
- **Texto completo:** Postgres **pg_trgm/tsvector** o motor externo (**OpenSearch/Elasticsearch**) para búsquedas por frase, RUT, número de folio, etc.  
- **Extracción de fechas y entidades:** **spaCy** + reglas locales (fechas procesales, *téngase por notificado*, *traslado*, *cúmplase*).  

---

# **6) Seguridad y cumplimiento**

- **Legal:** revisa **TOS** del portal judicial, privacidad de **datos personales** (ej. normativa local de protección de datos).  
- **Técnico:** **RBAC**, **2FA**, cifrado **en reposo (KMS)** y **en tránsito (TLS)**, **auditoría** (quién vio/descargó qué), **retención de datos** y **políticas de borrado**.  
- **Multi-tenant:** scoping por **tenant_id** en todas las consultas.  

---

# **7) Frontend (vistas clave)**

- **Dashboard:** “novedades hoy”, plazos próximos, audiencias.  
- **Buscador:** por rol/tribunal/cliente/palabras clave (sobre OCR).  
- **Detalle de causa:** línea de tiempo, resoluciones, escritos, documentos, tareas.  
- **Reportes:** productividad (resoluciones por mes), SLA de respuesta, causas por estado/materia.  

---

# **8) Integraciones útiles**

- **Email in:** parseo de notificaciones del Poder Judicial (**IMAP webhook/cron**).  
- **Calendario:** **Google/Microsoft** para audiencias/plazos.  
- **Firma electrónica:** proveedor local si necesitas **presentar escritos** desde la plataforma (según normas).  
- **Facturación:** horas por causa → factura.  

---

# **9) Roadmap de MVP → Pro**

- **MVP:**  
  Alta de causas, conector a 1 portal, detección de novedades, notificación por email, subida/descarga de PDFs, búsqueda básica y plazos simples.  
- **Pro:**  
  OCR masivo + búsqueda semántica, reglas avanzadas (detectar *traslado*, *cúmplase*), dashboards, WhatsApp/push, multijurisdicción, auditoría completa, firmas/integraciones.  

---

# **Consejos prácticos antes de codear**

- Empieza por **una sola jurisdicción/portal** y documenta bien los **selectores** (cambian seguido).  
- Diseña el conector como **plugin** (interfaz común `search(rol)`, `fetch_events(...)`).  
- Logra **idempotencia** (hash de eventos/documentos) para evitar duplicados.  
- Mantén un **catálogo de feriados** y reglas de **días hábiles** por jurisdicción.  
- Define desde el día 1 **auditoría** y **backups**.  

# `requirements.txt`

```text
fastapi==0.112.0
uvicorn[standard]==0.30.5
SQLAlchemy==2.0.34
psycopg2-binary==2.9.9
alembic==1.13.2
pydantic==2.8.2
python-dotenv==1.0.1
celery==5.4.0
redis==5.0.8
playwright==1.47.2
beautifulsoup4==4.12.3
httpx==0.27.2
imapclient==2.3.1
mailparser==3.16.2
requests==2.32.3
```

# Próximos pasos

- Añadir reglas automáticas (p. ej. “si aparece *traslado*, crear plazo 5 días hábiles y notificar”).
- Exponer endpoints para creación/listado de **plazos** y enviar a Google Calendar.
- Integrar notificaciones por **email/WhatsApp/Telegram**.
- Desarrollar un **frontend** (React) con tablero de novedades y buscador.
- Auditoría, RBAC, backups y retención de datos.
