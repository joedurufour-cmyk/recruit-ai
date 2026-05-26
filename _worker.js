export default {
  async fetch(request, env) {
    const html = `<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RecruitAI</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#0a0e1a;color:#e2e8f0;line-height:1.6}
.container{max-width:900px;margin:0 auto;padding:16px}

/* Header */
.header{background:#0f172a;border:1px solid #1e293b;border-radius:12px;padding:20px;margin-bottom:20px;text-align:center;position:relative}
.header h1{font-size:1.8rem;background:linear-gradient(135deg,#00d9ff,#ff006e);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:4px}
.header p{color:#64748b;font-size:.9rem}
.settings-btn{position:absolute;top:12px;right:12px;background:#1e293b;border:1px solid #334155;border-radius:8px;padding:6px 10px;cursor:pointer;font-size:.8rem;color:#94a3b8}
.settings-btn:active{background:#334155}

/* Connection Panel */
.conn-panel{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:16px;margin-bottom:20px;display:none}
.conn-panel.open{display:block}
.conn-panel label{display:block;margin:12px 0 4px;font-size:.85rem;color:#94a3b8}
.conn-panel input{width:100%;padding:10px;background:#0f172a;border:1px solid #334155;border-radius:8px;color:#e2e8f0;font-size:1rem}
.conn-btns{margin-top:12px;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.status-text{font-size:.85rem;margin-left:8px}

/* Cards Grid */
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-bottom:20px}
@media(min-width:600px){.grid{grid-template-columns:repeat(3,1fr)}}
.card{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:16px;cursor:pointer;transition:all .2s}
.card:active{background:#334155;transform:scale(.98)}
.card h3{color:#00d9ff;font-size:1rem;margin-bottom:6px}
.card p{color:#94a3b8;font-size:.85rem}

/* Module Forms */
.module{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:16px;margin-bottom:16px;display:none}
.module.open{display:block}
.module h3{color:#00d9ff;margin-bottom:8px;font-size:1.1rem}
.module label{display:block;margin:12px 0 4px;font-size:.85rem;color:#94a3b8}
.module input,.module textarea,.module select{width:100%;padding:10px;background:#0f172a;border:1px solid #334155;border-radius:8px;color:#e2e8f0;font-size:1rem}
.module textarea{min-height:100px;resize:vertical}

/* Buttons */
.btn{background:linear-gradient(135deg,#00d9ff,#ff006e);color:#fff;border:none;padding:10px 20px;border-radius:8px;cursor:pointer;font-weight:600;font-size:.9rem;margin-top:12px}
.btn:active{opacity:.8}

/* Results */
.result{background:#0f172a;border-left:3px solid #00d9ff;border-radius:8px;padding:12px;margin-top:12px;display:none;white-space:pre-wrap;font-size:.9rem;line-height:1.5}
.result.open{display:block}
.result.error{border-left-color:#ef4444;color:#fca5a5}
.result .ok{color:#22c55e;font-weight:600;margin-bottom:6px}
.result .err{color:#ef4444;font-weight:600;margin-bottom:6px}
.loading{color:#64748b;text-align:center;padding:20px}

/* Tips */
.tip{font-size:.8rem;color:#64748b;margin-top:8px}
</style>
</head>
<body>
<div class="container">

<div class="header">
  <h1>⚡ RecruitAI</h1>
  <p>Suite de Reclutamiento con IA</p>
  <button class="settings-btn" onclick="toggleSettings()">⚙️</button>
</div>

<div id="connPanel" class="conn-panel">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
    <h3 style="color:#00d9ff;font-size:1rem">⚙️ Conexión Backend</h3>
    <button onclick="toggleSettings()" style="background:none;border:none;color:#64748b;font-size:1.2rem;cursor:pointer">×</button>
  </div>
  <label>Backend URL (Render)</label>
  <input id="backendUrl" type="text" placeholder="https://tu-api.onrender.com">
  <label>API Secret</label>
  <input id="apiSecret" type="password" placeholder="tu-api-secret">
  <div class="conn-btns">
    <button class="btn" onclick="saveSettings()">Guardar</button>
    <button class="btn" onclick="testConnection()">Probar</button>
    <span id="connStatus" class="status-text"></span>
  </div>
  <p class="tip">💡 Backend oculta tu API key de Kimi. Los usuarios nunca la ven.</p>
</div>

<div class="grid">
  <div class="card" onclick="openModule('cv')">
    <h3>📄 CV</h3>
    <p>Optimización ATS + IA</p>
  </div>
  <div class="card" onclick="openModule('linkedin')">
    <h3>🔗 LinkedIn</h3>
    <p>Análisis de perfil</p>
  </div>
  <div class="card" onclick="openModule('job')">
    <h3>🎯 Job Match</h3>
    <p>Candidato vs oferta</p>
  </div>
  <div class="card" onclick="openModule('freelance')">
    <h3>💼 Freelance</h3>
    <p>Proyectos rentables</p>
  </div>
  <div class="card" onclick="openModule('interview')">
    <h3>🎤 Interview</h3>
    <p>Preparación tech</p>
  </div>
</div>

<div id="cvModule" class="module">
  <h3>📄 CV Optimizer</h3>
  <p style="color:#64748b;font-size:.85rem;margin-bottom:12px">Pega tu CV y recibe diagnóstico ATS completo</p>
  <label>Nombre</label><input id="cvName" placeholder="Juan Pérez">
  <label>Email</label><input id="cvEmail" type="email" placeholder="juan@ejemplo.com">
  <label>Teléfono</label><input id="cvPhone" placeholder="+1 234 567 890">
  <label>LinkedIn</label><input id="cvLinkedin" placeholder="linkedin.com/in/tu-perfil">
  <label>Profesión</label><input id="cvProfession" placeholder="Full Stack Developer">
  <label>Industria</label>
  <select id="cvIndustry">
    <option value="general">General</option>
    <option value="tech">Tecnología</option>
    <option value="finance">Finanzas</option>
    <option value="healthcare">Salud</option>
    <option value="marketing">Marketing</option>
    <option value="design">Diseño/UX</option>
    <option value="engineering">Ingeniería</option>
  </select>
  <label>CV (texto plano)</label><textarea id="cvContent" placeholder="Pega todo tu CV aquí..."></textarea>
  <button class="btn" onclick="submit('cv')">Analizar CV →</button>
  <div id="cvResult" class="result"></div>
</div>

<div id="linkedinModule" class="module">
  <h3>🔗 LinkedIn Analyzer</h3>
  <p style="color:#64748b;font-size:.85rem;margin-bottom:12px">Headline, about section, estrategia de contenido</p>
  <label>URL perfil</label><input id="liUrl" placeholder="linkedin.com/in/tu-perfil">
  <label>Headline actual</label><input id="liTitle" placeholder="Full Stack | React | Node">
  <label>About / Bio</label><textarea id="liBio" placeholder="Tu About section..."></textarea>
  <label>Skills (separados por coma)</label><input id="liSkills" placeholder="React, Node.js, Python, AWS">
  <button class="btn" onclick="submit('linkedin')">Analizar Perfil →</button>
  <div id="linkedinResult" class="result"></div>
</div>

<div id="jobModule" class="module">
  <h3>🎯 Job Match</h3>
  <p style="color:#64748b;font-size:.85rem;margin-bottom:12px">Compara tu perfil con una oferta</p>
  <label>Título del puesto</label><input id="jobTitle" placeholder="Senior Frontend Dev">
  <label>Descripción</label><textarea id="jobDesc" placeholder="Pega la descripción de la oferta..."></textarea>
  <label>Tu perfil</label><textarea id="jobProfile" placeholder="Tu experiencia, skills, logros..."></textarea>
  <label>Interés</label>
  <select id="jobInterest">
    <option value="high">Alto — Muy interesado</option>
    <option value="medium" selected>Medio — Explorando</option>
    <option value="low">Bajo — Curiosidad</option>
  </select>
  <button class="btn" onclick="submit('job')">Analizar Match →</button>
  <div id="jobResult" class="result"></div>
</div>

<div id="freelanceModule" class="module">
  <h3>💼 Freelance Search</h3>
  <p style="color:#64748b;font-size:.85rem;margin-bottom:12px">Encuentra proyectos y nichos rentables</p>
  <label>Especialidad</label><input id="flSpecialty" placeholder="Desarrollo Web Full Stack">
  <label>Nivel</label>
  <select id="flLevel">
    <option value="junior">Junior (0-2a)</option>
    <option value="mid" selected>Mid (2-5a)</option>
    <option value="senior">Senior (5+a)</option>
    <option value="expert">Expert/Lead</option>
  </select>
  <label>Skills</label><input id="flSkills" placeholder="React, Node, MongoDB, AWS">
  <label>Tarifa esperada ($/h)</label>
  <select id="flRate">
    <option value="20-50">$20-50</option>
    <option value="50-100" selected>$50-100</option>
    <option value="100-200">$100-200</option>
    <option value="200+">$200+</option>
  </select>
  <button class="btn" onclick="submit('freelance')">Buscar Proyectos →</button>
  <div id="freelanceResult" class="result"></div>
</div>

<div id="interviewModule" class="module">
  <h3>🎤 Interview Trainer</h3>
  <p style="color:#64748b;font-size:.85rem;margin-bottom:12px">Preguntas, roleplay, pitch, negociación</p>
  <label>Puesto</label><input id="intPosition" placeholder="Senior React Dev">
  <label>Empresa (opcional)</label><input id="intCompany" placeholder="Google, Meta, startup...">
  <label>Tu perfil</label><textarea id="intProfile" placeholder="Experiencia, fortalezas..."></textarea>
  <label>Mayor desafío</label>
  <select id="intChallenge">
    <option value="general">General — Preparación completa</option>
    <option value="technical">Preguntas técnicas</option>
    <option value="behavioral">Behavioral / Cultura</option>
    <option value="negotiation">Negociación salarial</option>
    <option value="confidence">Nerviosismo / Confianza</option>
    <option value="system_design">System Design</option>
  </select>
  <button class="btn" onclick="submit('interview')">Preparar Entrevista →</button>
  <div id="interviewResult" class="result"></div>
</div>

</div>

<script>
let backendUrl = localStorage.getItem('ra_backendUrl') || '';
let apiSecret = localStorage.getItem('ra_apiSecret') || '';

function init(){
  document.getElementById('backendUrl').value = backendUrl;
  document.getElementById('apiSecret').value = apiSecret;
  if(!backendUrl || !apiSecret){
    document.getElementById('connPanel').classList.add('open');
  }
}

function toggleSettings(){
  document.getElementById('connPanel').classList.toggle('open');
}

function saveSettings(){
  backendUrl = document.getElementById('backendUrl').value.trim().replace(/\/$/, '');
  apiSecret = document.getElementById('apiSecret').value.trim();
  localStorage.setItem('ra_backendUrl', backendUrl);
  localStorage.setItem('ra_apiSecret', apiSecret);
  testConnection();
}

async function testConnection(retries = 3){
  const statusEl = document.getElementById('connStatus');
  statusEl.textContent = '⏳ Probando...';
  statusEl.style.color = '#fbbf24';
  
  for(let i = 0; i < retries; i++){
    try{
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 45000);
      const resp = await fetch(backendUrl + '/health', {
        headers: {'x-api-key': apiSecret},
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      if(resp.ok){
        const data = await resp.json();
        if(data.ok){
          statusEl.textContent = '✅ Conectado';
          statusEl.style.color = '#22c55e';
          return;
        }
      }
    } catch(e){
      if(i < retries - 1){
        statusEl.textContent = '⏳ Reintentando...';
        await new Promise(r => setTimeout(r, 3000));
        continue;
      }
    }
  }
  statusEl.textContent = '❌ No responde';
  statusEl.style.color = '#ef4444';
}

function openModule(name){
  document.querySelectorAll('.module').forEach(el => el.classList.remove('open'));
  document.getElementById(name + 'Module').classList.add('open');
  window.scrollTo(0, document.getElementById(name + 'Module').offsetTop - 10);
}

const PAYLOADS = {
  cv: () => ({
    name: document.getElementById('cvName').value,
    email: document.getElementById('cvEmail').value,
    phone: document.getElementById('cvPhone').value,
    linkedin: document.getElementById('cvLinkedin').value,
    profession: document.getElementById('cvProfession').value,
    industry: document.getElementById('cvIndustry').value,
    cv_content: document.getElementById('cvContent').value
  }),
  linkedin: () => ({
    url: document.getElementById('liUrl').value,
    title: document.getElementById('liTitle').value,
    bio: document.getElementById('liBio').value,
    skills: document.getElementById('liSkills').value
  }),
  job: () => ({
    job_title: document.getElementById('jobTitle').value,
    job_description: document.getElementById('jobDesc').value,
    user_profile: document.getElementById('jobProfile').value,
    interest: document.getElementById('jobInterest').value
  }),
  freelance: () => ({
    specialty: document.getElementById('flSpecialty').value,
    level: document.getElementById('flLevel').value,
    skills: document.getElementById('flSkills').value,
    rate_range: document.getElementById('flRate').value
  }),
  interview: () => ({
    position: document.getElementById('intPosition').value,
    company: document.getElementById('intCompany').value,
    profile: document.getElementById('intProfile').value,
    challenge: document.getElementById('intChallenge').value
  })
};

const ENDPOINTS = {
  cv: '/api/cv/optimize',
  linkedin: '/api/linkedin/analyze',
  job: '/api/job/match',
  freelance: '/api/freelance/search',
  interview: '/api/interview/prep'
};

async function submit(name, retries = 2){
  if(!backendUrl || !apiSecret){
    document.getElementById('connPanel').classList.add('open');
    return;
  }
  const resultEl = document.getElementById(name + 'Result');
  resultEl.classList.add('open');
  resultEl.classList.remove('error');
  resultEl.innerHTML = '<div class="loading">⚡ Analizando... (puede tardar 60s en primer uso)</div>';
  
  const payload = PAYLOADS[name]();
  
  for(let i = 0; i < retries; i++){
    try{
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 65000);
      const resp = await fetch(backendUrl + ENDPOINTS[name], {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'x-api-key': apiSecret},
        body: JSON.stringify(payload),
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      if(!resp.ok){
        const err = await resp.json().catch(() => ({}));
        throw new Error(err.error || 'HTTP ' + resp.status);
      }
      const data = await resp.json();
      resultEl.innerHTML = '<div class="ok">✅ Análisis completo</div>' + (data.result || data.error || JSON.stringify(data));
      resultEl.style.borderLeftColor = '#22c55e';
      return;
    } catch(e){
      if(i < retries - 1 && e.name === 'AbortError'){
        resultEl.innerHTML = '<div class="loading">⏳ Reintentando... (Render despertando)</div>';
        await new Promise(r => setTimeout(r, 5000));
        continue;
      }
      resultEl.classList.add('error');
      resultEl.innerHTML = '<div class="err">❌ Error</div>' + e.message;
    }
  }
}

init();
</script>
</body>
</html>`;

    return new Response(html, {
      headers: {
        'content-type': 'text/html;charset=UTF-8',
        'cache-control': 'public, max-age=60'
      }
    });
  }
};
