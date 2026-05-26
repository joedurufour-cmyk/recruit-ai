from flask import Flask, request, jsonify
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

KIMI_API_KEY = os.getenv("KIMI_API_KEY", "")
KIMI_MODEL = os.getenv("KIMI_MODEL", "kimi-latest")
KIMI_BASE = "https://api.moonshot.cn/v1"
API_SECRET = os.getenv("API_SECRET", "default-secret-change-me")

def verify_api_key():
    key = request.headers.get("x-api-key", "")
    if not key or key != API_SECRET:
        return jsonify({"error": "Invalid API key"}), 401
    return None

async def kimi_chat(messages, temperature=0.5, max_tokens=2500):
    if not KIMI_API_KEY:
        return jsonify({"error": "KIMI_API_KEY not configured"}), 500
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{KIMI_BASE}/chat/completions",
            headers={"Authorization": f"Bearer {KIMI_API_KEY}"},
            json={"model": KIMI_MODEL, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
        )
    if resp.status_code != 200:
        return jsonify({"error": f"Kimi API error: {resp.status_code}"}), 502
    return resp.json()["choices"][0]["message"]["content"]

def strip_markdown(text):
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

@app.route("/", methods=["GET"])
def root():
    return jsonify({"status": "RecruitAI API running", "version": "1.0.0"})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True, "kimi_configured": bool(KIMI_API_KEY)})

@app.route("/api/cv/optimize", methods=["POST"])
async def cv_optimize():
    err = verify_api_key()
    if err: return err
    data = request.get_json() or {}
    user_msg = f"""Analiza este CV para la industria "{data.get('industry', 'general')}":
DATOS: Nombre: {data.get('name', '')}, Email: {data.get('email', '')}, Profesion: {data.get('profession', '')}
CV: {data.get('cv_content', '')}
Proporciona analisis completo."""
    result = await kimi_chat([{"role": "system", "content": CV_SYSTEM}, {"role": "user", "content": user_msg}], 0.4, 2500)
    if isinstance(result, tuple): return result
    return jsonify({"result": strip_markdown(result), "meta": {"module": "cv_optimizer"}})

@app.route("/api/linkedin/analyze", methods=["POST"])
async def linkedin_analyze():
    err = verify_api_key()
    if err: return err
    data = request.get_json() or {}
    user_msg = f"""Analiza perfil LinkedIn:
Headline: {data.get('title', '')}
About: {data.get('bio', '')}
Skills: {data.get('skills', 'No especificados')}
Proporciona analisis completo."""
    result = await kimi_chat([{"role": "system", "content": LINKEDIN_SYSTEM}, {"role": "user", "content": user_msg}], 0.4, 2500)
    if isinstance(result, tuple): return result
    return jsonify({"result": strip_markdown(result), "meta": {"module": "linkedin_analyzer"}})

@app.route("/api/job/match", methods=["POST"])
async def job_match():
    err = verify_api_key()
    if err: return err
    data = request.get_json() or {}
    user_msg = f"""Analiza compatibilidad:
OFERTA: {data.get('job_title', '')} - {data.get('job_description', '')}
PERFIL: {data.get('user_profile', '')}
Interes: {data.get('interest', 'medium')}
Proporciona analisis completo."""
    result = await kimi_chat([{"role": "system", "content": JOB_MATCH_SYSTEM}, {"role": "user", "content": user_msg}], 0.5, 2500)
    if isinstance(result, tuple): return result
    return jsonify({"result": strip_markdown(result), "meta": {"module": "job_analyzer"}})

@app.route("/api/freelance/search", methods=["POST"])
async def freelance_search():
    err = verify_api_key()
    if err: return err
    data = request.get_json() or {}
    user_msg = f"""Recomienda proyectos freelance:
Especialidad: {data.get('specialty', '')}, Nivel: {data.get('level', '')}, Skills: {data.get('skills', '')}, Tarifa: {data.get('rate_range', '50-100')}
Proporciona recomendaciones completas."""
    result = await kimi_chat([{"role": "system", "content": FREELANCE_SYSTEM}, {"role": "user", "content": user_msg}], 0.6, 2500)
    if isinstance(result, tuple): return result
    return jsonify({"result": strip_markdown(result), "meta": {"module": "freelance_search"}})

@app.route("/api/interview/prep", methods=["POST"])
async def interview_prep():
    err = verify_api_key()
    if err: return err
    data = request.get_json() or {}
    user_msg = f"""Prepara entrevista:
Puesto: {data.get('position', '')}, Empresa: {data.get('company', 'No especificada')}, Perfil: {data.get('profile', '')}, Desafio: {data.get('challenge', 'General')}
Genera preparacion completa."""
    result = await kimi_chat([{"role": "system", "content": INTERVIEW_SYSTEM}, {"role": "user", "content": user_msg}], 0.5, 3000)
    if isinstance(result, tuple): return result
    return jsonify({"result": strip_markdown(result), "meta": {"module": "interview_trainer"}})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
