from flask import Flask, request, jsonify
import os
import requests
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

def kimi_chat(messages, temperature=0.5, max_tokens=2500):
    if not KIMI_API_KEY:
        return jsonify({"error": "KIMI_API_KEY not configured"}), 500
    resp = requests.post(
        f"{KIMI_BASE}/chat/completions",
        headers={"Authorization": f"Bearer {KIMI_API_KEY}", "Content-Type": "application/json"},
        json={"model": KIMI_MODEL, "messages": messages, "temperature": temperature, "max_tokens": max_tokens},
        timeout=60
    )
    if resp.status_code != 200:
        return jsonify({"error": f"Kimi API error: {resp.status_code}"}), 502
    return resp.json()["choices"][0]["message"]["content"]

def strip_markdown(text):
    t = text.strip()
    if t.startswith("```"):
        lines = t.splitlines()
        if lines[0].startswith("```"): lines = lines[1:]
        if lines and lines[-1].startswith("```"): lines = lines[:-1]
        t = "\n".join(lines).strip()
    return t

CV_SYSTEM = "Eres un experto en ATS y reclutamiento. Analiza CVs. Markdown. Espanol. Directo."
LINKEDIN_SYSTEM = "Eres un experto en LinkedIn. Analiza perfiles. Markdown. Espanol. Directo."
JOB_MATCH_SYSTEM = "Eres un coach de carrera. Compara candidato vs oferta. Markdown. Espanol."
FREELANCE_SYSTEM = "Eres un experto en mercado freelance. Recomienda proyectos. Markdown. Espanol."
INTERVIEW_SYSTEM = "Eres un coach de entrevistas tech. Prepara candidatos. Markdown. Espanol."

@app.route("/", methods=["GET"])
def root():
    return jsonify({"status": "RecruitAI API running", "version": "1.0.0"})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True, "kimi_configured": bool(KIMI_API_KEY)})

@app.route("/api/cv/optimize", methods=["POST"])
def cv_optimize():
    err = verify_api_key()
    if err: return err
    data = request.get_json() or {}
    msg = f"Analiza CV para {data.get('industry','general')}: Nombre: {data.get('name','')}, Profesion: {data.get('profession','')}\nCV: {data.get('cv_content','')}"
    result = kimi_chat([{"role": "system", "content": CV_SYSTEM}, {"role": "user", "content": msg}], 0.4, 2500)
    if isinstance(result, tuple): return result
    return jsonify({"result": strip_markdown(result), "meta": {"module": "cv_optimizer"}})

@app.route("/api/linkedin/analyze", methods=["POST"])
def linkedin_analyze():
    err = verify_api_key()
    if err: return err
    data = request.get_json() or {}
    msg = f"Analiza LinkedIn: Headline: {data.get('title','')}\nAbout: {data.get('bio','')}\nSkills: {data.get('skills','')}"
    result = kimi_chat([{"role": "system", "content": LINKEDIN_SYSTEM}, {"role": "user", "content": msg}], 0.4, 2500)
    if isinstance(result, tuple): return result
    return jsonify({"result": strip_markdown(result), "meta": {"module": "linkedin_analyzer"}})

@app.route("/api/job/match", methods=["POST"])
def job_match():
    err = verify_api_key()
    if err: return err
    data = request.get_json() or {}
    msg = f"Match: Oferta: {data.get('job_title','')} - {data.get('job_description','')}\nPerfil: {data.get('user_profile','')}\nInteres: {data.get('interest','medium')}"
    result = kimi_chat([{"role": "system", "content": JOB_MATCH_SYSTEM}, {"role": "user", "content": msg}], 0.5, 2500)
    if isinstance(result, tuple): return result
    return jsonify({"result": strip_markdown(result), "meta": {"module": "job_analyzer"}})

@app.route("/api/freelance/search", methods=["POST"])
def freelance_search():
    err = verify_api_key()
    if err: return err
    data = request.get_json() or {}
    msg = f"Freelance: {data.get('specialty','')}, Nivel: {data.get('level','')}, Skills: {data.get('skills','')}, Tarifa: {data.get('rate_range','50-100')}"
    result = kimi_chat([{"role": "system", "content": FREELANCE_SYSTEM}, {"role": "user", "content": msg}], 0.6, 2500)
    if isinstance(result, tuple): return result
    return jsonify({"result": strip_markdown(result), "meta": {"module": "freelance_search"}})

@app.route("/api/interview/prep", methods=["POST"])
def interview_prep():
    err = verify_api_key()
    if err: return err
    data = request.get_json() or {}
    msg = f"Entrevista: {data.get('position','')}, Empresa: {data.get('company','')}, Perfil: {data.get('profile','')}, Desafio: {data.get('challenge','')}"
    result = kimi_chat([{"role": "system", "content": INTERVIEW_SYSTEM}, {"role": "user", "content": msg}], 0.5, 3000)
    if isinstance(result, tuple): return result
    return jsonify({"result": strip_markdown(result), "meta": {"module": "interview_trainer"}})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
