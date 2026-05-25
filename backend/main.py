from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Literal
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="RecruitAI API", version="1.0.0")

# CORS — tighten to your Cloudflare domain in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Kimi / Moonshot AI Configuration
KIMI_API_KEY = os.getenv("KIMI_API_KEY", "")
KIMI_MODEL = os.getenv("KIMI_MODEL", "kimi-latest")
KIMI_BASE = "https://api.moonshot.cn/v1"

# Your own API key for users calling your backend
API_SECRET = os.getenv("API_SECRET", "default-secret-change-me")

# ============================================================
# Auth
# ============================================================
async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if not x_api_key or x_api_key != API_SECRET:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

# ============================================================
# Models
# ============================================================
class CvOptimizeRequest(BaseModel):
    name: str
    email: Optional[str] = ""
    phone: Optional[str] = ""
    linkedin: Optional[str] = ""
    profession: str
    cv_content: str
    industry: Optional[str] = "general"

class LinkedinAnalyzeRequest(BaseModel):
    url: Optional[str] = ""
    title: str
    bio: str
    skills: Optional[str] = ""

class JobMatchRequest(BaseModel):
    job_title: str
    job_description: str
    user_profile: str
    interest: Optional[str] = "medium"

class FreelanceSearchRequest(BaseModel):
    specialty: str
    level: str
    skills: str
    rate_range: Optional[str] = "50-100"

class InterviewPrepRequest(BaseModel):
    position: str
    company: Optional[str] = ""
    profile: str
    challenge: Optional[str] = ""

class ApiResponse(BaseModel):
    result: str
    meta: dict

# ============================================================
# Kimi LLM Helper
# ============================================================
async def kimi_chat(messages: list, temperature: float = 0.5, max_tokens: int = 2500) -> str:
    if not KIMI_API_KEY:
        raise HTTPException(status_code=500, detail="KIMI_API_KEY not configured")

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{KIMI_BASE}/chat/completions",
            headers={"Authorization": f"Bearer {KIMI_API_KEY}"},
            json={
                "model": KIMI_MODEL,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Kimi API error: {resp.status_code} {resp.text}")

    data = resp.json()
    return data["choices"][0]["message"]["content"]

def strip_markdown(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        lines = t.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        t = "\n".join(lines).strip()
    return t

# ============================================================
# System Prompts
# ============================================================
CV_SYSTEM = """Eres un experto en ATS (Applicant Tracking Systems) y reclutamiento con 10+ años de experiencia.
Tu tarea es analizar CVs y proporcionar:
1. Puntuación ATS (0-100) con criterios detallados
2. Palabras clave faltantes para la industria
3. Problemas de formato y estructura
4. Top 5 recomendaciones específicas y accionables
5. Versión optimizada del resumen profesional
6. Puntos fuertes que debe destacar

Formato: Markdown profesional con headers, bullet points, y una tabla de scoring.
Escribe en español. Sé directo, no uses fluff."""

LINKEDIN_SYSTEM = """Eres un experto en LinkedIn y personal branding para profesionales tech.
Analiza perfiles y proporciona:
1. Puntuación de optimización (0-100)
2. Problemas críticos identificados
3. Headline mejorado (máx 120 caracteres)
4. About section optimizado y listo para copiar
5. Top 5 skills a destacar y por qué
6. Estrategia de contenido semanal para engagement

Formato: Markdown con secciones claras. Español. Directo y accionable."""

JOB_MATCH_SYSTEM = """Eres un experto en análisis de compatibilidad laboral y coach de carrera.
Compara candidato vs oferta y proporciona:
1. Match Score (0-100) con breakdown por categoría
2. Top 5 fortalezas para esta posición específica
3. Top 5 gaps o áreas de mejora urgentes
4. Recomendación CLARA: SÍ aplicar / NO todavía / MEJORAR antes
5. Top 3 puntos para enfatizar en cover letter
6. Red flags de la oferta (si existen)
7. Estrategia de negociación si aplica

Sé honesto pero constructivo. Markdown. Español."""

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

# ============================================================
# Endpoints
# ============================================================
@app.get("/")
async def root():
    return {"status": "RecruitAI API running", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"ok": True, "kimi_configured": bool(KIMI_API_KEY)}

@app.post("/api/cv/optimize", response_model=ApiResponse)
async def cv_optimize(req: CvOptimizeRequest, api_key: str = Depends(verify_api_key)):
    user_msg = f"""Analiza este CV para la industria "{req.industry or 'general'}":

DATOS PERSONALES:
- Nombre: {req.name}
- Email: {req.email}
- Teléfono: {req.phone}
- LinkedIn: {req.linkedin}
- Profesión: {req.profession}

CONTENIDO DEL CV:
{req.cv_content}

Proporciona análisis completo."""

    result = await kimi_chat([
        {"role": "system", "content": CV_SYSTEM},
        {"role": "user", "content": user_msg}
    ], temperature=0.4, max_tokens=2500)

    return ApiResponse(result=strip_markdown(result), meta={"module": "cv_optimizer", "industry": req.industry})

@app.post("/api/linkedin/analyze", response_model=ApiResponse)
async def linkedin_analyze(req: LinkedinAnalyzeRequest, api_key: str = Depends(verify_api_key)):
    user_msg = f"""Analiza mi perfil de LinkedIn:

HEADLINE ACTUAL:
{req.title}

ABOUT SECTION:
{req.bio}

SKILLS:
{req.skills or 'No especificados'}

URL: {req.url or 'No proporcionada'}

Proporciona análisis completo."""

    result = await kimi_chat([
        {"role": "system", "content": LINKEDIN_SYSTEM},
        {"role": "user", "content": user_msg}
    ], temperature=0.4, max_tokens=2500)

    return ApiResponse(result=strip_markdown(result), meta={"module": "linkedin_analyzer"})

@app.post("/api/job/match", response_model=ApiResponse)
async def job_match(req: JobMatchRequest, api_key: str = Depends(verify_api_key)):
    user_msg = f"""Analiza compatibilidad:

OFERTA:
Puesto: {req.job_title}
Descripción: {req.job_description}

MI PERFIL:
{req.user_profile}

Interés en aplicar: {req.interest}

Proporciona análisis completo."""

    result = await kimi_chat([
        {"role": "system", "content": JOB_MATCH_SYSTEM},
        {"role": "user", "content": user_msg}
    ], temperature=0.5, max_tokens=2500)

    return ApiResponse(result=strip_markdown(result), meta={"module": "job_analyzer", "interest": req.interest})

@app.post("/api/freelance/search", response_model=ApiResponse)
async def freelance_search(req: FreelanceSearchRequest, api_key: str = Depends(verify_api_key)):
    user_msg = f"""Recomiéndame proyectos freelance:

ESPECIALIDAD: {req.specialty}
NIVEL: {req.level}
SKILLS: {req.skills}
TARIFA ESPERADA: {req.rate_range}/hora

Proporciona recomendaciones completas."""

    result = await kimi_chat([
        {"role": "system", "content": FREELANCE_SYSTEM},
        {"role": "user", "content": user_msg}
    ], temperature=0.6, max_tokens=2500)

    return ApiResponse(result=strip_markdown(result), meta={"module": "freelance_search", "specialty": req.specialty})

@app.post("/api/interview/prep", response_model=ApiResponse)
async def interview_prep(req: InterviewPrepRequest, api_key: str = Depends(verify_api_key)):
    user_msg = f"""Prepárame para entrevista:

PUESTO: {req.position}
EMPRESA: {req.company or 'No especificada'}
MI PERFIL: {req.profile}
DESAFÍO PRINCIPAL: {req.challenge or 'General'}

Genera preparación completa."""

    result = await kimi_chat([
        {"role": "system", "content": INTERVIEW_SYSTEM},
        {"role": "user", "content": user_msg}
    ], temperature=0.5, max_tokens=3000)

    return ApiResponse(result=strip_markdown(result), meta={"module": "interview_trainer", "challenge": req.challenge})
