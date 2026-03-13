$file = "c:\Fazenda digital\fazenda_mobile.html"

$part1 = @'
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Gestao de Fazenda de Gado</title>
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://unpkg.com/@phosphor-icons/web@2.0.3"></script>
<script src="https://cdn.sheetjs.com/xlsx-0.20.1/package/dist/xlsx.full.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<script>
tailwind.config = {
  theme: {
    extend: {
      fontFamily: { sans: ['Inter', 'sans-serif'] },
      colors: {
        primary: '#2563EB',
        'primary-dark': '#1D4ED8',
        'primary-light': '#3B82F6',
        surface: '#F2F4F7',
        'surface-card': '#FFFFFF',
        'text-primary': '#1E293B',
        'text-secondary': '#64748B',
        'text-muted': '#94A3B8',
        success: '#10B981',
        warning: '#F59E0B',
        danger: '#EF4444',
        cria: '#22C55E',
        recria: '#3B82F6',
        engorda: '#F97316',
        venda: '#A855F7',
      }
    }
  }
}
</script>
<style>
* { -webkit-tap-highlight-color: transparent; }
body { font-family: 'Inter', sans-serif; background: #F2F4F7; overscroll-behavior: none; }
.screen { display: none; animation: fadeIn 0.3s ease; }
.screen.active { display: block; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
@keyframes slideUp { from { opacity: 0; transform: translateY(40px); } to { opacity: 1; transform: translateY(0); } }
@keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.05); } }
.card-anim { animation: slideUp 0.4s ease forwards; opacity: 0; }
.card-anim:nth-child(1) { animation-delay: 0.05s; }
.card-anim:nth-child(2) { animation-delay: 0.1s; }
.card-anim:nth-child(3) { animation-delay: 0.15s; }
.card-anim:nth-child(4) { animation-delay: 0.2s; }
.btn-press { transition: transform 0.15s; }
.btn-press:active { transform: scale(0.95); }
.nav-item { transition: all 0.2s; }
.nav-item.active i, .nav-item.active span { color: #2563EB; }
input, select, textarea { font-size: 16px !important; }
.toast { position: fixed; top: 20px; left: 50%; transform: translateX(-50%); z-index: 9999; animation: slideDown 0.3s ease; }
@keyframes slideDown { from { opacity: 0; transform: translate(-50%, -20px); } to { opacity: 1; transform: translate(-50%, 0); } }
.metric-card { background: linear-gradient(135deg, #fff 0%, #f8fafc 100%); }
.fase-badge { display: inline-flex; align-items: center; gap: 4px; padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; }
::-webkit-scrollbar { width: 0; }
</style>
</head>
<body class="bg-surface text-text-primary max-w-md mx-auto min-h-screen relative pb-20">
'@

Set-Content -Path $file -Value $part1 -Encoding UTF8

$part2 = @'
<!-- ===== LOGIN SCREEN ===== -->
<div id="screen-login" class="screen active min-h-screen flex flex-col items-center justify-center px-6">
  <div class="text-center mb-10 animate-pulse">
    <div class="w-24 h-24 bg-primary rounded-3xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-primary/30">
      <i class="ph-bold ph-cow text-white text-5xl"></i>
    </div>
    <h1 class="text-2xl font-bold text-text-primary">Fazenda Digital</h1>
    <p class="text-text-secondary text-sm mt-1">Gestao Inteligente de Gado</p>
  </div>
  <div class="w-full space-y-4">
    <div>
      <label class="text-xs font-semibold text-text-secondary uppercase tracking-wider">Usuario</label>
      <input id="login-user" type="text" value="admin" class="w-full mt-1 px-4 py-3 bg-white rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all">
    </div>
    <div>
      <label class="text-xs font-semibold text-text-secondary uppercase tracking-wider">Senha</label>
      <input id="login-pass" type="password" value="1234" class="w-full mt-1 px-4 py-3 bg-white rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all">
    </div>
    <button onclick="doLogin()" class="btn-press w-full py-3.5 bg-primary text-white font-semibold rounded-xl shadow-lg shadow-primary/30 hover:bg-primary-dark transition-all">
      Entrar
    </button>
  </div>
  <p class="text-text-muted text-xs mt-8">&copy; 2026 Fazenda Digital</p>
</div>
'@

Add-Content -Path $file -Value $part2 -Encoding UTF8

$part3 = @'
<!-- ===== DASHBOARD ===== -->
<div id="screen-dashboard" class="screen px-4 pt-4">
  <div class="flex items-center justify-between mb-5">
    <div>
      <p class="text-text-secondary text-sm">Bem-vindo,</p>
      <h2 class="text-xl font-bold">Fazenda Digital</h2>
    </div>
    <button onclick="exportAllToExcel()" class="btn-press w-10 h-10 bg-success/10 rounded-xl flex items-center justify-center" title="Exportar Excel">
      <i class="ph-bold ph-file-xls text-success text-xl"></i>
    </button>
  </div>
  <div class="grid grid-cols-2 gap-3 mb-5">
    <div class="metric-card rounded-2xl p-4 shadow-sm border border-gray-100 card-anim">
      <div class="flex items-center gap-2 mb-2"><div class="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center"><i class="ph-bold ph-cow text-primary"></i></div><span class="text-xs text-text-secondary">Cabecas</span></div>
      <p class="text-2xl font-bold" id="dash-total-animals">0</p>
      <p class="text-xs text-success font-medium">+2 esta semana</p>
    </div>
    <div class="metric-card rounded-2xl p-4 shadow-sm border border-gray-100 card-anim">
      <div class="flex items-center gap-2 mb-2"><div class="w-8 h-8 bg-success/10 rounded-lg flex items-center justify-center"><i class="ph-bold ph-chart-line-up text-success"></i></div><span class="text-xs text-text-secondary">GMD Medio</span></div>
      <p class="text-2xl font-bold">0.85<span class="text-sm font-normal text-text-secondary"> kg/d</span></p>
      <p class="text-xs text-success font-medium">+0.05</p>
    </div>
    <div class="metric-card rounded-2xl p-4 shadow-sm border border-gray-100 card-anim">
      <div class="flex items-center gap-2 mb-2"><div class="w-8 h-8 bg-warning/10 rounded-lg flex items-center justify-center"><i class="ph-bold ph-map-pin text-warning"></i></div><span class="text-xs text-text-secondary">Piquetes</span></div>
      <p class="text-2xl font-bold" id="dash-paddocks">3</p>
      <p class="text-xs text-primary font-medium">100% uso</p>
    </div>
    <div class="metric-card rounded-2xl p-4 shadow-sm border border-gray-100 card-anim">
      <div class="flex items-center gap-2 mb-2"><div class="w-8 h-8 bg-danger/10 rounded-lg flex items-center justify-center"><i class="ph-bold ph-clipboard-text text-danger"></i></div><span class="text-xs text-text-secondary">Tarefas</span></div>
      <p class="text-2xl font-bold" id="dash-tasks">0</p>
      <p class="text-xs text-danger font-medium">pendentes</p>
    </div>
  </div>
  <h3 class="font-semibold text-sm mb-2">Alertas</h3>
  <div class="space-y-2 mb-5">
    <div class="bg-warning/10 border border-warning/20 rounded-xl px-4 py-3 flex items-start gap-3 card-anim">
      <i class="ph-bold ph-warning text-warning mt-0.5"></i><p class="text-sm">Piquete 2: Escore de Pasto Baixo (3.0)</p>
    </div>
    <div class="bg-danger/10 border border-danger/20 rounded-xl px-4 py-3 flex items-start gap-3 card-anim">
      <i class="ph-bold ph-warning-octagon text-danger mt-0.5"></i><p class="text-sm">Animal BR-001: Perda de Peso Brusca (-5kg)</p>
    </div>
    <div class="bg-primary/10 border border-primary/20 rounded-xl px-4 py-3 flex items-start gap-3 card-anim">
      <i class="ph-bold ph-info text-primary mt-0.5"></i><p class="text-sm">Campanha de Vacinacao Aftosa em 10 dias</p>
    </div>
  </div>
  <h3 class="font-semibold text-sm mb-2">Ciclo Produtivo</h3>
  <div class="grid grid-cols-4 gap-2 mb-5" id="dash-fases"></div>
</div>
'@

Add-Content -Path $file -Value $part3 -Encoding UTF8

$part4 = @'
<!-- ===== REBANHO ===== -->
<div id="screen-rebanho" class="screen px-4 pt-4">
  <div class="flex items-center justify-between mb-4">
    <h2 class="text-xl font-bold">Rebanho</h2>
    <button onclick="showSubScreen('cadastro')" class="btn-press bg-primary text-white px-4 py-2 rounded-xl text-sm font-semibold shadow-md shadow-primary/20">
      <i class="ph-bold ph-plus mr-1"></i>Novo
    </button>
  </div>
  <div class="flex gap-2 mb-4 overflow-x-auto pb-1">
    <button onclick="filterRebanho('all')" class="filter-btn btn-press px-3 py-1.5 rounded-full text-xs font-semibold bg-primary text-white" data-filter="all">Todos</button>
    <button onclick="filterRebanho('cria')" class="filter-btn btn-press px-3 py-1.5 rounded-full text-xs font-semibold bg-gray-100 text-text-secondary" data-filter="cria">Cria</button>
    <button onclick="filterRebanho('recria')" class="filter-btn btn-press px-3 py-1.5 rounded-full text-xs font-semibold bg-gray-100 text-text-secondary" data-filter="recria">Recria</button>
    <button onclick="filterRebanho('engorda')" class="filter-btn btn-press px-3 py-1.5 rounded-full text-xs font-semibold bg-gray-100 text-text-secondary" data-filter="engorda">Engorda</button>
    <button onclick="filterRebanho('venda')" class="filter-btn btn-press px-3 py-1.5 rounded-full text-xs font-semibold bg-gray-100 text-text-secondary" data-filter="venda">Venda</button>
  </div>
  <div id="rebanho-list" class="space-y-3"></div>
</div>

<!-- ===== CADASTRO ANIMAL ===== -->
<div id="screen-cadastro" class="screen px-4 pt-4">
  <div class="flex items-center gap-3 mb-5">
    <button onclick="showScreen('rebanho')" class="btn-press w-10 h-10 bg-gray-100 rounded-xl flex items-center justify-center"><i class="ph-bold ph-arrow-left text-lg"></i></button>
    <h2 class="text-xl font-bold">Cadastrar Animal</h2>
  </div>
  <div class="space-y-4">
    <div><label class="text-xs font-semibold text-text-secondary uppercase tracking-wider">RFID / Brinco</label><input id="cad-rfid" type="text" placeholder="Ex: BR-004" class="w-full mt-1 px-4 py-3 bg-white rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none"></div>
    <div><label class="text-xs font-semibold text-text-secondary uppercase tracking-wider">Raca</label>
      <select id="cad-breed" class="w-full mt-1 px-4 py-3 bg-white rounded-xl border border-gray-200 focus:border-primary outline-none"><option>Nelore</option><option>Angus</option><option>Brahman</option><option>Hereford</option><option>Cruzado</option></select></div>
    <div class="grid grid-cols-2 gap-3">
      <div><label class="text-xs font-semibold text-text-secondary uppercase tracking-wider">Fase</label>
        <select id="cad-fase" class="w-full mt-1 px-4 py-3 bg-white rounded-xl border border-gray-200 focus:border-primary outline-none"><option value="cria">Cria</option><option value="recria">Recria</option><option value="engorda">Engorda</option></select></div>
      <div><label class="text-xs font-semibold text-text-secondary uppercase tracking-wider">Peso (kg)</label><input id="cad-weight" type="number" step="0.1" placeholder="0.0" class="w-full mt-1 px-4 py-3 bg-white rounded-xl border border-gray-200 focus:border-primary outline-none"></div>
    </div>
    <div class="grid grid-cols-2 gap-3">
      <div><label class="text-xs font-semibold text-text-secondary uppercase tracking-wider">Piquete</label>
        <select id="cad-paddock" class="w-full mt-1 px-4 py-3 bg-white rounded-xl border border-gray-200 focus:border-primary outline-none"><option>Piquete 1</option><option>Piquete 2</option><option>Piquete 3</option></select></div>
      <div><label class="text-xs font-semibold text-text-secondary uppercase tracking-wider">Status</label>
        <select id="cad-status" class="w-full mt-1 px-4 py-3 bg-white rounded-xl border border-gray-200 focus:border-primary outline-none"><option value="active">Ativo</option><option value="quarantine">Quarentena</option><option value="sick">Doente</option></select></div>
    </div>
    <div><label class="text-xs font-semibold text-text-secondary uppercase tracking-wider">Data Nascimento</label><input id="cad-birth" type="date" class="w-full mt-1 px-4 py-3 bg-white rounded-xl border border-gray-200 focus:border-primary outline-none"></div>
    <button onclick="cadastrarAnimal()" class="btn-press w-full py-3.5 bg-primary text-white font-semibold rounded-xl shadow-lg shadow-primary/30 mt-2">Cadastrar Animal</button>
  </div>
</div>
'@

Add-Content -Path $file -Value $part4 -Encoding UTF8

$part5 = @'
<!-- ===== MANEJO ===== -->
<div id="screen-manejo" class="screen px-4 pt-4">
  <h2 class="text-xl font-bold mb-4">Manejo e Coleta</h2>
  <div class="flex gap-2 mb-4">
    <button onclick="showManejoTab('escores')" class="manejo-tab btn-press px-4 py-2 rounded-xl text-sm font-semibold bg-primary text-white" data-tab="escores">Escores</button>
    <button onclick="showManejoTab('eventos')" class="manejo-tab btn-press px-4 py-2 rounded-xl text-sm font-semibold bg-gray-100 text-text-secondary" data-tab="eventos">Eventos</button>
  </div>
  <div id="manejo-escores">
    <div class="space-y-4">
      <div><label class="text-xs font-semibold text-text-secondary uppercase tracking-wider">Piquete</label>
        <select id="esc-paddock" class="w-full mt-1 px-4 py-3 bg-white rounded-xl border border-gray-200 outline-none"><option>Piquete 1</option><option>Piquete 2</option><option>Piquete 3</option></select></div>
      <div><label class="text-xs font-semibold text-text-secondary uppercase tracking-wider">Tipo de Escore</label>
        <select id="esc-type" class="w-full mt-1 px-4 py-3 bg-white rounded-xl border border-gray-200 outline-none"><option>Escore de Pasto</option><option>Escore de Fezes</option><option>Escore de Cocho</option></select></div>
      <div><label class="text-xs font-semibold text-text-secondary uppercase tracking-wider">Valor (0-100)</label><input id="esc-value" type="range" min="0" max="100" value="50" class="w-full mt-1" oninput="document.getElementById('esc-val-label').textContent=this.value"><p class="text-center text-sm font-semibold text-primary" id="esc-val-label">50</p></div>
      <div><label class="text-xs font-semibold text-text-secondary uppercase tracking-wider">Observacoes</label><textarea id="esc-notes" rows="2" class="w-full mt-1 px-4 py-3 bg-white rounded-xl border border-gray-200 outline-none" placeholder="Opcional"></textarea></div>
      <button onclick="salvarEscore()" class="btn-press w-full py-3.5 bg-primary text-white font-semibold rounded-xl shadow-lg shadow-primary/30">Salvar Escore</button>
    </div>
  </div>
  <div id="manejo-eventos" style="display:none">
    <div class="space-y-4">
      <div><label class="text-xs font-semibold text-text-secondary uppercase tracking-wider">RFID do Animal</label>
        <select id="evt-rfid" class="w-full mt-1 px-4 py-3 bg-white rounded-xl border border-gray-200 outline-none"></select></div>
      <div id="evt-animal-card" class="hidden bg-white rounded-xl border border-gray-200 p-3"></div>
      <div><label class="text-xs font-semibold text-text-secondary uppercase tracking-wider">Tipo de Evento</label>
        <select id="evt-type" class="w-full mt-1 px-4 py-3 bg-white rounded-xl border border-gray-200 outline-none" onchange="togglePesoEvt()"><option>Pesagem</option><option>Vacinacao</option><option>Vermifugacao</option><option>Desmama</option></select></div>
      <div id="evt-peso-wrap"><label class="text-xs font-semibold text-text-secondary uppercase tracking-wider">Novo Peso (kg)</label><input id="evt-peso" type="number" step="0.1" class="w-full mt-1 px-4 py-3 bg-white rounded-xl border border-gray-200 outline-none"></div>
      <div><label class="text-xs font-semibold text-text-secondary uppercase tracking-wider">Detalhes</label><input id="evt-details" type="text" placeholder="Ex: nome da vacina" class="w-full mt-1 px-4 py-3 bg-white rounded-xl border border-gray-200 outline-none"></div>
      <button onclick="registrarEvento()" class="btn-press w-full py-3.5 bg-primary text-white font-semibold rounded-xl shadow-lg shadow-primary/30">Registrar Evento</button>
    </div>
  </div>
</div>
'@

Add-Content -Path $file -Value $part5 -Encoding UTF8

$part6 = @'
<!-- ===== ESTOQUE ===== -->
<div id="screen-estoque" class="screen px-4 pt-4">
  <div class="flex items-center justify-between mb-4">
    <h2 class="text-xl font-bold">Estoque</h2>
    <button onclick="showSubScreen('cad-produto')" class="btn-press bg-primary text-white px-4 py-2 rounded-xl text-sm font-semibold shadow-md shadow-primary/20"><i class="ph-bold ph-plus mr-1"></i>Novo</button>
  </div>
  <div id="estoque-summary" class="grid grid-cols-3 gap-2 mb-4"></div>
  <div id="estoque-list" class="space-y-3"></div>
</div>

<!-- ===== CADASTRO PRODUTO ===== -->
<div id="screen-cad-produto" class="screen px-4 pt-4">
  <div class="flex items-center gap-3 mb-5">
    <button onclick="showScreen('estoque')" class="btn-press w-10 h-10 bg-gray-100 rounded-xl flex items-center justify-center"><i class="ph-bold ph-arrow-left text-lg"></i></button>
    <h2 class="text-xl font-bold">Novo Produto</h2>
  </div>
  <div class="space-y-4">
    <div><label class="text-xs font-semibold text-text-secondary uppercase tracking-wider">Nome do Produto</label><input id="prod-name" type="text" class="w-full mt-1 px-4 py-3 bg-white rounded-xl border border-gray-200 outline-none"></div>
    <div><label class="text-xs font-semibold text-text-secondary uppercase tracking-wider">Categoria</label>
      <select id="prod-cat" class="w-full mt-1 px-4 py-3 bg-white rounded-xl border border-gray-200 outline-none"><option>Nutricao</option><option>Medicamento</option><option>Material Geral</option><option>Ferramentas</option><option>Outros</option></select></div>
    <div class="grid grid-cols-2 gap-3">
      <div><label class="text-xs font-semibold text-text-secondary uppercase tracking-wider">Quantidade</label><input id="prod-qty" type="number" step="1" value="0" class="w-full mt-1 px-4 py-3 bg-white rounded-xl border border-gray-200 outline-none"></div>
      <div><label class="text-xs font-semibold text-text-secondary uppercase tracking-wider">Unidade</label>
        <select id="prod-unit" class="w-full mt-1 px-4 py-3 bg-white rounded-xl border border-gray-200 outline-none"><option>kg</option><option>Litros</option><option>Sacos</option><option>Frascos</option><option>Doses</option><option>Unidade</option><option>Caixas</option></select></div>
    </div>
    <div><label class="text-xs font-semibold text-text-secondary uppercase tracking-wider">Custo Unitario (R$)</label><input id="prod-cost" type="number" step="0.01" value="0" class="w-full mt-1 px-4 py-3 bg-white rounded-xl border border-gray-200 outline-none"></div>
    <button onclick="cadastrarProduto()" class="btn-press w-full py-3.5 bg-primary text-white font-semibold rounded-xl shadow-lg shadow-primary/30">Cadastrar Produto</button>
  </div>
</div>
'@

Add-Content -Path $file -Value $part6 -Encoding UTF8

$part7 = @'
<!-- ===== TAREFAS ===== -->
<div id="screen-tarefas" class="screen px-4 pt-4">
  <div class="flex items-center justify-between mb-4">
    <h2 class="text-xl font-bold">Tarefas</h2>
    <button onclick="showSubScreen('nova-tarefa')" class="btn-press bg-primary text-white px-4 py-2 rounded-xl text-sm font-semibold shadow-md shadow-primary/20"><i class="ph-bold ph-plus mr-1"></i>Nova</button>
  </div>
  <div id="tarefas-list" class="space-y-3"></div>
</div>

<!-- ===== NOVA TAREFA ===== -->
<div id="screen-nova-tarefa" class="screen px-4 pt-4">
  <div class="flex items-center gap-3 mb-5">
    <button onclick="showScreen('tarefas')" class="btn-press w-10 h-10 bg-gray-100 rounded-xl flex items-center justify-center"><i class="ph-bold ph-arrow-left text-lg"></i></button>
    <h2 class="text-xl font-bold">Nova Tarefa</h2>
  </div>
  <div class="space-y-4">
    <div><label class="text-xs font-semibold text-text-secondary uppercase tracking-wider">Descricao</label><input id="task-desc" type="text" class="w-full mt-1 px-4 py-3 bg-white rounded-xl border border-gray-200 outline-none"></div>
    <div><label class="text-xs font-semibold text-text-secondary uppercase tracking-wider">Responsavel</label><input id="task-assignee" type="text" class="w-full mt-1 px-4 py-3 bg-white rounded-xl border border-gray-200 outline-none"></div>
    <div><label class="text-xs font-semibold text-text-secondary uppercase tracking-wider">Prioridade</label>
      <select id="task-priority" class="w-full mt-1 px-4 py-3 bg-white rounded-xl border border-gray-200 outline-none"><option value="alta">Alta</option><option value="media" selected>Media</option><option value="baixa">Baixa</option></select></div>
    <button onclick="addTask()" class="btn-press w-full py-3.5 bg-primary text-white font-semibold rounded-xl shadow-lg shadow-primary/30">Criar Tarefa</button>
  </div>
</div>

<!-- ===== CICLO PRODUTIVO ===== -->
<div id="screen-ciclo" class="screen px-4 pt-4">
  <div class="flex items-center gap-3 mb-5">
    <button onclick="showScreen('dashboard')" class="btn-press w-10 h-10 bg-gray-100 rounded-xl flex items-center justify-center"><i class="ph-bold ph-arrow-left text-lg"></i></button>
    <h2 class="text-xl font-bold">Ciclo Produtivo</h2>
  </div>
  <div id="ciclo-cards" class="space-y-4"></div>
  <h3 class="font-semibold text-sm mt-5 mb-3">Transicao de Fase</h3>
  <div class="space-y-3">
    <div><label class="text-xs font-semibold text-text-secondary uppercase tracking-wider">Animal</label>
      <select id="trans-animal" class="w-full mt-1 px-4 py-3 bg-white rounded-xl border border-gray-200 outline-none"></select></div>
    <div><label class="text-xs font-semibold text-text-secondary uppercase tracking-wider">Nova Fase</label>
      <select id="trans-fase" class="w-full mt-1 px-4 py-3 bg-white rounded-xl border border-gray-200 outline-none"><option value="recria">Recria</option><option value="engorda">Engorda</option><option value="venda">Venda</option></select></div>
    <div><label class="text-xs font-semibold text-text-secondary uppercase tracking-wider">Peso na Transicao (kg)</label><input id="trans-peso" type="number" step="0.5" class="w-full mt-1 px-4 py-3 bg-white rounded-xl border border-gray-200 outline-none"></div>
    <button onclick="transicaoFase()" class="btn-press w-full py-3.5 bg-venda text-white font-semibold rounded-xl shadow-lg shadow-venda/30">Confirmar Transicao</button>
  </div>
</div>
'@

Add-Content -Path $file -Value $part7 -Encoding UTF8

Write-Host "Parts 1-7 written OK"
