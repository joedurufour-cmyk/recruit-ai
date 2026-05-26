from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pydantic import BaseModel, ValidationError
import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

# ═══════════════════════════════════════════════════════════════════════════════
# CVME ENGINE v1.0 | RECRUITAI BACKEND
# Axioma: ERROR_MITIGATION > DOCUMENTATION > OPTIMIZATION
# Invariantes: INVARIANTE_1-10 activas
# ═══════════════════════════════════════════════════════════════════════════════

app = Flask(__name__)
CORS(app)

# ── L3: CONFIG ── INVARIANTE_1: SECRET_ISOLATION ────────────────────────────
KIMI_API_KEY = os.getenv("KIMI_API_KEY", "")
KIMI_MODEL = os.getenv("KIMI_MODEL", "kimi-latest")
KIMI_BASE = "https://api.moonshot.cn/v1"
API_SECRET = os.getenv("API_SECRET", "default-secret-change-me")

# ── Σ type: Result ── TIER_3 symbolic substitution ────────────────────────────
class Result:
    """Σ(T|E) - sum type. ¬ bare exception."""
    def __init__(self, ok: bool, data=None, error=None, status=200):
        self.ok = ok
        self.data = data
        self.error = error
        self.status = status

    def to_tuple(self):
        if self.ok:
            return {"result": self.data}, self.status
        return {"error": self.error}, self.status

# ── Ω marker: Kimi LLM call ── INVARIANTE_5: SEGREGACIÓN Ω vs λ ────────────────
def Ω_kimi_chat(messages: list, temperature: float = 0.5, max_tokens: int = 2500) -> Result:
    """Ω(f) - side effect declarado: llama a API externa."""
    if not KIMI_API_KEY:
        return Result(False, error="KIMI_API_KEY not configured", status=500)

    # τ constraint: 60s max
    τ_start = time.time()
    try:
        resp = requests.post(
            f"{KIMI_BASE}/chat/completions",
            headers={"Authorization": f"Bearer {KIMI_API_KEY}", "Content-Type": "application/json"},
            json={"model": KIMI_MODEL, "messages": messages, "temperature": temperature, "max_tokens": max_tokens},
            timeout=60
        )
        τ_elapsed = time.time() - τ_start

        if resp.status_code != 200:
            return Result(False, error=f"Kimi API error: {resp.status_code} - {resp.text}", status=502)

        content = resp.json()["choices"][0]["message"]["content"]
        return Result(True, data=content, meta={"latency_ms": int(τ_elapsed * 1000)})
    except requests.exceptions.Timeout:
        return Result(False, error="τ exceeded: Kimi API timeout > 60s", status=504)
    except Exception as e:
        return Result(False, error=f"Ω exception: {str(e)}", status=500)

# ── λ: Pure functions ── INVARIANTE_5 ──────────────────────────────────────────
def λ_strip_markdown(text: str) -> str:
    """λ - pura, sin side effects. Transforma input → output."""
    t = text.strip()
    if t.startswith("```"):
        lines = t.splitlines()
        if lines[0].startswith("```"): lines = lines[1:]
        if lines and lines[-1].startswith("```"): lines = lines[:-1]
        t = "\n".join(lines).strip()
    return t

def λ_verify_api_key(x_api_key: str) -> Result:
    """λ - pura. Validación sin side effects."""
    if not x_api_key or x_api_key != API_SECRET:
        return Result(False, error="Invalid API key", status=401)
    return Result(True, data="auth_ok")

# ── L2: API BOUNDARY ── INVARIANTE_2: BOUNDARY_VALIDATION ───────────────────────
# {P} Precondiciones como Pydantic schemas
class CvOptimizeIn(BaseModel):
    name: str
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    profession: str
    cv_content: str
    industry: str = "general"

class LinkedinAnalyzeIn(BaseModel):
    url: str = ""
    title: str
    bio: str
    skills: str = ""

class JobMatchIn(BaseModel):
    job_title: str
    job_description: str
    user_profile: str
    interest: str = "medium"

class FreelanceSearchIn(BaseModel):
    specialty: str
    level: str
    skills: str
    rate_range: str = "50-100"

class InterviewPrepIn(BaseModel):
    position: str
    company: str = ""
    profile: str
    challenge: str = ""

# ── System prompts ── INVARIANTE_8: determinismo ─────────────────────────────
CV_SYSTEM = """Eres un experto en ATS y reclutamiento. Analiza CVs y proporciona:
1. Puntuación ATS (0-100) con criterios detallados
2. Palabras clave faltantes para la industria
3. Problemas de formato y estructura
4. Top 5 recomendaciones específicas y accionables
5. Versión optimizada del resumen profesional
6. Puntos fuertes que debe destacar

Formato: Markdown profesional con headers, bullet points, y tabla de scoring.
Español. Directo, sin fluff."""

LINKEDIN_SYSTEM = """Eres un experto en LinkedIn y personal branding para profesionales tech.
Analiza perfiles y proporciona:
1. Puntuación de optimización (0-100)
2. Problemas críticos identificados
3. Headline mejorado (máx 120 caracteres)
4. About section optimizado y listo para copiar
5. Top 5 skills a destacar y por qué
6. Estrategia de contenido semanal para engagement

Markdown con secciones claras. Español. Directo y accionable."""

JOB_MATCH_SYSTEM = """Eres un experto en análisis de compatibilidad laboral y coach de carrera.
Compara candidato vs oferta y proporciona:
1. Match Score (0-100) con breakdown por categoría
2. Top 5 fortalezas para esta posición específica
3. Top 5 gaps o áreas de mejora urgentes
4. Recomendación CLARA: SÍ aplicar / NO todavía / MEJORAR antes
5. Top 3 puntos para enfatizar en cover letter
6. Red flags de la oferta (si existen)
7. Estrategia de negociación si aplica

Honesto pero constructivo. Markdown. Español."""

FREELANCE_SYSTEM = """Eres un experto en mercado freelance (Upwork, Toptal, Fiverr, Contra, etc).
Recomienda proyectos y nichos rentables. Proporciona:
1. Top 5 tipos de proyectos que debería buscar AHORA
2. Rango de tarifa realista para su nivel y especialidad
3. Plataformas recomendadas con pros/cons
4. Palabras clave para búsqueda efectiva
5. Estrategia de diferenciación contra la competencia
6. Errores comunes que cuestan contratos
7. 3 ejemplos concretos de proyectos tipo

Markdown. Español. Directo."""

INTERVIEW_SYSTEM = """Eres un coach de entrevistas de alto nivel. Prepara candidatos para procesos selectivos tech.
Genera:
1. 5 preguntas probables + respuestas en formato STAR
2. 3 escenarios de roleplay (pregunta + sugerencia de respuesta)
3. 5 preguntas que EL candidato DEBE hacer
4. Elevator pitch personalizado listo para usar
5. Estrategia de negociación salarial
6. Cómo cerrar la entrevista con impacto
7. Checklist pre-entrevista (24h, 2h, 30min antes)
8. Respuesta perfecta para "¿Cuáles son tus debilidades?"

Markdown. Español. Específico, práctico, motivador."""

# ── GATE_1: Validation helper ── INVARIANTE_2 ────────────────────────────────
def gate_validate(schema_class, data: dict) -> Result:
    """{P} - precondición como schema. Si falla → 422 ANTES de ejecutar C."""
    try:
        validated = schema_class(**data)
        return Result(True, data=validated)
    except ValidationError as e:
        errors = []
        for err in e.errors():
            errors.append(f"{'.'.join(str(x) for x in err['loc'])}: {err['msg']}")
        return Result(False, error=f"Validation failed: {' | '.join(errors)}", status=422)

# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/", methods=["GET"])
def root():
    return send_file('index.html')

@app.route("/app", methods=["GET"])
def app_page():
    return send_file('index.html')

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True, "kimi_configured": bool(KIMI_API_KEY)})

@app.route("/api/cv/optimize", methods=["POST"])
def cv_optimize():
    # GATE_0: Auth
    auth = λ_verify_api_key(request.headers.get("x-api-key", ""))
    if not auth.ok:
        body, code = auth.to_tuple()
        return jsonify(body), code

    # GATE_1: Schema validation
    data = request.get_json() or {}
    validated = gate_validate(CvOptimizeIn, data)
    if not validated.ok:
        body, code = validated.to_tuple()
        return jsonify(body), code

    req = validated.data
    req_dict = req.dict()
    msg = f"""Analiza este CV para la industria "{req_dict.get('industry', 'general')}":
DATOS PERSONALES:
- Nombre: {req_dict.get('name', '')}
- Email: {req_dict.get('email', '')}
- Teléfono: {req_dict.get('phone', '')}
- LinkedIn: {req_dict.get('linkedin', '')}
- Profesión: {req_dict.get('profession', '')}

CONTENIDO DEL CV:
{req_dict.get('cv_content', '')}

Proporciona análisis completo."""

    result = Ω_kimi_chat([{"role": "system", "content": CV_SYSTEM}, {"role": "user", "content": msg}], 0.4, 2500)
    if not result.ok:
        body, code = result.to_tuple()
        return jsonify(body), code

    return jsonify({"result": λ_strip_markdown(result.data), "meta": {"module": "cv_optimizer", "industry": req_dict.get('industry', 'general')}})

@app.route("/api/linkedin/analyze", methods=["POST"])
def linkedin_analyze():
    auth = λ_verify_api_key(request.headers.get("x-api-key", ""))
    if not auth.ok:
        body, code = auth.to_tuple()
        return jsonify(body), code
    
    data = request.get_json() or {}
    validated = gate_validate(LinkedinAnalyzeIn, data)
    if not validated.ok:
        body, code = validated.to_tuple()
        return jsonify(body), code
    
    req = validated.data.dict()
    msg = f"""Analiza mi perfil de LinkedIn:
HEADLINE ACTUAL:
{req.get('title', '')}

ABOUT SECTION:
{req.get('bio', '')}

SKILLS:
{req.get('skills', 'No especificados')}

URL: {req.get('url', 'No proporcionada')}

Proporciona análisis completo."""
    
    result = Ω_kimi_chat([{"role": "system", "content": LINKEDIN_SYSTEM}, {"role": "user", "content": msg}], 0.4, 2500)
    if not result.ok:
        body, code = result.to_tuple()
        return jsonify(body), code
    
    return jsonify({"result": λ_strip_markdown(result.data), "meta": {"module": "linkedin_analyzer"}})

@app.route("/api/job/match", methods=["POST"])
def job_match():
    auth = λ_verify_api_key(request.headers.get("x-api-key", ""))
    if not auth.ok:
        body, code = auth.to_tuple()
        return jsonify(body), code
    
    data = request.get_json() or {}
    validated = gate_validate(JobMatchIn, data)
    if not validated.ok:
        body, code = validated.to_tuple()
        return jsonify(body), code
    
    req = validated.data.dict()
    msg = f"""Analiza compatibilidad:

OFERTA:
Puesto: {req.get('job_title', '')}
Descripción: {req.get('job_description', '')}

MI PERFIL:
{req.get('user_profile', '')}

Interés en aplicar: {req.get('interest', 'medium')}

Proporciona análisis completo."""
    
    result = Ω_kimi_chat([{"role": "system", "content": JOB_MATCH_SYSTEM}, {"role": "user", "content": msg}], 0.5, 2500)
    if not result.ok:
        body, code = result.to_tuple()
        return jsonify(body), code
    
    return jsonify({"result": λ_strip_markdown(result.data), "meta": {"module": "job_analyzer", "interest": req.get('interest', 'medium')}})

@app.route("/api/freelance/search", methods=["POST"])
def freelance_search():
    auth = λ_verify_api_key(request.headers.get("x-api-key", ""))
    if not auth.ok:
        body, code = auth.to_tuple()
        return jsonify(body), code
    
    data = request.get_json() or {}
    validated = gate_validate(FreelanceSearchIn, data)
    if not validated.ok:
        body, code = validated.to_tuple()
        return jsonify(body), code
    
    req = validated.data.dict()
    msg = f"""Recomiéndame proyectos freelance:

ESPECIALIDAD: {req.get('specialty', '')}
NIVEL: {req.get('level', '')}
SKILLS: {req.get('skills', '')}
TARIFA ESPERADA: {req.get('rate_range', '50-100')}/hora

Proporciona recomendaciones completas."""
    
    result = Ω_kimi_chat([{"role": "system", "content": FREELANCE_SYSTEM}, {"role": "user", "content": msg}], 0.6, 2500)
    if not result.ok:
        body, code = result.to_tuple()
        return jsonify(body), code
    
    return jsonify({"result": λ_strip_markdown(result.data), "meta": {"module": "freelance_search", "specialty": req.get('specialty', '')}})

@app.route("/api/interview/prep", methods=["POST"])
def interview_prep():
    auth = λ_verify_api_key(request.headers.get("x-api-key", ""))
    if not auth.ok:
        body, code = auth.to_tuple()
        return jsonify(body), code
    
    data = request.get_json() or {}
    validated = gate_validate(InterviewPrepIn, data)
    if not validated.ok:
        body, code = validated.to_tuple()
        return jsonify(body), code
    
    req = validated.data.dict()
    msg = f"""Prepárame para entrevista:

PUESTO: {req.get('position', '')}
EMPRESA: {req.get('company', 'No especificada')}
MI PERFIL: {req.get('profile', '')}
DESAFÍO PRINCIPAL: {req.get('challenge', 'General')}

Genera preparación completa."""
    
    result = Ω_kimi_chat([{"role": "system", "content": INTERVIEW_SYSTEM}, {"role": "user", "content": msg}], 0.5, 3000)
    if not result.ok:
        body, code = result.to_tuple()
        return jsonify(body), code
    
    return jsonify({"result": λ_strip_markdown(result.data), "meta": {"module": "interview_trainer", "challenge": req.get('challenge', '')}})

# ═══════════════════════════════════════════════════════════════════════════════
# INTAKE DECODER ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

INTAKE_SYSTEM = """Eres el motor INTAKE Decoder v2. Tu trabajo es tomar texto caótico, desordenado, con typos, fragmentos, dictado de voz mal transcrito — y transformarlo en un reporte ejecutivo estructurado.

PROCESO:
1. Corregir texto (typos, normalizar, segmentar en oraciones)
2. Clasificar intención: PRODUCIR|SOLUCIONAR|CREAR|INVESTIGAR|PROCESAR|DESAHOGO
3. Extraer entidades: dinero, fechas, emails, personas, sistemas, keywords
4. Catalogar variables clave
5. Generar tareas priorizadas (P1/P2/P3)
6. Detectar gaps y rellenar con inferencia contextual
7. Redactar reporte ejecutivo

OUTPUT FORMAT (Markdown estructurado):

# INTAKE REPORT

## 1. Texto corregido
[texto limpio, normalizado]

## 2. Clasificación
- Tipo: [PRODUCIR|SOLUCIONAR|CREAR|INVESTIGAR|PROCESAR|DESAHOGO]
- Confianza: [N]%
- Template: [nombre]

## 3. Análisis de Intención
- Problema presentado: [primeras 120 chars del input]
- Problema real: [qué realmente necesita resolver]
- Necesidad oculta: [lo que no dice explícitamente pero implica]
- Objetivo real: [acción concreta a ejecutar]

## 4. Prioridad Automática
- Nivel: [ALTA|MEDIA|BAJA]
- Score: [N]/100
- Justificación: [por qué]

## 5. Tareas Catalogadas (máx 8)
- [P1/P2/P3] [VERBO]: [objeto]
  - Categoría: [finanzas|trabajo|producto|casa|entregable|general]
  - Plazo: [fecha o 'no definido']
  - Siguiente paso: [acción inmediata]

## 6. Variables Detectadas
- [tipo]: [valor] ([confianza]%)

## 7. Gaps y Recomendaciones
- [qué falta]: [sugerencia de relleno]

## 8. Entidades Extraídas
- Dinero: [...]
- Fechas: [...]
- Personas: [...]
- Sistemas: [...]
- Keywords: [...]

Reglas:
- Sé directo, sin fluff
- Si es DESAHOGO, primero validar emociones sin forzar solución
- Prioridad por: bloqueo > fecha cercana > impacto externo > esfuerzo
- Siempre proponer próximo paso verificable"""

class IntakeDecodeIn(BaseModel):
    text: str
    mode: str = "standard"
    autofill: bool = True

class IntakeSaveIn(BaseModel):
    id: int = 0
    input: str
    corrected_text: str
    classification_type: str
    classification_confidence: int
    template: str
    priority_level: str
    priority_score: int
    tasks: list
    variables: list
    gaps: list
    entities: dict
    markdown: str
    raw: str
    profile: dict

# ── Simple SQLite persistence for INTAKE reports ──
import sqlite3
import json

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "intake_reports.db")

def init_intake_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        input TEXT,
        corrected_text TEXT,
        classification_type TEXT,
        classification_confidence INTEGER,
        template TEXT,
        priority_level TEXT,
        priority_score INTEGER,
        tasks TEXT,
        variables TEXT,
        gaps TEXT,
        entities TEXT,
        markdown TEXT,
        raw TEXT,
        profile TEXT
    )''')
    conn.commit()
    conn.close()

init_intake_db()

@app.route("/intake", methods=["GET"])
def intake_page():
    return send_file('intake-offline.html')

@app.route("/api/intake/decode", methods=["POST"])
def intake_decode():
    auth = λ_verify_api_key(request.headers.get("x-api-key", ""))
    if not auth.ok:
        body, code = auth.to_tuple()
        return jsonify(body), code
    
    data = request.get_json() or {}
    validated = gate_validate(IntakeDecodeIn, data)
    if not validated.ok:
        body, code = validated.to_tuple()
        return jsonify(body), code
    
    req = validated.data.dict()
    text = req.get('text', '')
    mode = req.get('mode', 'standard')
    
    msg = f"""Procesa el siguiente INTAKE:

MODO: {mode}

TEXTO ORIGINAL:
{text}

Genera reporte completo siguiendo el formato especificado."""
    
    result = Ω_kimi_chat([
        {"role": "system", "content": INTAKE_SYSTEM},
        {"role": "user", "content": msg}
    ], 0.4, 3000)
    
    if not result.ok:
        body, code = result.to_tuple()
        return jsonify(body), code
    
    return jsonify({
        "result": λ_strip_markdown(result.data),
        "meta": {
            "module": "intake_decoder",
            "mode": mode,
            "input_length": len(text)
        }
    })

@app.route("/api/intake/save", methods=["POST"])
def intake_save():
    auth = λ_verify_api_key(request.headers.get("x-api-key", ""))
    if not auth.ok:
        body, code = auth.to_tuple()
        return jsonify(body), code
    
    data = request.get_json() or {}
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO reports 
        (input, corrected_text, classification_type, classification_confidence, 
         template, priority_level, priority_score, tasks, variables, gaps, 
         entities, markdown, raw, profile)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (
            data.get('input', ''),
            data.get('corrected_text', ''),
            data.get('classification_type', ''),
            data.get('classification_confidence', 0),
            data.get('template', ''),
            data.get('priority_level', ''),
            data.get('priority_score', 0),
            json.dumps(data.get('tasks', [])),
            json.dumps(data.get('variables', [])),
            json.dumps(data.get('gaps', [])),
            json.dumps(data.get('entities', {})),
            data.get('markdown', ''),
            data.get('raw', ''),
            json.dumps(data.get('profile', {}))
        ))
    conn.commit()
    report_id = c.lastrowid
    conn.close()
    
    return jsonify({"ok": True, "id": report_id, "message": "Report saved"})

@app.route("/api/intake/reports", methods=["GET"])
def intake_reports():
    auth = λ_verify_api_key(request.headers.get("x-api-key", ""))
    if not auth.ok:
        body, code = auth.to_tuple()
        return jsonify(body), code
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, created_at, classification_type, priority_level, priority_score, template FROM reports ORDER BY id DESC')
    rows = c.fetchall()
    conn.close()
    
    reports = []
    for row in rows:
        reports.append({
            "id": row[0],
            "created_at": row[1],
            "classification_type": row[2],
            "priority_level": row[3],
            "priority_score": row[4],
            "template": row[5]
        })
    
    return jsonify({"reports": reports, "count": len(reports)})

@app.route("/api/intake/report/<int:report_id>", methods=["GET"])
def intake_report_get(report_id):
    auth = λ_verify_api_key(request.headers.get("x-api-key", ""))
    if not auth.ok:
        body, code = auth.to_tuple()
        return jsonify(body), code
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM reports WHERE id = ?', (report_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return jsonify({"error": "Report not found"}), 404
    
    return jsonify({
        "id": row[0],
        "created_at": row[1],
        "input": row[2],
        "corrected_text": row[3],
        "classification_type": row[4],
        "classification_confidence": row[5],
        "template": row[6],
        "priority_level": row[7],
        "priority_score": row[8],
        "tasks": json.loads(row[9] or '[]'),
        "variables": json.loads(row[10] or '[]'),
        "gaps": json.loads(row[11] or '[]'),
        "entities": json.loads(row[12] or '{}'),
        "markdown": row[13],
        "raw": row[14],
        "profile": json.loads(row[15] or '{}')
    })

@app.route("/api/intake/report/<int:report_id>", methods=["DELETE"])
def intake_report_delete(report_id):
    auth = λ_verify_api_key(request.headers.get("x-api-key", ""))
    if not auth.ok:
        body, code = auth.to_tuple()
        return jsonify(body), code
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM reports WHERE id = ?', (report_id,))
    conn.commit()
    deleted = c.rowcount
    conn.close()
    
    return jsonify({"ok": deleted > 0, "deleted": deleted})

# ═══════════════════════════════════════════════════════════════════════════════
# END INTAKE DECODER
# ═══════════════════════════════════════════════════════════════════════════════


