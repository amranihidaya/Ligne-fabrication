"""
Animation industrielle du flux de production.
Design type SCADA/MES — sobre, lisible, sans emojis.
"""
import json
from services.domain import ResultatSimulation


def generer_animation_html(resultat: ResultatSimulation, vitesse: int = 50) -> str:
    postes = resultat.postes
    goulot_num = resultat.poste_goulot.numero

    config = {
        "postes": [
            {
                "numero": p.numero,
                "nom": p.nom_operation,
                "machine": p.machine,
                "temps": p.temps_min_par_piece,
                "temps_eff": p.temps_effectif,
                "nb_machines": p.nb_machines,
                "is_goulot": p.numero == goulot_num,
            } for p in postes
        ],
        "taux_arret": resultat.parametres.taux_arret_machine,
        "taux_rebut": resultat.parametres.taux_rebut,
        "demande": resultat.parametres.demande_client_jour,
        "duree_journee_min": resultat.parametres.temps_travail_min_jour,
    }
    config_json = json.dumps(config)

    return f"""
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<style>
  :root {{
    --bg: #f8f9fb;
    --surface: #ffffff;
    --border: #e5e7ec;
    --text: #1a1d23;
    --text-muted: #6b7280;
    --text-subtle: #9ca3af;
    --primary: #1f3a8a;
    --primary-light: #3b5bdb;
    --accent: #0d9488;
    --warning: #d97706;
    --danger: #b91c1c;
    --success: #15803d;
    --machine-fill: #f1f3f6;
    --machine-stroke: #475569;
    --goulot-fill: #fef2f2;
    --goulot-stroke: #b91c1c;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 20px;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: var(--bg);
    color: var(--text);
    -webkit-font-smoothing: antialiased;
  }}

  .controls {{
    display: flex;
    align-items: center;
    gap: 8px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 16px;
  }}
  button {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 7px 14px;
    border: 1px solid var(--border);
    border-radius: 5px;
    background: var(--surface);
    color: var(--text);
    font-family: inherit;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s;
  }}
  button:hover {{ background: #f3f4f6; border-color: #cbd5e0; }}
  button.primary {{ background: var(--primary); color: white; border-color: var(--primary); }}
  button.primary:hover {{ background: var(--primary-light); border-color: var(--primary-light); }}
  button svg {{ width: 14px; height: 14px; }}

  .divider {{ width: 1px; height: 24px; background: var(--border); margin: 0 4px; }}

  .speed {{ display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--text-muted); }}
  select {{
    padding: 5px 8px;
    border: 1px solid var(--border);
    border-radius: 4px;
    font-family: inherit;
    font-size: 12px;
    background: var(--surface);
    color: var(--text);
  }}

  .time-display {{
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: var(--text-muted);
  }}
  .time-value {{
    font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
    font-size: 13px;
    font-weight: 600;
    color: var(--text);
    background: var(--bg);
    padding: 4px 10px;
    border-radius: 4px;
  }}

  .kpis {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin-bottom: 16px;
  }}
  @media (max-width: 900px) {{ .kpis {{ grid-template-columns: repeat(2, 1fr); }} }}

  .kpi {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 14px 16px;
    position: relative;
    overflow: hidden;
  }}
  .kpi-label {{
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-muted);
    margin-bottom: 6px;
  }}
  .kpi-value {{
    font-size: 26px;
    font-weight: 700;
    color: var(--text);
    line-height: 1;
    font-variant-numeric: tabular-nums;
  }}
  .kpi-sub {{
    font-size: 11px;
    color: var(--text-subtle);
    margin-top: 6px;
  }}
  .kpi-indicator {{
    position: absolute;
    top: 0; left: 0;
    width: 3px;
    height: 100%;
    background: var(--primary);
  }}
  .kpi.success .kpi-indicator {{ background: var(--success); }}
  .kpi.warning .kpi-indicator {{ background: var(--warning); }}
  .kpi.danger  .kpi-indicator {{ background: var(--danger); }}

  .scene {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 24px 16px 20px;
  }}
  svg.line-svg {{ display: block; width: 100%; height: auto; }}

  .conveyor-stripe {{ animation: scroll 1.5s linear infinite; }}
  @keyframes scroll {{ to {{ transform: translateX(-20px); }} }}

  .goulot-pulse {{ animation: pulse 2s ease-in-out infinite; }}
  @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.55; }} }}

  .legend {{
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
    margin-top: 16px;
    padding-top: 14px;
    border-top: 1px solid var(--border);
    font-size: 12px;
    color: var(--text-muted);
  }}
  .legend-item {{ display: flex; align-items: center; gap: 7px; }}
  .swatch {{ width: 12px; height: 12px; border-radius: 50%; border: 1.5px solid rgba(0,0,0,0.1); }}
  .swatch.square {{ border-radius: 2px; width: 14px; height: 14px; }}
</style>
</head>
<body>

<div class="controls">
  <button class="primary" id="btn-play">
    <svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
    Démarrer
  </button>
  <button id="btn-pause">
    <svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>
    Pause
  </button>
  <button id="btn-reset">
    <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/></svg>
    Réinitialiser
  </button>
  <div class="divider"></div>
  <div class="speed">
    <span>Vitesse</span>
    <select id="speed-select">
      <option value="100">0.5x</option>
      <option value="50" selected>1x</option>
      <option value="20">2.5x</option>
      <option value="10">5x</option>
    </select>
  </div>
  <div class="time-display">
    <span>Temps simulé</span>
    <span class="time-value"><span id="sim-time">0.0</span> / {int(config['duree_journee_min'])} min</span>
  </div>
</div>

<div class="kpis">
  <div class="kpi">
    <div class="kpi-indicator"></div>
    <div class="kpi-label">Pièces lancées</div>
    <div class="kpi-value" id="count-in">0</div>
    <div class="kpi-sub">Entrées en production</div>
  </div>
  <div class="kpi success">
    <div class="kpi-indicator"></div>
    <div class="kpi-label">Conformes</div>
    <div class="kpi-value" id="count-ok">0</div>
    <div class="kpi-sub">Pièces livrables</div>
  </div>
  <div class="kpi danger">
    <div class="kpi-indicator"></div>
    <div class="kpi-label">Rebuts</div>
    <div class="kpi-value" id="count-rebut">0</div>
    <div class="kpi-sub">Non conformes</div>
  </div>
  <div class="kpi warning">
    <div class="kpi-indicator"></div>
    <div class="kpi-label">Arrêts machine</div>
    <div class="kpi-value" id="count-arrets">0</div>
    <div class="kpi-sub">Événements</div>
  </div>
  <div class="kpi" id="kpi-objectif">
    <div class="kpi-indicator"></div>
    <div class="kpi-label">Avancement demande</div>
    <div class="kpi-value"><span id="objectif-pct">0</span><span style="font-size: 16px; color: var(--text-muted);">%</span></div>
    <div class="kpi-sub">Cible {int(config['demande'])} pcs/jour</div>
  </div>
</div>

<div class="scene">
  <svg class="line-svg" id="ligne" viewBox="0 0 1100 360" xmlns="http://www.w3.org/2000/svg"></svg>
  <div class="legend">
    <div class="legend-item"><div class="swatch" style="background: #1f3a8a;"></div><span>Pièce en cours</span></div>
    <div class="legend-item"><div class="swatch" style="background: #15803d;"></div><span>Pièce conforme</span></div>
    <div class="legend-item"><div class="swatch" style="background: #b91c1c;"></div><span>Rebut</span></div>
    <div class="legend-item"><div class="swatch square" style="background: #fef3c7; border-color: #d97706;"></div><span>Machine en arrêt</span></div>
    <div class="legend-item"><div class="swatch square" style="background: #fef2f2; border-color: #b91c1c;"></div><span>Goulot d'étranglement</span></div>
  </div>
</div>

<script>
const CONFIG = {config_json};
const SVG_NS = 'http://www.w3.org/2000/svg';
const svg = document.getElementById('ligne');
const W = 1100, H = 360;
const N = CONFIG.postes.length;

const MARGIN_X = 50;
const MACHINE_W = (W - 2 * MARGIN_X) / N - 20;
const MACHINE_H_BASE = 110;
const CENTER_Y = 200;
const postesX = CONFIG.postes.map((_, i) => MARGIN_X + 10 + i * (MACHINE_W + 20));

function drawConveyor() {{
  const support = document.createElementNS(SVG_NS, 'rect');
  support.setAttribute('x', MARGIN_X - 5);
  support.setAttribute('y', CENTER_Y + 8);
  support.setAttribute('width', W - 2 * MARGIN_X + 10);
  support.setAttribute('height', 6);
  support.setAttribute('fill', '#cbd5e0');
  svg.appendChild(support);

  const belt = document.createElementNS(SVG_NS, 'rect');
  belt.setAttribute('x', MARGIN_X - 5);
  belt.setAttribute('y', CENTER_Y - 4);
  belt.setAttribute('width', W - 2 * MARGIN_X + 10);
  belt.setAttribute('height', 12);
  belt.setAttribute('fill', '#475569');
  belt.setAttribute('rx', 1);
  svg.appendChild(belt);

  const stripeGroup = document.createElementNS(SVG_NS, 'g');
  stripeGroup.setAttribute('class', 'conveyor-stripe');
  for (let i = MARGIN_X - 20; i < W; i += 20) {{
    const stripe = document.createElementNS(SVG_NS, 'line');
    stripe.setAttribute('x1', i);
    stripe.setAttribute('y1', CENTER_Y - 4);
    stripe.setAttribute('x2', i + 8);
    stripe.setAttribute('y2', CENTER_Y + 8);
    stripe.setAttribute('stroke', '#64748b');
    stripe.setAttribute('stroke-width', 1.5);
    stripeGroup.appendChild(stripe);
  }}
  svg.appendChild(stripeGroup);

  const arrowIn = document.createElementNS(SVG_NS, 'path');
  arrowIn.setAttribute('d', `M ${{MARGIN_X - 25}} ${{CENTER_Y - 12}} L ${{MARGIN_X - 8}} ${{CENTER_Y + 2}} L ${{MARGIN_X - 25}} ${{CENTER_Y + 16}}`);
  arrowIn.setAttribute('fill', 'none');
  arrowIn.setAttribute('stroke', '#0d9488');
  arrowIn.setAttribute('stroke-width', 2.5);
  arrowIn.setAttribute('stroke-linecap', 'round');
  arrowIn.setAttribute('stroke-linejoin', 'round');
  svg.appendChild(arrowIn);

  const arrowOut = document.createElementNS(SVG_NS, 'path');
  arrowOut.setAttribute('d', `M ${{W - MARGIN_X + 8}} ${{CENTER_Y - 12}} L ${{W - MARGIN_X + 25}} ${{CENTER_Y + 2}} L ${{W - MARGIN_X + 8}} ${{CENTER_Y + 16}}`);
  arrowOut.setAttribute('fill', 'none');
  arrowOut.setAttribute('stroke', '#0d9488');
  arrowOut.setAttribute('stroke-width', 2.5);
  arrowOut.setAttribute('stroke-linecap', 'round');
  arrowOut.setAttribute('stroke-linejoin', 'round');
  svg.appendChild(arrowOut);
}}

function drawMachine(p, x, idx) {{
  const g = document.createElementNS(SVG_NS, 'g');

  const maxTemps = Math.max(...CONFIG.postes.map(po => po.temps));
  const machineH = MACHINE_H_BASE + (p.temps / maxTemps) * 30;
  const machineY = CENTER_Y - 8 - machineH;

  if (p.is_goulot) {{
    const tagBg = document.createElementNS(SVG_NS, 'rect');
    tagBg.setAttribute('x', x + MACHINE_W/2 - 38);
    tagBg.setAttribute('y', machineY - 28);
    tagBg.setAttribute('width', 76);
    tagBg.setAttribute('height', 20);
    tagBg.setAttribute('rx', 3);
    tagBg.setAttribute('fill', '#b91c1c');
    tagBg.setAttribute('class', 'goulot-pulse');
    g.appendChild(tagBg);

    const tagText = document.createElementNS(SVG_NS, 'text');
    tagText.setAttribute('x', x + MACHINE_W/2);
    tagText.setAttribute('y', machineY - 14);
    tagText.setAttribute('text-anchor', 'middle');
    tagText.setAttribute('font-size', '11');
    tagText.setAttribute('font-weight', '700');
    tagText.setAttribute('fill', 'white');
    tagText.setAttribute('letter-spacing', '0.5');
    tagText.textContent = 'GOULOT';
    g.appendChild(tagText);

    const triangle = document.createElementNS(SVG_NS, 'path');
    triangle.setAttribute('d', `M ${{x + MACHINE_W/2 - 5}} ${{machineY - 8}} L ${{x + MACHINE_W/2 + 5}} ${{machineY - 8}} L ${{x + MACHINE_W/2}} ${{machineY - 2}} Z`);
    triangle.setAttribute('fill', '#b91c1c');
    g.appendChild(triangle);
  }}

  const body = document.createElementNS(SVG_NS, 'rect');
  body.setAttribute('x', x);
  body.setAttribute('y', machineY);
  body.setAttribute('width', MACHINE_W);
  body.setAttribute('height', machineH);
  body.setAttribute('rx', 4);
  body.setAttribute('fill', p.is_goulot ? '#fef2f2' : '#f1f3f6');
  body.setAttribute('stroke', p.is_goulot ? '#b91c1c' : '#475569');
  body.setAttribute('stroke-width', p.is_goulot ? 2 : 1.5);
  g.appendChild(body);

  const panel = document.createElementNS(SVG_NS, 'rect');
  panel.setAttribute('x', x + 8);
  panel.setAttribute('y', machineY + 8);
  panel.setAttribute('width', MACHINE_W - 16);
  panel.setAttribute('height', 18);
  panel.setAttribute('rx', 2);
  panel.setAttribute('fill', '#1e293b');
  g.appendChild(panel);

  const led = document.createElementNS(SVG_NS, 'circle');
  led.setAttribute('cx', x + 16);
  led.setAttribute('cy', machineY + 17);
  led.setAttribute('r', 3);
  led.setAttribute('fill', '#10b981');
  g.appendChild(led);

  const machineLabel = document.createElementNS(SVG_NS, 'text');
  machineLabel.setAttribute('x', x + 26);
  machineLabel.setAttribute('y', machineY + 21);
  machineLabel.setAttribute('font-size', '10');
  machineLabel.setAttribute('font-weight', '600');
  machineLabel.setAttribute('fill', '#cbd5e0');
  machineLabel.setAttribute('font-family', "'SF Mono', monospace");
  machineLabel.textContent = 'M0' + p.numero;
  g.appendChild(machineLabel);

  const mecaY = machineY + 38;
  const mecaH = machineH - 60;
  const cx = x + MACHINE_W/2;
  const cy = mecaY + mecaH/2;
  const radius = Math.min(18, mecaH/3);

  const tool = document.createElementNS(SVG_NS, 'circle');
  tool.setAttribute('cx', cx);
  tool.setAttribute('cy', cy);
  tool.setAttribute('r', radius);
  tool.setAttribute('fill', 'none');
  tool.setAttribute('stroke', '#64748b');
  tool.setAttribute('stroke-width', 2);
  g.appendChild(tool);

  const r2 = radius - 4;
  const cross1 = document.createElementNS(SVG_NS, 'line');
  cross1.setAttribute('x1', cx - r2); cross1.setAttribute('y1', cy);
  cross1.setAttribute('x2', cx + r2); cross1.setAttribute('y2', cy);
  cross1.setAttribute('stroke', '#94a3b8'); cross1.setAttribute('stroke-width', 1.5);
  g.appendChild(cross1);
  const cross2 = document.createElementNS(SVG_NS, 'line');
  cross2.setAttribute('x1', cx); cross2.setAttribute('y1', cy - r2);
  cross2.setAttribute('x2', cx); cross2.setAttribute('y2', cy + r2);
  cross2.setAttribute('stroke', '#94a3b8'); cross2.setAttribute('stroke-width', 1.5);
  g.appendChild(cross2);

  const nameLabel = document.createElementNS(SVG_NS, 'text');
  nameLabel.setAttribute('x', x + MACHINE_W/2);
  nameLabel.setAttribute('y', machineY + machineH - 10);
  nameLabel.setAttribute('text-anchor', 'middle');
  nameLabel.setAttribute('font-size', '12');
  nameLabel.setAttribute('font-weight', '600');
  nameLabel.setAttribute('fill', '#1a1d23');
  nameLabel.textContent = p.machine;
  g.appendChild(nameLabel);

  const infoY = CENTER_Y + 35;

  const counterBox = document.createElementNS(SVG_NS, 'rect');
  counterBox.setAttribute('x', x + 4);
  counterBox.setAttribute('y', infoY);
  counterBox.setAttribute('width', MACHINE_W - 8);
  counterBox.setAttribute('height', 56);
  counterBox.setAttribute('rx', 4);
  counterBox.setAttribute('fill', '#f8f9fb');
  counterBox.setAttribute('stroke', '#e5e7ec');
  counterBox.setAttribute('stroke-width', 1);
  g.appendChild(counterBox);

  const timeLabel = document.createElementNS(SVG_NS, 'text');
  timeLabel.setAttribute('x', x + MACHINE_W/2);
  timeLabel.setAttribute('y', infoY + 16);
  timeLabel.setAttribute('text-anchor', 'middle');
  timeLabel.setAttribute('font-size', '9');
  timeLabel.setAttribute('font-weight', '600');
  timeLabel.setAttribute('fill', '#6b7280');
  timeLabel.setAttribute('letter-spacing', '0.5');
  timeLabel.textContent = 'TEMPS / PIÈCE';
  g.appendChild(timeLabel);

  const timeValue = document.createElementNS(SVG_NS, 'text');
  timeValue.setAttribute('x', x + MACHINE_W/2);
  timeValue.setAttribute('y', infoY + 30);
  timeValue.setAttribute('text-anchor', 'middle');
  timeValue.setAttribute('font-size', '13');
  timeValue.setAttribute('font-weight', '700');
  timeValue.setAttribute('fill', '#1a1d23');
  timeValue.setAttribute('font-family', "'SF Mono', monospace");
  timeValue.textContent = p.temps + ' min';
  g.appendChild(timeValue);

  const counter = document.createElementNS(SVG_NS, 'text');
  counter.setAttribute('x', x + MACHINE_W/2);
  counter.setAttribute('y', infoY + 48);
  counter.setAttribute('text-anchor', 'middle');
  counter.setAttribute('font-size', '11');
  counter.setAttribute('font-weight', '500');
  counter.setAttribute('fill', '#0d9488');
  counter.textContent = '0 traitées';
  g.appendChild(counter);

  svg.appendChild(g);

  return {{ body, led, counter, machineY, machineH, x, w: MACHINE_W }};
}}

drawConveyor();
const machinesEls = CONFIG.postes.map((p, i) => drawMachine(p, postesX[i], i));

let simState = {{
  running: false, simTime: 0, pieces: [], nextId: 1,
  countIn: 0, countOk: 0, countRebut: 0, countArrets: 0,
  postesTraites: new Array(N).fill(0),
  machineState: CONFIG.postes.map(() => ({{ enPanne: false, finPanne: 0 }})),
  queues: CONFIG.postes.map(() => []),
  enCours: CONFIG.postes.map(() => null),
}};

let timerId = null;
let speed = parseInt(document.getElementById('speed-select').value);
const TICK_MIN = 0.1;

function newPiece() {{
  return {{ id: simState.nextId++, posteIdx: -1, progres: 0, rejected: false, el: null }};
}}

function createPieceEl(piece) {{
  const c = document.createElementNS(SVG_NS, 'circle');
  c.setAttribute('r', 6);
  c.setAttribute('fill', '#1f3a8a');
  c.setAttribute('stroke', '#172554');
  c.setAttribute('stroke-width', 1.5);
  svg.appendChild(c);
  piece.el = c;
}}

function updatePiecePos(piece) {{
  if (!piece.el) return;
  let x, y = CENTER_Y + 2;
  if (piece.posteIdx === -1) {{
    x = (MARGIN_X - 8) + piece.progres * (postesX[0] + MACHINE_W/2 - (MARGIN_X - 8));
  }} else if (piece.posteIdx >= N) {{
    const lastX = postesX[N-1] + MACHINE_W/2;
    x = lastX + piece.progres * (W - MARGIN_X + 8 - lastX);
    if (piece.rejected) y = CENTER_Y + 2 + (piece.progres * 80);
  }} else {{
    const px = postesX[piece.posteIdx];
    x = px + piece.progres * MACHINE_W;
  }}
  piece.el.setAttribute('cx', x);
  piece.el.setAttribute('cy', y);
  if (piece.rejected) {{
    piece.el.setAttribute('fill', '#b91c1c');
    piece.el.setAttribute('stroke', '#7f1d1d');
  }}
}}

function checkPanne(posteIdx, t) {{
  const ms = simState.machineState[posteIdx];
  if (ms.enPanne) {{
    if (t >= ms.finPanne) {{
      ms.enPanne = false;
      const m = machinesEls[posteIdx];
      m.body.setAttribute('fill', CONFIG.postes[posteIdx].is_goulot ? '#fef2f2' : '#f1f3f6');
      m.led.setAttribute('fill', '#10b981');
    }}
    return ms.enPanne;
  }}
  const probTick = CONFIG.taux_arret * TICK_MIN / 10;
  if (Math.random() < probTick) {{
    ms.enPanne = true;
    ms.finPanne = t + 5 + Math.random() * 10;
    const m = machinesEls[posteIdx];
    m.body.setAttribute('fill', '#fef3c7');
    m.led.setAttribute('fill', '#f59e0b');
    simState.countArrets++;
    return true;
  }}
  return false;
}}

function tick() {{
  if (!simState.running) return;
  if (simState.simTime >= CONFIG.duree_journee_min) {{ pause(); return; }}
  simState.simTime += TICK_MIN;

  if (!simState.enCours[0] && simState.queues[0].length === 0) {{
    const p = newPiece();
    createPieceEl(p);
    simState.pieces.push(p);
    simState.queues[0].push(p);
    simState.countIn++;
  }}

  for (let i = 0; i < N; i++) {{
    if (checkPanne(i, simState.simTime)) continue;
    if (!simState.enCours[i] && simState.queues[i].length > 0) {{
      const p = simState.queues[i].shift();
      p.posteIdx = i;
      p.progres = 0;
      simState.enCours[i] = {{ piece: p, debut: simState.simTime, duree: CONFIG.postes[i].temps_eff }};
    }}
    if (simState.enCours[i]) {{
      const ec = simState.enCours[i];
      ec.piece.progres = (simState.simTime - ec.debut) / ec.duree;
      if (ec.piece.progres >= 1) {{
        ec.piece.progres = 1;
        simState.postesTraites[i]++;
        machinesEls[i].counter.textContent = simState.postesTraites[i] + ' traitées';
        if (i === N - 1) {{
          if (Math.random() < CONFIG.taux_rebut) {{
            ec.piece.rejected = true;
            simState.countRebut++;
          }} else {{
            ec.piece.el.setAttribute('fill', '#15803d');
            ec.piece.el.setAttribute('stroke', '#14532d');
            simState.countOk++;
          }}
          ec.piece.posteIdx = N;
          ec.piece.progres = 0;
        }} else {{
          simState.queues[i+1].push(ec.piece);
          ec.piece.posteIdx = -2;
        }}
        simState.enCours[i] = null;
      }}
      updatePiecePos(ec.piece);
    }}
  }}

  simState.pieces.forEach(p => {{
    if (p.posteIdx === N) {{
      p.progres += TICK_MIN / 1.5;
      if (p.progres >= 1) {{ if (p.el) p.el.remove(); p.el = null; }}
      else updatePiecePos(p);
    }}
  }});
  simState.pieces = simState.pieces.filter(p => p.el !== null);

  document.getElementById('count-in').textContent = simState.countIn;
  document.getElementById('count-ok').textContent = simState.countOk;
  document.getElementById('count-rebut').textContent = simState.countRebut;
  document.getElementById('count-arrets').textContent = simState.countArrets;
  document.getElementById('sim-time').textContent = simState.simTime.toFixed(1);
  const pct = Math.min(100, (simState.countOk / CONFIG.demande) * 100);
  document.getElementById('objectif-pct').textContent = pct.toFixed(0);
  const cardObj = document.getElementById('kpi-objectif');
  cardObj.classList.remove('success', 'warning', 'danger');
  if (pct >= 100) cardObj.classList.add('success');
  else if (pct >= 80) cardObj.classList.add('warning');
  else if (simState.simTime > 60) cardObj.classList.add('danger');

  timerId = setTimeout(tick, speed);
}}

function play() {{ if (simState.running) return; simState.running = true; tick(); }}
function pause() {{ simState.running = false; if (timerId) clearTimeout(timerId); }}
function reset() {{
  pause();
  simState.pieces.forEach(p => {{ if (p.el) p.el.remove(); }});
  simState = {{
    running: false, simTime: 0, pieces: [], nextId: 1,
    countIn: 0, countOk: 0, countRebut: 0, countArrets: 0,
    postesTraites: new Array(N).fill(0),
    machineState: CONFIG.postes.map(() => ({{ enPanne: false, finPanne: 0 }})),
    queues: CONFIG.postes.map(() => []),
    enCours: CONFIG.postes.map(() => null),
  }};
  machinesEls.forEach((el, i) => {{
    el.body.setAttribute('fill', CONFIG.postes[i].is_goulot ? '#fef2f2' : '#f1f3f6');
    el.led.setAttribute('fill', '#10b981');
    el.counter.textContent = '0 traitées';
  }});
  ['count-in', 'count-ok', 'count-rebut', 'count-arrets'].forEach(id => document.getElementById(id).textContent = '0');
  document.getElementById('sim-time').textContent = '0.0';
  document.getElementById('objectif-pct').textContent = '0';
  document.getElementById('kpi-objectif').classList.remove('success', 'warning', 'danger');
}}

document.getElementById('btn-play').onclick = play;
document.getElementById('btn-pause').onclick = pause;
document.getElementById('btn-reset').onclick = reset;
document.getElementById('speed-select').onchange = (e) => {{ speed = parseInt(e.target.value); }};
</script>
</body>
</html>
"""
