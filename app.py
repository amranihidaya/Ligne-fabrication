"""
Application Streamlit — Optimisation Ligne de Fabrication
Lancer : streamlit run app.py
"""
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import pandas as pd

from services import calculs, scenarios, alertes
from services.excel_loader import charger_excel, generer_template_excel, ExcelStructureError
from components.animation import generer_animation_html


st.set_page_config(
    page_title="Optimisation Ligne de Fabrication",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CSS GLOBAL — design industriel premium
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', -apple-system, sans-serif;
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 1400px;
}

h1 {
    font-weight: 600 !important;
    font-size: 1.65rem !important;
    color: #0f172a !important;
    letter-spacing: -0.03em;
    margin-bottom: 0.2rem !important;
}
h2 {
    font-weight: 600 !important;
    font-size: 1.1rem !important;
    color: #1e293b !important;
    margin-top: 1.8rem !important;
    letter-spacing: -0.01em;
}
h3 { font-weight: 500 !important; font-size: 0.95rem !important; color: #334155 !important; }

.subtitle {
    color: #64748b; font-size: 0.9rem;
    margin-bottom: 1.75rem; margin-top: -0.2rem; font-weight: 400;
}

/* ─── SIDEBAR ─── */
section[data-testid="stSidebar"] {
    background: #0f172a !important;
    border-right: none !important;
    width: 270px !important;
}
section[data-testid="stSidebar"] > div { background: #0f172a !important; padding: 0 !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label { color: #e2e8f0 !important; }
section[data-testid="stSidebar"] hr { border-color: #1e293b !important; margin: 0.75rem 0 !important; }
section[data-testid="stSidebar"] .stCheckbox label { color: #94a3b8 !important; font-size: 13px !important; }
section[data-testid="stSidebar"] .stCheckbox label:hover { color: #e2e8f0 !important; }
section[data-testid="stSidebar"] .stButton > button,
section[data-testid="stSidebar"] .stDownloadButton > button {
    background: #1e3a5f !important; color: #93c5fd !important;
    border: 1px solid #1d4ed8 !important; border-radius: 6px !important;
    font-size: 13px !important; font-weight: 500 !important;
    padding: 8px 14px !important; width: 100% !important; transition: all 0.15s ease !important;
}
section[data-testid="stSidebar"] .stButton > button:hover,
section[data-testid="stSidebar"] .stDownloadButton > button:hover {
    background: #1d4ed8 !important; color: #ffffff !important; border-color: #3b82f6 !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] section {
    background: #1e293b !important; border: 1.5px dashed #334155 !important; border-radius: 8px !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] section:hover {
    border-color: #3b82f6 !important; background: #1e3a5f !important;
}

/* ─── TABS ─── */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px; background: transparent;
    border-bottom: 1.5px solid #e2e8f0; margin-bottom: 1.75rem;
}
.stTabs [data-baseweb="tab"] {
    height: 40px; padding: 0 16px; background: transparent;
    color: #64748b; font-weight: 500; font-size: 13.5px;
    border: none; border-bottom: 2px solid transparent; border-radius: 0; letter-spacing: -0.01em;
}
.stTabs [aria-selected="true"] {
    color: #0f172a !important; border-bottom: 2.5px solid #1d4ed8 !important; background: transparent !important;
}

/* ─── METRICS ─── */
[data-testid="stMetric"] {
    background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px;
    padding: 18px 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 1px 1px rgba(0,0,0,0.02);
    transition: box-shadow 0.15s ease;
}
[data-testid="stMetric"]:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.07); }
[data-testid="stMetricLabel"] {
    font-size: 11px !important; font-weight: 600 !important; color: #64748b !important;
    text-transform: uppercase; letter-spacing: 0.07em;
}
[data-testid="stMetricValue"] {
    font-size: 1.9rem !important; font-weight: 600 !important; color: #0f172a !important;
    font-family: 'DM Mono', monospace !important; letter-spacing: -0.03em;
}
[data-testid="stMetricDelta"] { font-size: 12px !important; font-weight: 500 !important; }

/* ─── BUTTONS MAIN ─── */
.stButton > button, .stDownloadButton > button {
    background: #1d4ed8; color: white; border: none; border-radius: 7px;
    padding: 9px 18px; font-weight: 500; font-size: 13.5px;
    transition: all 0.15s ease; box-shadow: 0 1px 2px rgba(29,78,216,0.3);
}
.stButton > button:hover, .stDownloadButton > button:hover {
    background: #1e40af; color: white;
    box-shadow: 0 4px 12px rgba(29,78,216,0.35); transform: translateY(-1px);
}

/* ─── FILE UPLOADER ─── */
[data-testid="stFileUploader"] section {
    border: 1.5px dashed #cbd5e1; border-radius: 8px;
    background: #f8fafc; padding: 1rem; transition: all 0.15s;
}
[data-testid="stFileUploader"] section:hover { border-color: #1d4ed8; background: #eff6ff; }

/* ─── DATAFRAME ─── */
[data-testid="stDataFrame"] {
    border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

/* ─── ALERTES ─── */
.alerte {
    background: white; border: 1px solid #e2e8f0; border-left: 3.5px solid;
    border-radius: 8px; padding: 14px 18px; margin-bottom: 10px;
    transition: all 0.15s; box-shadow: 0 1px 2px rgba(0,0,0,0.03);
}
.alerte:hover { box-shadow: 0 3px 8px rgba(0,0,0,0.07); }
.alerte.CRITIQUE  { border-left-color: #dc2626; }
.alerte.ATTENTION { border-left-color: #d97706; }
.alerte.INFO      { border-left-color: #2563eb; }
.alerte-tag {
    display: inline-block; padding: 2px 9px; font-size: 10px; font-weight: 700;
    letter-spacing: 0.07em; text-transform: uppercase; border-radius: 4px; margin-right: 8px;
    font-family: 'DM Mono', monospace;
}
.alerte-tag.CRITIQUE  { background: #fef2f2; color: #991b1b; }
.alerte-tag.ATTENTION { background: #fffbeb; color: #92400e; }
.alerte-tag.INFO      { background: #eff6ff; color: #1e40af; }
.alerte-message { font-weight: 600; color: #0f172a; font-size: 13.5px; margin-bottom: 6px; }
.alerte-cause, .alerte-reco { font-size: 12.5px; color: #475569; line-height: 1.55; margin-top: 4px; }
.alerte-label {
    font-weight: 600; color: #64748b; font-size: 10px; text-transform: uppercase;
    letter-spacing: 0.06em; margin-right: 4px; font-family: 'DM Mono', monospace;
}

/* ─── INFO BOX ─── */
.info-box {
    background: white; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 28px 32px; margin: 1rem 0; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.info-box h3 { margin-top: 0; }
.info-box ol { color: #475569; line-height: 1.85; }

header[data-testid="stHeader"] { background: transparent; }
.stSelectbox label { font-size: 13px; font-weight: 500; color: #374151; }

/* ─── SIDEBAR KPI ─── */
.sb-kpi {
    display: flex; justify-content: space-between; align-items: center;
    padding: 9px 16px; border-radius: 7px; background: #1e293b; margin-bottom: 6px;
}
.sb-kpi-label { font-size: 12px; color: #64748b; font-weight: 500; letter-spacing: 0.02em; }
.sb-kpi-value {
    font-size: 14px; font-weight: 600; font-family: 'DM Mono', monospace;
    color: #e2e8f0; letter-spacing: -0.02em;
}
.sb-kpi-value.warn { color: #fbbf24; }
.sb-kpi-value.ok   { color: #34d399; }
.sb-kpi-value.bad  { color: #f87171; }

.sb-section {
    font-size: 10px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase;
    color: #475569; padding: 0 4px; margin: 18px 0 8px; font-family: 'DM Mono', monospace;
}

.sb-logo {
    padding: 20px 20px 16px; border-bottom: 1px solid #1e293b; margin-bottom: 4px;
    display: flex; justify-content: center; align-items: center;
}
.sb-logo-title { font-size: 15px; font-weight: 600; color: #f1f5f9; letter-spacing: -0.02em; margin-bottom: 3px; }
.sb-logo-sub   { font-size: 11.5px; color: #475569; font-weight: 400; }
.sb-logo-badge {
    display: inline-block; margin-top: 10px; background: #1e3a5f; color: #60a5fa;
    font-size: 10px; font-weight: 600; letter-spacing: 0.07em; text-transform: uppercase;
    padding: 3px 9px; border-radius: 4px; font-family: 'DM Mono', monospace; border: 1px solid #1d4ed8;
}

.sb-bottom {
    padding: 16px 20px; border-top: 1px solid #1e293b; margin-top: 16px;
}
.sb-bottom-text { font-size: 11px; color: #334155; line-height: 1.6; }
.sb-kpi-block { padding: 0 12px; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("""
    <div class="sb-logo">
        <svg width="160" height="100" viewBox="0 0 160 100" role="img" xmlns="http://www.w3.org/2000/svg">
            <title>MécaOpt — Ligne de Fabrication</title>
            <!-- Engrenage -->
            <circle cx="80" cy="34" r="16" fill="none" stroke="#7c3aed" stroke-width="1.5"/>
            <circle cx="80" cy="34" r="8" fill="#7c3aed" opacity="0.2"/>
            <circle cx="80" cy="34" r="4" fill="#a78bfa"/>
            <!-- Dents engrenage -->
            <rect x="77" y="14" width="6" height="5" rx="1" fill="#7c3aed"/>
            <rect x="77" y="49" width="6" height="5" rx="1" fill="#7c3aed"/>
            <rect x="59" y="31" width="5" height="6" rx="1" fill="#7c3aed"/>
            <rect x="96" y="31" width="5" height="6" rx="1" fill="#7c3aed"/>
            <rect x="63" y="19" width="5" height="5" rx="1" fill="#7c3aed" transform="rotate(45 65.5 21.5)"/>
            <rect x="63" y="44" width="5" height="5" rx="1" fill="#7c3aed" transform="rotate(-45 65.5 46.5)"/>
            <rect x="92" y="19" width="5" height="5" rx="1" fill="#7c3aed" transform="rotate(-45 94.5 21.5)"/>
            <rect x="92" y="44" width="5" height="5" rx="1" fill="#7c3aed" transform="rotate(45 94.5 46.5)"/>
            <!-- Barre TRS -->
            <rect x="30" y="60" width="88" height="5" rx="2.5" fill="#334155"/>
            <rect x="30" y="60" width="75" height="5" rx="2.5" fill="#a78bfa"/>
            <text x="122" y="65" font-size="8" fill="#a78bfa" font-family="system-ui" font-weight="600">85%</text>
            <!-- Nom -->
            <text x="80" y="82" text-anchor="middle" font-size="13" font-weight="700" fill="#f1f5f9" font-family="system-ui" letter-spacing="2.5">MÉCAOPT</text>
            <text x="80" y="95" text-anchor="middle" font-size="7.5" fill="#64748b" font-family="system-ui" letter-spacing="1.2">LIGNE DE FABRICATION</text>
        </svg>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-section" style="padding: 0 20px; margin-top: 18px; margin-bottom: 10px;">Données d\'entrée</div>', unsafe_allow_html=True)

    st.markdown('<div style="padding: 0 12px;">', unsafe_allow_html=True)
    template_bytes = generer_template_excel()
    st.download_button(
        label="↓  Télécharger le template Excel",
        data=template_bytes,
        file_name="template_ligne_fab.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div style="padding: 0 12px; margin-top: 8px;">', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Importer un fichier Excel",
        type=["xlsx"],
        help="Le fichier doit contenir les feuilles 'Postes' et 'Parametres'.",
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div style="padding: 0 12px; margin-top: 8px;">', unsafe_allow_html=True)
    use_demo = st.checkbox("Utiliser les données de démonstration", value=not uploaded)
    st.markdown("</div>", unsafe_allow_html=True)

    kpi_placeholder = st.empty()

    st.markdown("""
    <div class="sb-bottom">
        <div class="sb-bottom-text">
            Département Génie Industriel<br>
            Projet arbre mécanique · 2025–2026
        </div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================
postes = None
params = None
err = None

if uploaded:
    try:
        postes, params = charger_excel(uploaded.read())
    except ExcelStructureError as e:
        err = str(e)
elif use_demo:
    postes, params = charger_excel(template_bytes)

if err:
    st.error(f"Erreur dans le fichier Excel : {err}")
    st.stop()

if not postes:
    st.markdown('<h1>Optimisation de Ligne de Fabrication</h1>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Analyse, diagnostic et simulation de scénarios d\'amélioration</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
      <h3 style="margin-top: 0;">Démarrer l'analyse</h3>
      <ol>
        <li>Téléchargez le <strong>template Excel</strong> via le bouton dans la barre latérale.</li>
        <li>Remplissez le fichier avec les données de votre ligne de production :
          <ul>
            <li><em>Feuille Postes</em> : numéro, opération, machine, temps, nombre de machines</li>
            <li><em>Feuille Parametres</em> : demande client, temps de travail, taux de rebut, taux d'arrêt, taille de lot</li>
          </ul>
        </li>
        <li>Importez le fichier rempli dans la barre latérale.</li>
        <li>L'application calcule automatiquement les indicateurs et identifie les goulots.</li>
      </ol>
      <div style="color: #64748b; font-size: 13px; margin-top: 1rem;">
        Vous pouvez également cocher <strong>« Utiliser les données de démonstration »</strong> pour explorer l'application avec un cas d'étude pré-configuré.
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ============================================================
# CALCULS BASELINE
# ============================================================
res_baseline = calculs.simuler(postes, params, "Baseline")
res_baseline.alertes = alertes.generer_alertes(res_baseline)


# ============================================================
# SIDEBAR — KPIs live
# ============================================================
trs_val = res_baseline.trs * 100
cap_val = int(res_baseline.pieces_conformes)
dem_val = int(params.demande_client_jour)
deficit_val = res_baseline.deficit

trs_cls = "ok" if trs_val >= 85 else "warn" if trs_val >= 75 else "bad"
cap_cls = "ok" if cap_val >= dem_val else "bad"
def_cls = "ok" if deficit_val <= 0 else "bad"
lt_val  = int(res_baseline.lead_time)
lt_cls  = "ok" if lt_val <= 120 else "warn"
nb_alertes = len(res_baseline.alertes)
al_cls  = "ok" if nb_alertes == 0 else "warn" if nb_alertes <= 2 else "bad"

kpi_placeholder.markdown(f"""
<div style="border-top: 1px solid #1e293b; border-bottom: 1px solid #1e293b; padding: 14px 0; margin: 4px 0;">
  <div class="sb-section" style="padding: 0 20px; margin-top: 0; margin-bottom: 10px;">Indicateurs clés</div>
  <div class="sb-kpi-block">
    <div class="sb-kpi">
      <span class="sb-kpi-label">TRS / OEE</span>
      <span class="sb-kpi-value {trs_cls}">{trs_val:.1f} %</span>
    </div>
    <div class="sb-kpi">
      <span class="sb-kpi-label">Capacité réelle</span>
      <span class="sb-kpi-value {cap_cls}">{cap_val} pcs/j</span>
    </div>
    <div class="sb-kpi">
      <span class="sb-kpi-label">Demande client</span>
      <span class="sb-kpi-value">{dem_val} pcs/j</span>
    </div>
    <div class="sb-kpi">
      <span class="sb-kpi-label">Déficit</span>
      <span class="sb-kpi-value {def_cls}">{'+' if deficit_val > 0 else ''}{deficit_val:.0f} pcs/j</span>
    </div>
    <div class="sb-kpi">
      <span class="sb-kpi-label">Lead Time</span>
      <span class="sb-kpi-value {lt_cls}">{lt_val} min</span>
    </div>
    <div class="sb-kpi">
      <span class="sb-kpi-label">Goulot</span>
      <span class="sb-kpi-value warn">{res_baseline.poste_goulot.machine}</span>
    </div>
    <div class="sb-kpi">
      <span class="sb-kpi-label">Alertes actives</span>
      <span class="sb-kpi-value {al_cls}">{nb_alertes} alerte{'s' if nb_alertes > 1 else ''}</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================
st.markdown('<h1>Optimisation de Ligne de Fabrication</h1>', unsafe_allow_html=True)
st.markdown(
    f'<div class="subtitle">Sous-traitance mécanique · {len(postes)} postes · Demande : {int(params.demande_client_jour)} pcs/jour</div>',
    unsafe_allow_html=True
)


# ============================================================
# TABS
# ============================================================
tab_diag, tab_anim, tab_scen, tab_eco = st.tabs([
    "Diagnostic", "Simulation animée", "Scénarios d'amélioration", "Analyse économique"
])


# ============================================================
# TAB 1 : DIAGNOSTIC
# ============================================================
with tab_diag:
    st.markdown("## Indicateurs de performance")

    cols = st.columns(4)
    deficit = res_baseline.deficit
    deficit_label = f"Déficit de {deficit:.0f} pcs" if deficit > 0 else "Demande couverte"
    deficit_color = "inverse" if deficit > 0 else "normal"

    with cols[0]:
        st.metric("Capacité journalière", f"{res_baseline.pieces_conformes:.0f} pcs",
                  delta=deficit_label, delta_color=deficit_color)
    with cols[1]:
        trs_target = res_baseline.trs - 0.85
        st.metric("TRS / OEE", f"{res_baseline.trs*100:.1f} %",
                  delta=f"{trs_target*100:+.1f} pts vs cible 85%",
                  delta_color="normal" if trs_target >= 0 else "inverse")
    with cols[2]:
        st.metric("Lead Time", f"{res_baseline.lead_time:.0f} min",
                  delta=f"Lot de {params.taille_lot} pièces", delta_color="off")
    with cols[3]:
        st.metric("Goulot identifié", res_baseline.poste_goulot.machine,
                  delta=f"{res_baseline.t_goulot:.1f} min/pièce", delta_color="off")

    st.markdown("## Taux d'utilisation par poste")
    df_util = pd.DataFrame([
        {"Machine": p.machine,
         "Utilisation": res_baseline.taux_utilisation[p.numero] * 100,
         "Goulot": p.numero == res_baseline.poste_goulot.numero}
        for p in postes
    ])
    colors = ["#dc2626" if g else "#2563eb" for g in df_util["Goulot"]]
    fig_util = go.Figure()
    fig_util.add_trace(go.Bar(
        x=df_util["Machine"], y=df_util["Utilisation"],
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{v:.1f}%" for v in df_util["Utilisation"]],
        textposition="outside",
        textfont=dict(size=12, color="#374151", family="DM Sans"),
        hovertemplate="<b>%{x}</b><br>Utilisation : %{y:.1f}%<extra></extra>",
    ))
    fig_util.add_hline(y=85, line_dash="dot", line_color="#94a3b8", line_width=1.5,
        annotation_text="Cible 85%", annotation_position="right",
        annotation_font=dict(size=11, color="#64748b"))
    fig_util.update_layout(
        yaxis=dict(range=[0, 115], title="Utilisation (%)", gridcolor="#f1f5f9", zerolinecolor="#e2e8f0"),
        xaxis=dict(showgrid=False), height=360, plot_bgcolor="white", paper_bgcolor="white",
        showlegend=False, margin=dict(l=20, r=20, t=20, b=40),
        font=dict(family="DM Sans", size=12, color="#374151"))
    st.plotly_chart(fig_util, use_container_width=True)

    st.markdown("## Décomposition du TRS")
    cols = st.columns(3)
    with cols[0]:
        st.metric("Disponibilité (A)", f"{res_baseline.disponibilite*100:.1f} %",
                  delta="T_eff / T_dispo", delta_color="off")
    with cols[1]:
        st.metric("Performance (P)", f"{res_baseline.performance*100:.1f} %",
                  delta="Cadence réelle / théorique", delta_color="off")
    with cols[2]:
        st.metric("Qualité (Q)", f"{res_baseline.qualite*100:.1f} %",
                  delta="1 − taux de rebut", delta_color="off")

    st.markdown(
        f"## Alertes diagnostiques  <span style='color:#94a3b8; font-weight:400; font-size:0.85rem;'>"
        f"({len(res_baseline.alertes)} détectée{'s' if len(res_baseline.alertes) > 1 else ''})</span>",
        unsafe_allow_html=True)
    if not res_baseline.alertes:
        st.success("Aucune alerte. La ligne fonctionne dans les paramètres attendus.")
    else:
        for a in res_baseline.alertes:
            st.markdown(f"""
            <div class="alerte {a.niveau}">
              <div class="alerte-message">
                <span class="alerte-tag {a.niveau}">{a.niveau}</span>{a.message}
              </div>
              <div class="alerte-cause"><span class="alerte-label">Cause</span>{a.cause_chiffree}</div>
              <div class="alerte-reco"><span class="alerte-label">Action</span>{a.recommandation}</div>
            </div>
            """, unsafe_allow_html=True)


# ============================================================
# TAB 2 : ANIMATION
# ============================================================
with tab_anim:
    st.markdown("## Simulation visuelle de la production")
    st.markdown(
        '<div style="color: #64748b; font-size: 13.5px; margin-bottom: 1.5rem; line-height: 1.65;">'
        "Visualisation en temps réel du flux de pièces sur la ligne durant une journée de travail. "
        "Le poste goulot est mis en évidence — observez comment il limite la cadence globale. "
        "Les machines passent en jaune lors d'arrêts simulés selon le taux d'arrêt paramétré."
        "</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        scenario_anim = st.selectbox(
            "Scénario à simuler", list(scenarios.SCENARIOS.keys()),
            help="Modifie les paramètres de la ligne selon le scénario d'amélioration choisi.")

    p_anim, par_anim = scenarios.SCENARIOS[scenario_anim](postes, params)
    res_anim = calculs.simuler(p_anim, par_anim, scenario_anim)

    cols = st.columns(4)
    cols[0].metric("Goulot", res_anim.poste_goulot.machine, f"{res_anim.t_goulot:.1f} min/pièce", delta_color="off")
    cols[1].metric("Capacité théorique", f"{res_anim.capacite_prod:.0f} pcs/j")
    cols[2].metric("Conformes prévues", f"{res_anim.pieces_conformes:.0f} pcs/j")
    cols[3].metric("TRS prévu", f"{res_anim.trs*100:.1f} %")

    st.markdown("<br>", unsafe_allow_html=True)
    html = generer_animation_html(res_anim)
    components.html(html, height=720, scrolling=False)


# ============================================================
# TAB 3 : SCÉNARIOS
# ============================================================
with tab_scen:
    st.markdown("## Comparaison des scénarios d'amélioration")

    tous_resultats = []
    for nom, fn in scenarios.SCENARIOS.items():
        p, par = fn(postes, params)
        r = calculs.simuler(p, par, nom)
        tous_resultats.append(r)

    df_synthese = pd.DataFrame([{
        "Scénario": r.nom_scenario, "Goulot": r.poste_goulot.machine,
        "t_goulot (min)": round(r.t_goulot, 2), "Capacité (pcs/j)": round(r.capacite_prod, 1),
        "Conformes (pcs/j)": round(r.pieces_conformes, 1), "Déficit": round(r.deficit, 1),
        "TRS (%)": round(r.trs * 100, 1), "Lead Time (min)": int(round(r.lead_time, 0)),
    } for r in tous_resultats])
    st.dataframe(df_synthese, use_container_width=True, hide_index=True)

    st.markdown("## Production journalière")
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(
        name="Capacité brute", x=[r.nom_scenario for r in tous_resultats],
        y=[r.capacite_prod for r in tous_resultats],
        marker=dict(color="#cbd5e1", line=dict(width=0)),
        text=[f"{r.capacite_prod:.0f}" for r in tous_resultats], textposition="outside",
        textfont=dict(size=11, color="#64748b", family="DM Sans")))
    fig_comp.add_trace(go.Bar(
        name="Pièces conformes", x=[r.nom_scenario for r in tous_resultats],
        y=[r.pieces_conformes for r in tous_resultats],
        marker=dict(color="#2563eb", line=dict(width=0)),
        text=[f"{r.pieces_conformes:.0f}" for r in tous_resultats], textposition="outside",
        textfont=dict(size=11, color="#1e40af", family="DM Sans")))
    fig_comp.add_hline(y=params.demande_client_jour, line_dash="dot", line_color="#dc2626", line_width=1.5,
        annotation_text=f"Demande client : {int(params.demande_client_jour)}",
        annotation_position="top right", annotation_font=dict(size=11, color="#dc2626"))
    fig_comp.update_layout(
        barmode="group", height=420,
        yaxis=dict(title="Pièces / jour", gridcolor="#f1f5f9"),
        xaxis=dict(showgrid=False), plot_bgcolor="white", paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=40, b=40), font=dict(family="DM Sans", size=12, color="#374151"))
    st.plotly_chart(fig_comp, use_container_width=True)

    st.markdown("## TRS par scénario")
    fig_trs = go.Figure()
    fig_trs.add_trace(go.Bar(
        x=[r.nom_scenario for r in tous_resultats], y=[r.trs * 100 for r in tous_resultats],
        marker=dict(color=[r.trs * 100 for r in tous_resultats],
                    colorscale=[[0, "#94a3b8"], [0.5, "#2563eb"], [1, "#059669"]], line=dict(width=0)),
        text=[f"{r.trs*100:.1f}%" for r in tous_resultats], textposition="outside",
        textfont=dict(size=11, color="#374151", family="DM Sans")))
    fig_trs.add_hline(y=85, line_dash="dot", line_color="#94a3b8", line_width=1.5,
        annotation_text="Cible industrielle 85%", annotation_position="right",
        annotation_font=dict(size=11, color="#64748b"))
    fig_trs.update_layout(
        yaxis=dict(range=[80, 100], title="TRS (%)", gridcolor="#f1f5f9"),
        xaxis=dict(showgrid=False), height=360, plot_bgcolor="white", paper_bgcolor="white",
        showlegend=False, margin=dict(l=20, r=20, t=20, b=40),
        font=dict(family="DM Sans", size=12, color="#374151"))
    st.plotly_chart(fig_trs, use_container_width=True)


# ============================================================
# TAB 4 : ÉCONOMIE
# ============================================================
with tab_eco:
    st.markdown("## Analyse économique")

    res_base = tous_resultats[0]
    eco_data = []
    for r in tous_resultats:
        invest = scenarios.INVESTISSEMENTS.get(r.nom_scenario, 0)
        eco = scenarios.calculer_economie(res_base.pieces_conformes, r.pieces_conformes, params, invest)
        eco_data.append({
            "Scénario": r.nom_scenario,
            "Δ Pièces/j": f"{eco['delta_pieces']:+.1f}" if eco['delta_pieces'] != 0 else "—",
            "Investissement (€)": f"{eco['investissement']:,.0f}".replace(",", " "),
            "Gain annuel (€)": f"{eco['gain_annuel']:,.0f}".replace(",", " "),
            "ROI (%)": f"{eco['roi_pct']:.1f}" if eco['roi_pct'] != 0 else "—",
            "Retour (jours)": f"{eco['retour_jours']:.0f}" if eco['retour_jours'] > 0 else "—",
            "Gain net 3 ans (€)": f"{eco['gain_3_ans']:,.0f}".replace(",", " "),
        })
    df_eco = pd.DataFrame(eco_data)
    st.dataframe(df_eco, use_container_width=True, hide_index=True)

    st.markdown("### Hypothèses économiques")
    cols = st.columns(4)
    with cols[0]:
        st.metric("Prix de vente unitaire", f"{params.prix_vente_unitaire:.0f} €", delta_color="off")
    with cols[1]:
        st.metric("Coût variable unitaire", f"{params.cout_variable_unitaire:.0f} €", delta_color="off")
    with cols[2]:
        st.metric("Marge unitaire",
                  f"{params.prix_vente_unitaire - params.cout_variable_unitaire:.0f} €",
                  delta_color="off")
    with cols[3]:
        st.metric("Jours ouvrés / an", f"{params.jours_ouvres_an}", delta_color="off")