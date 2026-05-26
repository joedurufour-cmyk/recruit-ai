export default {
  async fetch(request, env) {
    return new Response(`<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RecruitAI</title>
<style>
body{font-family:sans-serif;background:#0a0e1a;color:#e2e8f0;margin:0;padding:16px;max-width:800px;margin:0 auto}
.header{text-align:center;padding:20px;border-bottom:1px solid #334155;margin-bottom:20px;position:relative}
.header h1{margin:0;background:linear-gradient(135deg,#00d9ff,#ff006e);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.settings{position:absolute;top:10px;right:10px;background:#1e293b;border:1px solid #334155;border-radius:8px;padding:8px 12px;cursor:pointer;color:#fff;font-size:1rem}
.panel{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:16px;margin-bottom:20px;display:none}
.panel.show{display:block}
.panel input{width:100%;padding:10px;margin:8px 0;background:#0f172a;border:1px solid #334155;border-radius:8px;color:#fff;font-size:1rem}
.btn{background:linear-gradient(135deg,#00d9ff,#ff006e);color:#fff;border:none;padding:10px 20px;border-radius:8px;cursor:pointer;font-weight:600;margin:4px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:20px}
.card{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:16px;cursor:pointer}
.card h3{color:#00d9ff;margin:0 0 6px}
.card p{color:#94a3b8;margin:0;font-size:.85rem}
.form{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:16px;margin-bottom:16px;display:none}
.form.show{display:block}
.form label{display:block;margin:10px 0 4px;font-size:.85rem;color:#94a3b8}
.form input,.form textarea,.form select{width:100%;padding:10px;background:#0f172a;border:1px solid #334155;border-radius:8px;color:#fff;font-size:1rem}
.form textarea{min-height:80px}
.result{background:#0f172a;border-left:3px solid #00d9ff;border-radius:8px;padding:12px;margin-top:12px;display:none;white-space:pre-wrap;font-size:.9rem}
.result.show{display:block}
.result.err{border-left-color:#ef4444;color:#fca5a5}
</style>
</head>
<body>

<div class="header">
  <h1>⚡ RecruitAI</h1>
  <p>Suite de Reclutamiento con IA</p>
  <button class="settings" onclick="toggle()">⚙️</button>
</div>

<div id="panel" class="panel">
  <h3 style="color:#00d9ff;margin-top:0">Conexión Backend</h3>
  <label style="font-size:.85rem;color:#94a3b8">Backend URL (Render)</label>
  <input id="url" placeholder="https://tu-api.onrender.com">
  <label style="font-size:.85rem;color:#94a3b8">API Secret</label>
  <input id="secret" type="password" placeholder="tu-api-secret">
  <div style="margin-top:10px">
    <button class="btn" onclick="save()">Guardar</button>
    <button class="btn" onclick="test()">Probar</button>
    <span id="status" style="margin-left:8px;font-size:.85rem"></span>
  </div>
  <p style="font-size:.8rem;color:#64748b;margin-top:8px">Backend oculta tu API key de Kimi</p>
</div>

<div class="grid">
  <div class="card" onclick="show('cv')">
    <h3>📄 CV</h3>
    <p>Optimización ATS + IA</p>
  </div>
  <div class="card" onclick="show('linkedin')">
    <h3>🔗 LinkedIn</h3>
    <p>Análisis de perfil</p>
  </div>
  <div class="card" onclick="show('job')">
    <h3>🎯 Job Match</h3>
    <p>Candidato vs oferta</p>
  </div>
  <div class="card" onclick="show('freelance')">
    <h3>💼 Freelance</h3>
    <p>Proyectos rentables</p>
  </div>
  <div class="card" onclick="show('interview')">
    <h3>🎤 Interview</h3>
    <p>Preparación tech</p>
  </div>
</div>

<div id="cvForm" class="form">
  <h3 style="color:#00d9ff;margin-top:0">📄 CV Optimizer</h3>
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
  <label>CV (texto plano)</label>
  <textarea id="cvContent" placeholder="Pega tu CV aquí..."></textarea>
  <button class="btn" onclick="go('cv')">Analizar CV →</button>
  <div id="cvResult" class="result"></div>
</div>

<div id="linkedinForm" class="form">
  <h3 style="color:#00d9ff;margin-top:0">🔗 LinkedIn Analyzer</h3>
  <label>URL perfil</label><input id="liUrl" placeholder="linkedin.com/in/tu-perfil">
  <label>Headline</label><input id="liTitle" placeholder="Full Stack | React | Node">
  <label>About</label><textarea id="liBio" placeholder="Tu About section..."></textarea>
  <label>Skills</label><input id="liSkills" placeholder="React, Node.js, Python, AWS">
  <button class="btn" onclick="go('linkedin')">Analizar Perfil →</button>
  <div id="linkedinResult" class="result"></div>
</div>

<div id="jobForm" class="form">
  <h3 style="color:#00d9ff;margin-top:0">🎯 Job Match</h3>
  <label>Título puesto</label><input id="jobTitle" placeholder="Senior Frontend Dev">
  <label>Descripción</label><textarea id="jobDesc" placeholder="Descripción de la oferta..."></textarea>
  <label>Tu perfil</label><textarea id="jobProfile" placeholder="Tu experiencia, skills..."></textarea>
  <label>Interés</label>
  <select id="jobInterest">
    <option value="high">Alto</option>
    <option value="medium" selected>Medio</option>
    <option value="low">Bajo</option>
  </select>
  <button class="btn" onclick="go('job')">Analizar Match →</button>
  <div id="jobResult" class="result"></div>
</div>

<div id="freelanceForm" class="form">
  <h3 style="color:#00d9ff;margin-top:0">💼 Freelance Search</h3>
  <label>Especialidad</label><input id="flSpecialty" placeholder="Desarrollo Web Full Stack">
  <label>Nivel</label>
  <select id="flLevel">
    <option value="junior">Junior (0-2a)</option>
    <option value="mid" selected>Mid (2-5a)</option>
    <option value="senior">Senior (5+a)</option>
    <option value="expert">Expert</option>
  </select>
  <label>Skills</label><input id="flSkills" placeholder="React, Node, MongoDB, AWS">
  <label>Tarifa $/h</label>
  <select id="flRate">
    <option value="20-50">$20-50</option>
    <option value="50-100" selected>$50-100</option>
    <option value="100-200">$100-200</option>
    <option value="200+">$200+</option>
  </select>
  <button class="btn" onclick="go('freelance')">Buscar Proyectos →</button>
  <div id="freelanceResult" class="result"></div>
</div>

<div id="interviewForm" class="form">
  <h3 style="color:#00d9ff;margin-top:0">🎤 Interview Trainer</h3>
  <label>Puesto</label><input id="intPosition" placeholder="Senior React Dev">
  <label>Empresa</label><input id="intCompany" placeholder="Google, Meta, startup...">
  <label>Tu perfil</label><textarea id="intProfile" placeholder="Experiencia, fortalezas..."></textarea>
  <label>Desafío</label>
  <select id="intChallenge">
    <option value="general">General</option>
    <option value="technical">Preguntas técnicas</option>
    <option value="behavioral">Behavioral / Cultura</option>
    <option value="negotiation">Negociación salarial</option>
    <option value="confidence">Nerviosismo</option>
    <option value="system_design">System Design</option>
  </select>
  <button class="btn" onclick="go('interview')">Preparar Entrevista →</button>
  <div id="interviewResult" class="result"></div>
</div>

<script>
let backendUrl = localStorage.getItem('ra_url') || '';
let apiSecret = localStorage.getItem('ra_secret') || '';

document.getElementById('url').value = backendUrl;
document.getElementById('secret').value = apiSecret;

function toggle(){
  var p = document.getElementById('panel');
  p.classList.toggle('show');
}

function save(){
  backendUrl = document.getElementById('url').value.trim().replace(/\/$/, '');
  apiSecret = document.getElementById('secret').value.trim();
  localStorage.setItem('ra_url', backendUrl);
  localStorage.setItem('ra_secret', apiSecret);
  test();
}

async function test(){
  var s = document.getElementById('status');
  s.textContent = '⏳';
  s.style.color = '#fbbf24';
  try{
    var r = await fetch(backendUrl + '/health', {
      headers: {'x-api-key': apiSecret},
      signal: AbortSignal.timeout(45000)
    });
    if(r.ok && (await r.json()).ok){
      s.textContent = '✅';
      s.style.color = '#22c55e';
    } else {
      throw new Error('no');
    }
  } catch(e){
    s.textContent = '❌';
    s.style.color = '#ef4444';
  }
}

function show(name){
  var forms = document.querySelectorAll('.form');
  for(var i = 0; i < forms.length; i++) forms[i].classList.remove('show');
  document.getElementById(name + 'Form').classList.add('show');
  document.getElementById(name + 'Form').scrollIntoView({behavior:'smooth', block:'start'});
}

var PAYLOADS = {
  cv: function(){ return {
    name: document.getElementById('cvName').value,
    email: document.getElementById('cvEmail').value,
    phone: document.getElementById('cvPhone').value,
    linkedin: document.getElementById('cvLinkedin').value,
    profession: document.getElementById('cvProfession').value,
    industry: document.getElementById('cvIndustry').value,
    cv_content: document.getElementById('cvContent').value
  };},
  linkedin: function(){ return {
    url: document.getElementById('liUrl').value,
    title: document.getElementById('liTitle').value,
    bio: document.getElementById('liBio').value,
    skills: document.getElementById('liSkills').value
  };},
  job: function(){ return {
    job_title: document.getElementById('jobTitle').value,
    job_description: document.getElementById('jobDesc').value,
    user_profile: document.getElementById('jobProfile').value,
    interest: document.getElementById('jobInterest').value
  };},
  freelance: function(){ return {
    specialty: document.getElementById('flSpecialty').value,
    level: document.getElementById('flLevel').value,
    skills: document.getElementById('flSkills').value,
    rate_range: document.getElementById('flRate').value
  };},
  interview: function(){ return {
    position: document.getElementById('intPosition').value,
    company: document.getElementById('intCompany').value,
    profile: document.getElementById('intProfile').value,
    challenge: document.getElementById('intChallenge').value
  };}
};

var ENDPOINTS = {
  cv: '/api/cv/optimize',
  linkedin: '/api/linkedin/analyze',
  job: '/api/job/match',
  freelance: '/api/freelance/search',
  interview: '/api/interview/prep'
};

async function go(name){
  if(!backendUrl || !apiSecret){
    document.getElementById('panel').classList.add('show');
    return;
  }
  var result = document.getElementById(name + 'Result');
  result.classList.add('show');
  result.classList.remove('err');
  result.textContent = '⚡ Analizando... (puede tardar 60s)';
  try{
    var r = await fetch(backendUrl + ENDPOINTS[name], {
      method: 'POST',
      headers: {'Content-Type': 'application/json', 'x-api-key': apiSecret},
      body: JSON.stringify(PAYLOADS[name]()),
      signal: AbortSignal.timeout(65000)
    });
    if(!r.ok) throw new Error('HTTP ' + r.status);
    var data = await r.json();
    result.innerHTML = '<div style="color:#22c55e;font-weight:600;margin-bottom:8px">✅ Análisis completo</div>' + (data.result || JSON.stringify(data));
    result.style.borderLeftColor = '#22c55e';
  } catch(e){
    result.classList.add('err');
    result.innerHTML = '<div style="color:#ef4444;font-weight:600;margin-bottom:8px">❌ Error</div>' + e.message;
  }
}
</script>
</body>
</html>`, {
      headers: {'content-type': 'text/html;charset=UTF-8'}
    });
  }
};
