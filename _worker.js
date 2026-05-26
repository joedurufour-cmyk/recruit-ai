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
.container{max-width:900px;margin:0 auto;padding:20px}
header{text-align:center;padding:30px 0;border-bottom:1px solid #1e293b;margin-bottom:30px}
header h1{font-size:2rem;background:linear-gradient(135deg,#00d9ff,#ff006e);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.status-dot{display:inline-block;width:10px;height:10px;border-radius:50%;background:#ef4444;margin-left:10px;cursor:pointer}
.status-dot.connected{background:#22c55e}
.connection-panel{background:#1e293b;padding:20px;border-radius:12px;margin-bottom:30px;display:none}
.connection-panel.active{display:block}
.connection-panel input{width:100%;padding:10px;margin:8px 0;background:#0f172a;border:1px solid #334155;border-radius:8px;color:#e2e8f0}
.btn{background:linear-gradient(135deg,#00d9ff,#ff006e);color:#fff;border:none;padding:10px 24px;border-radius:8px;cursor:pointer;font-weight:600;margin:5px}
.btn:hover{opacity:.9}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:15px;margin-bottom:30px}
.card{background:#1e293b;padding:20px;border-radius:12px;cursor:pointer;transition:transform .2s;border:1px solid #334155}
.card:hover{transform:translateY(-2px);border-color:#00d9ff}
.card h3{margin-bottom:8px;color:#00d9ff}
.module-form{background:#1e293b;padding:25px;border-radius:12px;display:none}
.module-form.active{display:block}
.module-form label{display:block;margin:15px 0 5px;font-size:.9rem;color:#94a3b8}
.module-form input,.module-form textarea,.module-form select{width:100%;padding:12px;background:#0f172a;border:1px solid #334155;border-radius:8px;color:#e2e8f0;font-size:1rem}
.module-form textarea{min-height:120px;resize:vertical}
.result-box{background:#0f172a;padding:20px;border-radius:8px;margin-top:20px;white-space:pre-wrap;display:none;border-left:3px solid #00d9ff}
.result-box.active{display:block}
.loading{text-align:center;padding:40px;color:#64748b}
.error{background:#450a0a;border-left-color:#ef4444;color:#fca5a5}
</style>
</head>
<body>
<div class="container">
<header>
<h1>⚡ RecruitAI</h1>
<p>Suite de Reclutamiento con IA</p>
</header>

<div id="connectionPanel" class="connection-panel">
<h3 style="margin-bottom:15px">⚙️ Conexión Backend</h3>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:15px">
<div>
<label>Backend URL (Render)</label>
<input id="backendUrl" type="text" placeholder="https://tu-api.onrender.com">
</div>
<div>
<label>API Secret</label>
<input id="apiSecret" type="password" placeholder="tu-api-secret">
</div>
</div>
<div style="margin-top:15px">
<button class="btn" onclick="saveSettings()">Guardar</button>
<button class="btn" onclick="testConnection()">Probar Conexión</button>
<span id="connStatus" style="margin-left:15px"></span>
</div>
<p style="margin-top:10px;font-size:.85rem;color:#64748b">💡 El backend oculta tu API key de Kimi. Los usuarios finales nunca la ven.</p>
</div>

<div class="grid">
<div class="card" onclick="showModule('cv')">
<h3>📄 CV</h3>
<p>Optimización ATS + análisis con IA</p>
</div>
<div class="card" onclick="showModule('linkedin')">
<h3>🔗 LinkedIn</h3>
<p>Análisis y optimización de perfil</p>
</div>
<div class="card" onclick="showModule('job')">
<h3>🎯 Job Match</h3>
<p>Compatibilidad candidato vs oferta</p>
</div>
<div class="card" onclick="showModule('freelance')">
<h3>💼 Freelance</h3>
<p>Búsqueda de proyectos rentables</p>
</div>
<div class="card" onclick="showModule('interview')">
<h3>🎤 Interview</h3>
<p>Preparación para entrevistas tech</p>
</div>
</div>

<div id="cvForm" class="module-form">
<h3>📄 CV Optimizer</h3>
<p style="margin-bottom:15px;color:#64748b">Análisis ATS + optimización con IA. Pega tu CV y recibe un diagnóstico completo.</p>
<label>Nombre completo</label><input id="cvName" placeholder="Juan Pérez">
<label>Email</label><input id="cvEmail" placeholder="juan@ejemplo.com" type="email">
<label>Teléfono</label><input id="cvPhone" placeholder="+1 234 567 890">
<label>LinkedIn URL</label><input id="cvLinkedin" placeholder="https://linkedin.com/in/tu-perfil">
<label>Profesión / Título</label><input id="cvProfession" placeholder="Full Stack Developer">
<label>Industria</label>
<select id="cvIndustry">
<option value="general">General</option>
<option value="tech">Tecnología / Software</option>
<option value="finance">Finanzas / Banca</option>
<option value="healthcare">Salud / Healthcare</option>
<option value="marketing">Marketing / Digital</option>
<option value="education">Educación</option>
<option value="design">Diseño / UX/UI</option>
<option value="engineering">Ingeniería</option>
</select>
<label>Pega tu CV aquí (texto plano)</label><textarea id="cvContent" placeholder="Pega todo el contenido de tu CV..."></textarea>
<button class="btn" onclick="submitModule('cv')">Analizar CV →</button>
<div id="cvResult" class="result-box"></div>
</div>

<div id="linkedinForm" class="module-form">
<h3>🔗 LinkedIn Analyzer</h3>
<p style="margin-bottom:15px;color:#64748b">Análisis de perfil, headline mejorado, estrategia de contenido.</p>
<label>URL de perfil</label><input id="liUrl" placeholder="https://linkedin.com/in/tu-perfil">
<label>Headline actual</label><input id="liTitle" placeholder="Full Stack Developer | React | Node.js">
<label>About / Bio</label><textarea id="liBio" placeholder="Pega tu About section actual..."></textarea>
<label>Skills (separados por coma)</label><input id="liSkills" placeholder="JavaScript, React, Node.js, Python, AWS">
<button class="btn" onclick="submitModule('linkedin')">Analizar Perfil →</button>
<div id="linkedinResult" class="result-box"></div>
</div>

<div id="jobForm" class="module-form">
<h3>🎯 Job Match</h3>
<p style="margin-bottom:15px;color:#64748b">Compara tu perfil con una oferta y recibe recomendaciones claras.</p>
<label>Título del puesto</label><input id="jobTitle" placeholder="Senior Frontend Developer">
<label>Descripción del puesto</label><textarea id="jobDesc" placeholder="Pega la descripción completa de la oferta..."></textarea>
<label>Tu perfil / experiencia</label><textarea id="jobProfile" placeholder="Describe tu experiencia, skills, logros..."></textarea>
<label>Interés en aplicar</label>
<select id="jobInterest">
<option value="high">Alto — Muy interesado</option>
<option value="medium" selected>Medio — Explorando</option>
<option value="low">Bajo — Solo curiosidad</option>
</select>
<button class="btn" onclick="submitModule('job')">Analizar Match →</button>
<div id="jobResult" class="result-box"></div>
</div>

<div id="freelanceForm" class="module-form">
<h3>💼 Freelance Search</h3>
<p style="margin-bottom:15px;color:#64748b">Encuentra proyectos rentables y estrategia de diferenciación.</p>
<label>Especialidad</label><input id="flSpecialty" placeholder="Desarrollo Web Full Stack">
<label>Nivel de experiencia</label>
<select id="flLevel">
<option value="junior">Junior (0-2 años)</option>
<option value="mid" selected>Mid (2-5 años)</option>
<option value="senior">Senior (5+ años)</option>
<option value="expert">Expert / Lead</option>
</select>
<label>Skills principales</label><input id="flSkills" placeholder="React, Node.js, MongoDB, AWS">
<label>Rango de tarifa esperada ($/hora)</label>
<select id="flRate">
<option value="20-50">$20-50 (Entry)</option>
<option value="50-100" selected>$50-100 (Mid)</option>
<option value="100-200">$100-200 (Senior)</option>
<option value="200+">$200+ (Expert)</option>
</select>
<button class="btn" onclick="submitModule('freelance')">Buscar Proyectos →</button>
<div id="freelanceResult" class="result-box"></div>
</div>

<div id="interviewForm" class="module-form">
<h3>🎤 Interview Trainer</h3>
<p style="margin-bottom:15px;color:#64748b">Preparación completa: preguntas, roleplay, pitch, negociación.</p>
<label>Puesto al que aplicas</label><input id="intPosition" placeholder="Senior React Developer">
<label>Empresa (opcional)</label><input id="intCompany" placeholder="Google, Meta, startup...">
<label>Tu perfil resumido</label><textarea id="intProfile" placeholder="Experiencia, fortalezas, contexto..."></textarea>
<label>Mayor desafío o preocupación</label>
<select id="intChallenge">
<option value="general">General — Quiero preparación completa</option>
<option value="technical">Preguntas técnicas difíciles</option>
<option value="behavioral">Behavioral / Cultura</option>
<option value="negotiation">Negociación salarial</option>
<option value="confidence">Falta de confianza / Nerviosismo</option>
<option value="system_design">System Design</option>
</select>
<button class="btn" onclick="submitModule('interview')">Preparar Entrevista →</button>
<div id="interviewResult" class="result-box"></div>
</div>

</div>
<script>
let backendUrl = localStorage.getItem('ra_backendUrl') || '';
let apiSecret = localStorage.getItem('ra_apiSecret') || '';

function init(){
  document.getElementById('backendUrl').value = backendUrl;
  document.getElementById('apiSecret').value = apiSecret;
  if(!backendUrl || !apiSecret){
    document.getElementById('connectionPanel').classList.add('active');
  } else {
    testConnection();
  }
}

function saveSettings(){
  backendUrl = document.getElementById('backendUrl').value.trim();
  apiSecret = document.getElementById('apiSecret').value.trim();
  localStorage.setItem('ra_backendUrl', backendUrl);
  localStorage.setItem('ra_apiSecret', apiSecret);
  testConnection();
}

async function testConnection(retries = 3){
  const statusEl = document.getElementById('connStatus');
  statusEl.innerHTML = '<span style="color:#fbbf24">⏳ Probando...</span>';
  
  for(let i = 0; i < retries; i++){
    try{
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 45000); // 45s timeout para cold start de Render
      
      const resp = await fetch(backendUrl + '/health', {
        method: 'GET',
        headers: {'x-api-key': apiSecret},
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      
      if(resp.ok){
        const data = await resp.json();
        if(data.ok){
          statusEl.innerHTML = '<span style="color:#22c55e">✅ Conectado</span>';
          document.querySelector('.status-dot').classList.add('connected');
          setTimeout(() => document.getElementById('connectionPanel').classList.remove('active'), 1000);
          return;
        }
      }
    } catch(e){
      if(i < retries - 1){
        statusEl.innerHTML = '<span style="color:#fbbf24">⏳ Reintentando (' + (i+1) + '/' + retries + ')...</span>';
        await new Promise(r => setTimeout(r, 3000)); // Esperar 3s antes de reintentar
        continue;
      }
    }
  }
  
  statusEl.innerHTML = '<span style="color:#ef4444">❌ No responde. Revisa URL y API Secret.</span>';
  document.querySelector('.status-dot').classList.remove('connected');
}

function showModule(name){
  document.querySelectorAll('.module-form').forEach(el => el.classList.remove('active'));
  document.getElementById(name + 'Form').classList.add('active');
  window.scrollTo(0, document.getElementById(name + 'Form').offsetTop - 20);
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

async function submitModule(name, retries = 2){
  if(!backendUrl || !apiSecret){
    document.getElementById('connectionPanel').classList.add('active');
    return;
  }
  
  const resultEl = document.getElementById(name + 'Result');
  resultEl.classList.add('active');
  resultEl.classList.remove('error');
  resultEl.innerHTML = '<div class="loading">⚡ Analizando con IA... (puede tardar hasta 60 segundos en el primer uso)</div>';
  
  const payload = PAYLOADS[name]();
  
  for(let i = 0; i < retries; i++){
    try{
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 65000); // 65s timeout total
      
      const resp = await fetch(backendUrl + ENDPOINTS[name], {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': apiSecret
        },
        body: JSON.stringify(payload),
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      
      if(!resp.ok){
        const err = await resp.json().catch(() => ({}));
        throw new Error(err.error || 'HTTP ' + resp.status);
      }
      
      const data = await resp.json();
      resultEl.innerHTML = '<div style="color:#22c55e;font-weight:600;margin-bottom:10px">✅ Análisis completo</div>' + (data.result || data.error || JSON.stringify(data));
      resultEl.style.borderLeftColor = '#22c55e';
      return;
    } catch(e){
      if(i < retries - 1 && e.name === 'AbortError'){
        resultEl.innerHTML = '<div class="loading">⏳ Reintentando... (Render se está despertando, espera 30s más)</div>';
        await new Promise(r => setTimeout(r, 5000));
        continue;
      }
      resultEl.classList.add('error');
      resultEl.innerHTML = '<div style="color:#ef4444;font-weight:600">❌ Error</div>' + e.message;
      resultEl.style.borderLeftColor = '#ef4444';
    }
  }
}

// Toggle settings panel
document.querySelector('.status-dot').addEventListener('click', () => {
  document.getElementById('connectionPanel').classList.toggle('active');
});

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
