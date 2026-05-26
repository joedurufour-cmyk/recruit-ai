from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="RecruitAI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

KIMI_API_KEY = os.getenv("KIMI_API_KEY", "")
KIMI_MODEL = os.getenv("KIMI_MODEL", "kimi-latest")
KIMI_BASE = "https://api.moonshot.cn/v1"
API_SECRET = os.getenv("API_SECRET", "default-secret-change-me")

async def verify_api_key(x_api_key: str = Header("")):
    if not x_api_key or x_api_key != API_SECRET:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

class CvOptimizeRequest(BaseModel):
    name: str
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    profession: str
    cv_content: str
    industry: str = "general"

class LinkedinAnalyzeRequest(BaseModel):
    url: str = ""
    title: str
    bio: str
    skills: str = ""

class JobMatchRequest(BaseModel):
    job_title: str
    job_description: str
    user_profile: str
    interest: str = "medium"

class FreelanceSearchRequest(BaseModel):
    specialty: str
    level: str
    skills: str
    rate_range: str = "50-100"

class InterviewPrepRequest(BaseModel):
    position: str
    company: str = ""
    profile: str
    challenge: str = ""

class ApiResponse(BaseModel):
    result: str
    meta: dict = {}

async def kimi_chat(messages: list, temperature: float = 0.5, max_tokens: int = 2500) -> str:
    if not KIMI_API_KEY:
        raise HTTPException(status_code=500, detail="KIMI_API_KEY not configured")
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{KIMI_BASE}/chat/completions",
            headers={"Authorization": f"Bearer {KIMI_API_KEY}"},
            json={"model": KIMI_MODEL, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Kimi API error: {resp.status_code} {resp.text}")
    return resp.json()["choices"][0]["message"]["content"]

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

CV_SYSTEM = """Eres un experto en ATS y reclutamiento. Analiza CVs y proporciona:
1. Puntuacion ATS (0-100)
2. Palabras clave faltantes
3. Problemas de formato
4. Top 5 recomendaciones
5. Version optimizada del resumen
6. Puntos fuertes

Formato: Markdown. Espanol. Directo."""

LINKEDIN_SYSTEM = """Eres un experto en LinkedIn y personal branding tech.
1. Puntuacion (0-100)
2. Problemas criticos
3. Headline mejorado
4. About optimizado
5. Top 5 skills
6. Estrategia de contenido

Markdown. Espanol. Directo."""

JOB_MATCH_SYSTEM = """Eres un coach de carrera. Compara candidato vs oferta:
1. Match Score (0-100)
2. 5 fortalezas
3. 5 gaps
4. Recomendacion: SI/NO/MEJORAR
5. Puntos para cover letter
6. Red flags
7. Estrategia de negociacion

Markdown. Espanol. Directo."""

FREELANCE_SYSTEM = """Eres un experto en mercado freelance. Recomienda:
1. Top 5 proyectos a buscar
2. Rango de tarifa realista
3. Plataformas recomendadas
4. Palabras clave de busqueda
5. Estrategia de diferenciacion
6. Errores comunes
7. 3 ejemplos de proyectos

Markdown. Espanol."""

INTERVIEW_SYSTEM = """Eres un coach de entrevistas tech.
1. 5 preguntas probables + respuestas STAR
2. 3 escenarios de roleplay
3. 5 preguntas que DEBE hacer
4. Elevator pitch
5. Negociacion salarial
6. Como cerrar la entrevista
7. Checklist pre-entrevista
8. Respuesta a 'tus debilidades'

Markdown. Espanol."""

@app.get("/")
async def root():
    return {"status": "RecruitAI API running", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"ok": True, "kimi_configured": bool(KIMI_API_KEY)}

@app.post("/api/cv/optimize")
async def cv_optimize(req: CvOptimizeRequest, api_key: str = Depends(verify_api_key)):
    user_msg = f"""Analiza este CV para la industria "{req.industry or 'general'}":
DATOS: Nombre: {req.name}, Email: {req.email}, Profesion: {req.profession}
CV: {req.cv_content}
Proporciona analisis completo."""
    result = await kimi_chat([{"role": "system", "content": CV_SYSTEM}, {"role": "user", "content": user_msg}], 0.4, 2500)
    return {"result": strip_markdown(result), "meta": {"module": "cv_optimizer"}}

@app.post("/api/linkedin/analyze")
async def linkedin_analyze(req: LinkedinAnalyzeRequest, api_key: str = Depends(verify_api_key)):
    user_msg = f"""Analiza perfil LinkedIn:
Headline: {req.title}
About: {req.bio}
Skills: {req.skills or 'No especificados'}
Proporciona analisis completo."""
    result = await kimi_chat([{"role": "system", "content": LINKEDIN_SYSTEM}, {"role": "user", "content": user_msg}], 0.4, 2500)
    return {"result": strip_markdown(result), "meta": {"module": "linkedin_analyzer"}}

@app.post("/api/job/match")
async def job_match(req: JobMatchRequest, api_key: str = Depends(verify_api_key)):
    user_msg = f"""Analiza compatibilidad:
OFERTA: {req.job_title} - {req.job_description}
PERFIL: {req.user_profile}
Interes: {req.interest}
Proporciona analisis completo."""
    result = await kimi_chat([{"role": "system", "content": JOB_MATCH_SYSTEM}, {"role": "user", "content": user_msg}], 0.5, 2500)
    return {"result": strip_markdown(result), "meta": {"module": "job_analyzer"}}

@app.post("/api/freelance/search")
async def freelance_search(req: FreelanceSearchRequest, api_key: str = Depends(verify_api_key)):
    user_msg = f"""Recomienda proyectos freelance:
Especialidad: {req.specialty}, Nivel: {req.level}, Skills: {req.skills}, Tarifa: {req.rate_range}
Proporciona recomendaciones completas."""
    result = await kimi_chat([{"role": "system", "content": FREELANCE_SYSTEM}, {"role": "user", "content": user_msg}], 0.6, 2500)
    return {"result": strip_markdown(result), "meta": {"module": "freelance_search"}}

@app.post("/api/interview/prep")
async def interview_prep(req: InterviewPrepRequest, api_key: str = Depends(verify_api_key)):
    user_msg = f"""Prepara entrevista:
Puesto: {req.position}, Empresa: {req.company or 'No especificada'}, Perfil: {req.profile}, Desafio: {req.challenge or 'General'}
Genera preparacion completa."""
    result = await kimi_chat([{"role": "system", "content": INTERVIEW_SYSTEM}, {"role": "user", "content": user_msg}], 0.5, 3000)
    return {"result": strip_markdown(result), "meta": {"module": "interview_trainer"}}
