$file = "c:\Fazenda digital\fazenda_mobile.html"

$part8 = @'
<!-- ===== BOTTOM NAV ===== -->
<nav class="fixed bottom-0 left-0 right-0 max-w-md mx-auto bg-white border-t border-gray-200 px-2 py-2 z-50" id="bottom-nav" style="display:none">
  <div class="flex justify-around">
    <button onclick="showScreen('dashboard')" class="nav-item active flex flex-col items-center gap-0.5 px-3 py-1" data-screen="dashboard">
      <i class="ph-bold ph-house text-xl"></i><span class="text-[10px] font-semibold">Home</span>
    </button>
    <button onclick="showScreen('rebanho')" class="nav-item flex flex-col items-center gap-0.5 px-3 py-1" data-screen="rebanho">
      <i class="ph-bold ph-cow text-xl"></i><span class="text-[10px] font-semibold">Rebanho</span>
    </button>
    <button onclick="showScreen('manejo')" class="nav-item flex flex-col items-center gap-0.5 px-3 py-1" data-screen="manejo">
      <i class="ph-bold ph-note-pencil text-xl"></i><span class="text-[10px] font-semibold">Manejo</span>
    </button>
    <button onclick="showScreen('estoque')" class="nav-item flex flex-col items-center gap-0.5 px-3 py-1" data-screen="estoque">
      <i class="ph-bold ph-package text-xl"></i><span class="text-[10px] font-semibold">Estoque</span>
    </button>
    <button onclick="showScreen('tarefas')" class="nav-item flex flex-col items-center gap-0.5 px-3 py-1" data-screen="tarefas">
      <i class="ph-bold ph-clipboard-text text-xl"></i><span class="text-[10px] font-semibold">Tarefas</span>
    </button>
  </div>
</nav>

<!-- ===== TOAST ===== -->
<div id="toast" class="toast hidden px-5 py-3 rounded-xl shadow-lg text-white text-sm font-semibold"></div>
'@

Add-Content -Path $file -Value $part8 -Encoding UTF8

$jsBlock = @'
<script>
// ===== DATA STORE =====
let appData = JSON.parse(localStorage.getItem('fazendaData')) || null;
if(!appData) {
  appData = {
    animals: [
      { id:1, rfid:'BR-001', breed:'Nelore', fase:'engorda', weight:480, paddock:'Piquete 1', status:'active', birth:'2024-03-15', dataFase:'2025-06-01', pesoEntrada:420 },
      { id:2, rfid:'BR-002', breed:'Angus', fase:'recria', weight:350, paddock:'Piquete 2', status:'active', birth:'2024-08-20', dataFase:'2025-09-01', pesoEntrada:280 },
      { id:3, rfid:'BR-003', breed:'Brahman', fase:'cria', weight:180, paddock:'Piquete 3', status:'active', birth:'2025-07-10', dataFase:'2025-07-10', pesoEntrada:35 }
    ],
    tasks: [
      { id:1, desc:'Vacinacao Aftosa - Piquete 1', assignee:'Joao', status:'pending', priority:'alta' },
      { id:2, desc:'Pesagem Mensal do Rebanho', assignee:'Carlos', status:'pending', priority:'media' },
      { id:3, desc:'Reposicao de Sal Mineral', assignee:'Maria', status:'pending', priority:'baixa' }
    ],
    inventory: [
      { id:1, name:'Sal Mineral Premium', category:'Nutricao', qty:50, unit:'Sacos', cost:45.00 },
      { id:2, name:'Ivermectina 1%', category:'Medicamento', qty:20, unit:'Frascos', cost:28.50 },
      { id:3, name:'Racao Suplementar', category:'Nutricao', qty:100, unit:'kg', cost:3.20 }
    ],
    scores: [],
    events: [],
    nextId: 4
  };
  saveData();
}

function saveData() { localStorage.setItem('fazendaData', JSON.stringify(appData)); }

function toast(msg, type='success') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'toast px-5 py-3 rounded-xl shadow-lg text-white text-sm font-semibold ' + (type==='success'?'bg-success':type==='error'?'bg-danger':'bg-warning');
  setTimeout(() => t.className = 'toast hidden', 2500);
}

// ===== NAVIGATION =====
function showScreen(name) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  const el = document.getElementById('screen-'+name);
  if(el) el.classList.add('active');
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  const nav = document.querySelector(`.nav-item[data-screen="${name}"]`);
  if(nav) nav.classList.add('active');
  if(name==='dashboard') renderDashboard();
  if(name==='rebanho') renderRebanho();
  if(name==='manejo') renderManejoSelects();
  if(name==='estoque') renderEstoque();
  if(name==='tarefas') renderTarefas();
}

function showSubScreen(name) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById('screen-'+name).classList.add('active');
  if(name==='ciclo') renderCiclo();
}

function doLogin() {
  document.getElementById('screen-login').classList.remove('active');
  document.getElementById('bottom-nav').style.display = 'block';
  showScreen('dashboard');
}

// ===== DASHBOARD =====
function renderDashboard() {
  const active = appData.animals.filter(a => a.status === 'active');
  document.getElementById('dash-total-animals').textContent = active.length;
  document.getElementById('dash-tasks').textContent = appData.tasks.filter(t => t.status==='pending').length;
  const fasesDiv = document.getElementById('dash-fases');
  const fases = ['cria','recria','engorda','venda'];
  const colors = {cria:'bg-cria',recria:'bg-recria',engorda:'bg-engorda',venda:'bg-venda'};
  const labels = {cria:'Cria',recria:'Recria',engorda:'Engorda',venda:'Venda'};
  const icons = {cria:'ph-baby',recria:'ph-plant',engorda:'ph-hamburger',venda:'ph-currency-dollar'};
  fasesDiv.innerHTML = fases.map(f => {
    const c = active.filter(a => a.fase===f).length;
    return `<div onclick="showSubScreen('ciclo')" class="btn-press ${colors[f]} rounded-xl p-3 text-white text-center cursor-pointer"><i class="ph-bold ${icons[f]} text-lg"></i><p class="text-lg font-bold">${c}</p><p class="text-[10px] font-semibold opacity-90">${labels[f]}</p></div>`;
  }).join('');
}

// ===== REBANHO =====
let currentFilter = 'all';
function filterRebanho(f) {
  currentFilter = f;
  document.querySelectorAll('.filter-btn').forEach(b => {
    b.classList.toggle('bg-primary', b.dataset.filter===f);
    b.classList.toggle('text-white', b.dataset.filter===f);
    b.classList.toggle('bg-gray-100', b.dataset.filter!==f);
    b.classList.toggle('text-text-secondary', b.dataset.filter!==f);
  });
  renderRebanho();
}
function renderRebanho() {
  let list = appData.animals;
  if(currentFilter!=='all') list = list.filter(a => a.fase===currentFilter);
  const statusEmoji = {active:'🟢',quarantine:'🟡',sick:'🔴'};
  const faseColors = {cria:'bg-cria/20 text-cria',recria:'bg-recria/20 text-recria',engorda:'bg-engorda/20 text-engorda',venda:'bg-venda/20 text-venda'};
  const faseLabels = {cria:'Cria',recria:'Recria',engorda:'Engorda',venda:'Venda'};
  document.getElementById('rebanho-list').innerHTML = list.map((a,i) => `
    <div class="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 card-anim" style="animation-delay:${i*0.05}s">
      <div class="flex items-center justify-between mb-2">
        <div class="flex items-center gap-2">
          <span class="text-lg">${statusEmoji[a.status]||'⚪'}</span>
          <span class="font-bold text-base">${a.rfid}</span>
          <span class="fase-badge ${faseColors[a.fase]}">${faseLabels[a.fase]}</span>
        </div>
        <button onclick="deleteAnimal(${a.id})" class="btn-press w-8 h-8 rounded-lg bg-danger/10 flex items-center justify-center"><i class="ph-bold ph-trash text-danger text-sm"></i></button>
      </div>
      <div class="grid grid-cols-3 gap-2 text-center">
        <div><p class="text-xs text-text-secondary">Raca</p><p class="text-sm font-semibold">${a.breed}</p></div>
        <div><p class="text-xs text-text-secondary">Peso</p><p class="text-sm font-semibold">${a.weight} kg</p></div>
        <div><p class="text-xs text-text-secondary">Piquete</p><p class="text-sm font-semibold">${a.paddock}</p></div>
      </div>
    </div>
  `).join('') || '<p class="text-center text-text-muted py-8">Nenhum animal encontrado.</p>';
}
function cadastrarAnimal() {
  const rfid = document.getElementById('cad-rfid').value.trim();
  if(!rfid) return toast('Informe o RFID!','error');
  appData.animals.push({ id: appData.nextId++, rfid, breed: document.getElementById('cad-breed').value, fase: document.getElementById('cad-fase').value, weight: parseFloat(document.getElementById('cad-weight').value)||0, paddock: document.getElementById('cad-paddock').value, status: document.getElementById('cad-status').value, birth: document.getElementById('cad-birth').value, dataFase: new Date().toISOString().slice(0,10), pesoEntrada: parseFloat(document.getElementById('cad-weight').value)||0 });
  saveData(); toast('Animal cadastrado!'); showScreen('rebanho');
}
function deleteAnimal(id) { appData.animals = appData.animals.filter(a => a.id!==id); saveData(); renderRebanho(); toast('Animal removido.','warning'); }

// ===== MANEJO =====
function showManejoTab(tab) {
  document.getElementById('manejo-escores').style.display = tab==='escores'?'block':'none';
  document.getElementById('manejo-eventos').style.display = tab==='eventos'?'block':'none';
  document.querySelectorAll('.manejo-tab').forEach(b => {
    b.classList.toggle('bg-primary', b.dataset.tab===tab);
    b.classList.toggle('text-white', b.dataset.tab===tab);
    b.classList.toggle('bg-gray-100', b.dataset.tab!==tab);
    b.classList.toggle('text-text-secondary', b.dataset.tab!==tab);
  });
}
function renderManejoSelects() {
  const sel = document.getElementById('evt-rfid');
  sel.innerHTML = '<option value="">Selecione...</option>' + appData.animals.map(a => `<option value="${a.rfid}">${a.rfid} - ${a.breed}</option>`).join('');
}
function togglePesoEvt() { document.getElementById('evt-peso-wrap').style.display = document.getElementById('evt-type').value==='Pesagem'?'block':'none'; }
function salvarEscore() {
  appData.scores.push({ paddock: document.getElementById('esc-paddock').value, type: document.getElementById('esc-type').value, value: document.getElementById('esc-value').value, notes: document.getElementById('esc-notes').value, date: new Date().toISOString().slice(0,10) });
  saveData(); toast('Escore salvo!');
}
function registrarEvento() {
  const rfid = document.getElementById('evt-rfid').value;
  if(!rfid) return toast('Selecione um animal!','error');
  const type = document.getElementById('evt-type').value;
  const evt = { rfid, type, details: document.getElementById('evt-details').value, date: new Date().toISOString().slice(0,10) };
  if(type==='Pesagem') {
    const peso = parseFloat(document.getElementById('evt-peso').value)||0;
    evt.peso = peso;
    const animal = appData.animals.find(a => a.rfid===rfid);
    if(animal) animal.weight = peso;
  }
  appData.events.push(evt); saveData(); toast('Evento registrado!');
}

// ===== ESTOQUE =====
function renderEstoque() {
  const inv = appData.inventory;
  const total = inv.reduce((s,i) => s + i.qty * i.cost, 0);
  const low = inv.filter(i => i.qty <= 0).length;
  document.getElementById('estoque-summary').innerHTML = `
    <div class="bg-white rounded-xl p-3 text-center shadow-sm border border-gray-100"><p class="text-xs text-text-secondary">Produtos</p><p class="text-lg font-bold">${inv.length}</p></div>
    <div class="bg-white rounded-xl p-3 text-center shadow-sm border border-gray-100"><p class="text-xs text-text-secondary">Valor Total</p><p class="text-lg font-bold text-success">R$${total.toFixed(0)}</p></div>
    <div class="bg-white rounded-xl p-3 text-center shadow-sm border border-gray-100"><p class="text-xs text-text-secondary">Sem Estoque</p><p class="text-lg font-bold text-danger">${low}</p></div>`;
  document.getElementById('estoque-list').innerHTML = inv.map((item,i) => `
    <div class="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 card-anim" style="animation-delay:${i*0.05}s">
      <div class="flex justify-between items-start mb-2">
        <div><p class="font-bold">${item.name}</p><p class="text-xs text-text-secondary">${item.category}</p></div>
        <span class="text-xs font-semibold px-2 py-1 rounded-full ${item.qty>0?'bg-success/10 text-success':'bg-danger/10 text-danger'}">${item.qty} ${item.unit}</span>
      </div>
      <div class="flex items-center gap-2 mt-2">
        <button onclick="moveStock(${item.id},-1)" class="btn-press w-8 h-8 rounded-lg bg-danger/10 flex items-center justify-center"><i class="ph-bold ph-minus text-danger text-sm"></i></button>
        <div class="flex-1 bg-gray-100 rounded-full h-2"><div class="bg-primary rounded-full h-2" style="width:${Math.min(100,item.qty)}%"></div></div>
        <button onclick="moveStock(${item.id},1)" class="btn-press w-8 h-8 rounded-lg bg-success/10 flex items-center justify-center"><i class="ph-bold ph-plus text-success text-sm"></i></button>
      </div>
      <p class="text-xs text-text-muted mt-1 text-right">R$ ${item.cost.toFixed(2)} / ${item.unit}</p>
    </div>`).join('');
}
function moveStock(id,dir) {
  const item = appData.inventory.find(i => i.id===id);
  if(item) { item.qty = Math.max(0, item.qty + dir); saveData(); renderEstoque(); }
}
function cadastrarProduto() {
  const name = document.getElementById('prod-name').value.trim();
  if(!name) return toast('Informe o nome!','error');
  appData.inventory.push({ id: appData.nextId++, name, category: document.getElementById('prod-cat').value, qty: parseFloat(document.getElementById('prod-qty').value)||0, unit: document.getElementById('prod-unit').value, cost: parseFloat(document.getElementById('prod-cost').value)||0 });
  saveData(); toast('Produto cadastrado!'); showScreen('estoque');
}

// ===== TAREFAS =====
function renderTarefas() {
  const prioColors = {alta:'border-l-danger',media:'border-l-warning',baixa:'border-l-success'};
  const prioLabels = {alta:'Alta',media:'Media',baixa:'Baixa'};
  document.getElementById('tarefas-list').innerHTML = appData.tasks.map((t,i) => `
    <div class="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 border-l-4 ${prioColors[t.priority]} card-anim" style="animation-delay:${i*0.05}s">
      <div class="flex items-start justify-between">
        <div class="flex items-start gap-3">
          <button onclick="toggleTask(${t.id})" class="btn-press mt-0.5 w-6 h-6 rounded-full border-2 ${t.status==='done'?'bg-success border-success':'border-gray-300'} flex items-center justify-center">
            ${t.status==='done'?'<i class="ph-bold ph-check text-white text-xs"></i>':''}
          </button>
          <div>
            <p class="font-semibold ${t.status==='done'?'line-through text-text-muted':''}">${t.desc}</p>
            <p class="text-xs text-text-secondary mt-0.5"><i class="ph ph-user mr-1"></i>${t.assignee} · ${prioLabels[t.priority]}</p>
          </div>
        </div>
        <button onclick="deleteTask(${t.id})" class="btn-press w-8 h-8 rounded-lg bg-danger/10 flex items-center justify-center"><i class="ph-bold ph-trash text-danger text-sm"></i></button>
      </div>
    </div>`).join('');
}
function toggleTask(id) { const t = appData.tasks.find(x=>x.id===id); if(t) { t.status = t.status==='done'?'pending':'done'; saveData(); renderTarefas(); renderDashboard(); } }
function deleteTask(id) { appData.tasks = appData.tasks.filter(t=>t.id!==id); saveData(); renderTarefas(); toast('Tarefa removida.','warning'); }
function addTask() {
  const desc = document.getElementById('task-desc').value.trim();
  if(!desc) return toast('Informe a descricao!','error');
  appData.tasks.push({ id: appData.nextId++, desc, assignee: document.getElementById('task-assignee').value||'N/A', status:'pending', priority: document.getElementById('task-priority').value });
  saveData(); toast('Tarefa criada!'); showScreen('tarefas');
}

// ===== CICLO PRODUTIVO =====
function renderCiclo() {
  const fases = ['cria','recria','engorda','venda'];
  const colors = {cria:'#22C55E',recria:'#3B82F6',engorda:'#F97316',venda:'#A855F7'};
  const labels = {cria:'Cria',recria:'Recria',engorda:'Engorda',venda:'Venda'};
  const active = appData.animals.filter(a => a.status==='active');
  document.getElementById('ciclo-cards').innerHTML = fases.map(f => {
    const grupo = active.filter(a => a.fase===f);
    const pesoMed = grupo.length ? (grupo.reduce((s,a)=>s+a.weight,0)/grupo.length).toFixed(0) : 0;
    return `<div style="border-left:4px solid ${colors[f]}" class="bg-white rounded-xl p-4 shadow-sm">
      <div class="flex justify-between items-center"><span class="font-bold">${labels[f]}</span><span class="text-2xl font-bold" style="color:${colors[f]}">${grupo.length}</span></div>
      <p class="text-xs text-text-secondary mt-1">Peso medio: ${pesoMed} kg</p>
      <div class="flex flex-wrap gap-1 mt-2">${grupo.map(a=>`<span class="text-[10px] bg-gray-100 px-2 py-0.5 rounded-full">${a.rfid}</span>`).join('')}</div>
    </div>`;
  }).join('');
  const sel = document.getElementById('trans-animal');
  sel.innerHTML = '<option value="">Selecione...</option>' + active.map(a => `<option value="${a.rfid}">${a.rfid} (${labels[a.fase]})</option>`).join('');
}
function transicaoFase() {
  const rfid = document.getElementById('trans-animal').value;
  if(!rfid) return toast('Selecione um animal!','error');
  const animal = appData.animals.find(a => a.rfid===rfid);
  const novaFase = document.getElementById('trans-fase').value;
  const peso = parseFloat(document.getElementById('trans-peso').value)||animal.weight;
  animal.fase = novaFase; animal.dataFase = new Date().toISOString().slice(0,10); animal.pesoEntrada = peso; animal.weight = peso;
  appData.events.push({ rfid, type:'Transicao', details:`Para ${novaFase}`, date:new Date().toISOString().slice(0,10), peso });
  saveData(); toast('Transicao realizada!'); renderCiclo();
}

// ===== EXPORTAR EXCEL =====
function exportAllToExcel() {
  const wb = XLSX.utils.book_new();
  if(appData.animals.length) { const ws = XLSX.utils.json_to_sheet(appData.animals.map(a=>({RFID:a.rfid,Raca:a.breed,Fase:a.fase,'Peso (kg)':a.weight,Piquete:a.paddock,Status:a.status,Nascimento:a.birth}))); XLSX.utils.book_append_sheet(wb,ws,'Rebanho'); }
  if(appData.tasks.length) { const ws = XLSX.utils.json_to_sheet(appData.tasks.map(t=>({Descricao:t.desc,Responsavel:t.assignee,Status:t.status,Prioridade:t.priority}))); XLSX.utils.book_append_sheet(wb,ws,'Tarefas'); }
  if(appData.inventory.length) { const ws = XLSX.utils.json_to_sheet(appData.inventory.map(i=>({Produto:i.name,Categoria:i.category,Quantidade:i.qty,Unidade:i.unit,'Custo (R$)':i.cost,'Total (R$)':(i.qty*i.cost).toFixed(2)}))); XLSX.utils.book_append_sheet(wb,ws,'Estoque'); }
  if(appData.scores.length) { const ws = XLSX.utils.json_to_sheet(appData.scores); XLSX.utils.book_append_sheet(wb,ws,'Escores'); }
  if(appData.events.length) { const ws = XLSX.utils.json_to_sheet(appData.events); XLSX.utils.book_append_sheet(wb,ws,'Eventos'); }
  XLSX.writeFile(wb, 'Fazenda_Digital_Export.xlsx');
  toast('Excel exportado!');
}
</script>
</body>
</html>
'@

Add-Content -Path $file -Value $jsBlock -Encoding UTF8
Write-Host "HTML file complete!"
