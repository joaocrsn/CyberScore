import hmac
import os
import random
import re
import tomllib
from html import escape
from pathlib import Path


import pandas as pd
import streamlit as st
from groq import Groq

import legal
from repositorio import TAMANHO_MINIMO_GRUPO, Repositorio, gerar_codigo, normalizar_codigo




# ============================================================
# CONFIGURAÇÕES GERAIS E TEMA VISUAL
# ============================================================

st.set_page_config(page_title="Central de Segurança", page_icon="🔐", layout="centered")


ARQUIVO_SEGREDOS = Path(__file__).resolve().parent / ".streamlit" / "secrets.toml"


def segredo(nome, padrao=""):
    """Busca a configuração `nome` (ex.: "GROQ_API_KEY") — nunca deixe a chave em si no código.

    Ordem: st.secrets (pasta de onde o comando foi rodado / Streamlit Cloud),
    .streamlit/secrets.toml ao lado do app.py, e por fim variável de ambiente.
    """
    try:
        if nome in st.secrets:
            return st.secrets[nome]
    except Exception:
        pass  # sem secrets.toml na pasta atual
    if ARQUIVO_SEGREDOS.exists():
        with open(ARQUIVO_SEGREDOS, "rb") as arquivo:
            valor = tomllib.load(arquivo).get(nome)
        if valor:
            return valor
    return os.environ.get(nome, padrao)


GROQ_API_KEY = segredo("GROQ_API_KEY")
# A Groq aposenta modelos com frequência: tenta em ordem até um responder.
# Lista atual: console.groq.com/docs/models
MODELOS_IA = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b"]
SENHA_ADMIN = segredo("SENHA_ADMIN")  # sem ela, a área administrativa fica desativada


CAMINHO_BANCO = Path(__file__).resolve().parent / "dados_seguranca.db"


# Paleta da marca
# Roxo (identidade) · Ciano (destaque secundário) · Verde/Âmbar/Vermelho (semântica)
COR_ROXO = "#8B5CF6"
COR_CIANO = "#22D3EE"


LOGO_SVG = """
<svg width="38" height="38" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
  <defs>
    <linearGradient id="lg" x1="6" y1="4" x2="42" y2="44" gradientUnits="userSpaceOnUse">
      <stop stop-color="#A78BFA"/><stop offset="1" stop-color="#22D3EE"/>
    </linearGradient>
  </defs>
  <path d="M24 4 L41 10 V23 C41 33 34 40 24 44 C14 40 7 33 7 23 V10 Z"
        stroke="url(#lg)" stroke-width="2.4" stroke-linejoin="round" fill="rgba(139,92,246,0.10)"/>
  <path d="M16 24.5 L22 30.5 L33 18" stroke="url(#lg)" stroke-width="3.2"
        stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""


st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');


        :root {
            --bg: #09090B;
            --surface: #131316;
            --surface-2: #1A1A1F;
            --border: #27272D;
            --border-strong: #62626E; /* contorno de campos e botões: ≥ 3:1 de contraste (WCAG 1.4.11) */
            --text: #ECECF1;
            --muted: #9A9AA8;
            --purple: #8B5CF6;
            --purple-soft: #A78BFA;
            --cyan: #22D3EE;
            --green: #10B981;
            --amber: #F59E0B;
            --red: #EF4444;
            --font-display: 'Space Grotesk', 'Inter', sans-serif;
            --font-body: 'Inter', system-ui, sans-serif;
            --font-mono: 'JetBrains Mono', ui-monospace, monospace;
        }


        /* ---------- Base ---------- */
        .stApp {
            background:
                radial-gradient(900px 480px at 85% -10%, rgba(139, 92, 246, 0.14), transparent 60%),
                radial-gradient(700px 420px at -5% 105%, rgba(34, 211, 238, 0.07), transparent 60%),
                var(--bg);
            color: var(--text);
            font-family: var(--font-body);
        }
        .stApp p, .stApp label, .stApp li, .stApp [data-testid="stMarkdownContainer"] {
            font-family: var(--font-body);
            color: var(--text);
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: var(--font-display) !important;
            color: var(--text) !important;
            letter-spacing: -0.02em;
        }
        h1 { font-weight: 700 !important; }
        h3 { font-weight: 600 !important; line-height: 1.35 !important; }
        [data-testid="stCaptionContainer"], .stApp small { color: var(--muted) !important; font-family: var(--font-mono); font-size: 12px; letter-spacing: 0.02em; }
        .block-container { padding-top: 3.2rem; max-width: 760px; }
        hr { border-color: var(--border) !important; }


        /* ---------- Cabeçalho do Streamlit discreto, mas funcional ---------- */
        header[data-testid="stHeader"] {
            background: transparent !important;
            box-shadow: none !important;
            border: none !important;
            pointer-events: none !important;
        }
        header[data-testid="stHeader"] [data-testid="stToolbar"] {
            display: flex !important; visibility: visible !important; opacity: 1 !important;
            background: transparent !important; box-shadow: none !important; border: none !important;
            pointer-events: none !important;
        }
        [data-testid="stToolbarActions"], [data-testid="stToolbarActionButton"],
        [data-testid="stDeployButton"], .stDeployButton, .stAppDeployButton,
        [data-testid="stStatusWidget"], .stStatusWidget, [data-testid="stMainMenu"], #MainMenu {
            display: none !important; visibility: hidden !important; opacity: 0 !important; pointer-events: none !important;
        }
        footer, [data-testid="stFooter"], [data-testid="stDecoration"] {
            display: none !important; visibility: hidden !important;
        }


        /* ---------- Botão para reabrir/recolher a barra lateral ---------- */
        [data-testid="stExpandSidebarButton"], [data-testid="collapsedControl"] {
            display: flex !important; visibility: visible !important; opacity: 1 !important;
            position: fixed !important; top: 10px !important; left: 10px !important;
            width: 32px !important; height: 32px !important; min-width: 32px !important; min-height: 32px !important;
            align-items: center !important; justify-content: center !important;
            padding: 0 !important; margin: 0 !important;
            background-color: var(--surface) !important;
            border: 1px solid var(--border-strong) !important;
            border-radius: 8px !important;
            color: var(--purple) !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4) !important;
            pointer-events: auto !important; cursor: pointer !important;
            z-index: 1000001 !important; transition: all 0.2s ease !important;
        }
        [data-testid="stExpandSidebarButton"] button, [data-testid="collapsedControl"] button {
            background-color: transparent !important; border: none !important; color: var(--purple) !important;
            pointer-events: auto !important; cursor: pointer !important;
            display: flex !important; align-items: center !important; justify-content: center !important;
            width: 100% !important; height: 100% !important; padding: 0 !important; margin: 0 !important;
        }
        [data-testid="stExpandSidebarButton"]:hover, [data-testid="collapsedControl"]:hover {
            border-color: var(--purple) !important; box-shadow: 0 0 12px rgba(139, 92, 246, 0.45) !important;
        }
        [data-testid="stExpandSidebarButton"] svg, [data-testid="collapsedControl"] svg {
            color: var(--purple) !important; fill: var(--purple) !important; width: 16px !important; height: 16px !important;
        }
        [data-testid="stExpandSidebarButton"] span, [data-testid="collapsedControl"] span {
            color: var(--purple) !important; -webkit-text-fill-color: var(--purple) !important;
        }
        [data-testid="stSidebarCollapseButton"] { visibility: visible !important; opacity: 1 !important; pointer-events: auto !important; }
        [data-testid="stSidebarCollapseButton"] button {
            background-color: var(--surface) !important; border: 1px solid var(--border-strong) !important;
            border-radius: 8px !important; color: var(--purple) !important; pointer-events: auto !important;
        }
        [data-testid="stSidebarCollapseButton"] svg { color: var(--purple) !important; fill: var(--purple) !important; }


        /* ---------- Barra lateral ---------- */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #111114 0%, #0C0C0F 100%);
            border-right: 1px solid var(--border);
        }
        [data-testid="stSidebar"] * { color: var(--text); }
        .brand { display: flex; align-items: center; gap: 12px; padding: 6px 0 18px 0; border-bottom: 1px solid var(--border); margin-bottom: 18px; }
        .brand-name { font-family: var(--font-display); font-weight: 700; font-size: 19px; line-height: 1.1; color: var(--text); }
        .brand-name em { font-style: normal; background: linear-gradient(90deg, #A78BFA, #22D3EE); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }
        .brand-tag { font-family: var(--font-mono); font-size: 10.5px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--muted); margin-top: 3px; }
        .side-label { font-family: var(--font-mono); font-size: 10.5px; letter-spacing: 0.16em; text-transform: uppercase; color: var(--muted); margin: 4px 0 6px 2px; }
        [data-testid="stSidebar"] [role="radiogroup"] { gap: 4px; }
        [data-testid="stSidebar"] [data-testid="stRadioOption"] {
            padding: 9px 12px; border-radius: 10px; border: 1px solid transparent; transition: all 0.2s ease; width: 100%;
        }
        [data-testid="stSidebar"] [data-testid="stRadioOption"]:hover { background: var(--surface-2); border-color: var(--border); }
        [data-testid="stSidebar"] [data-testid="stRadioOption"]:has(input:checked) {
            background: linear-gradient(90deg, rgba(139, 92, 246, 0.18), rgba(139, 92, 246, 0.04));
            border-color: rgba(139, 92, 246, 0.45);
        }
        [data-testid="stSidebar"] [data-baseweb="radio"] > div:first-child, [data-testid="stSidebar"] [role="radiogroup"] input + div { border-color: var(--purple) !important; }
        [data-testid="stSidebar"] [role="radiogroup"] { opacity: 1 !important; visibility: visible !important; }
        [data-testid="stSidebar"] [data-testid="stRadioOption"] p { font-weight: 500; font-size: 14.5px; }


        /* ---------- Cabeçalho de página ---------- */
        .page-title { font-family: var(--font-display); font-weight: 700; font-size: 34px; line-height: 1.12; letter-spacing: -0.025em; color: var(--text); margin: 0 0 8px 0; }
        .page-sub { color: var(--muted); font-size: 15.5px; line-height: 1.55; margin: 0 0 26px 0; max-width: 560px; }


        /* ---------- Botões (cartões de resposta) ---------- */
        div.stButton > button {
            background-color: var(--surface);
            color: var(--text) !important;
            border: 1px solid var(--border-strong);
            border-radius: 14px;
            padding: 18px 22px;
            text-align: left;
            justify-content: flex-start;
            font-family: var(--font-body);
            font-size: 15.5px;
            font-weight: 500;
            line-height: 1.45;
            transition: all 0.22s ease;
            box-shadow: 0 2px 0 rgba(0, 0, 0, 0.35);
            width: 100%;
            margin-bottom: 6px;
        }
        div.stButton > button > div, div.stButton > button span { width: 100%; justify-content: flex-start !important; text-align: left !important; }
        div.stButton > button p { text-align: left !important; color: var(--text); }
        div.stButton > button:hover {
            border-color: var(--purple);
            background: linear-gradient(90deg, rgba(139, 92, 246, 0.16), rgba(139, 92, 246, 0.03) 70%), var(--surface);
            transform: translateX(4px);
            box-shadow: -4px 0 0 var(--purple), 0 10px 24px rgba(139, 92, 246, 0.14);
        }
        div.stButton > button:active { transform: translateX(2px); }
        div.stButton > button:focus-visible { outline: 2px solid var(--cyan); outline-offset: 2px; }
        div.stButton > button:disabled { opacity: 0.45; cursor: not-allowed; transform: none; box-shadow: none; }


        /* ---------- Barra de progresso ---------- */
        [data-testid="stProgressBarTrack"] { background-color: var(--surface-2) !important; height: 6px !important; border-radius: 999px !important; overflow: hidden; }
        [data-testid="stProgressBarTrack"] > div {
            background: linear-gradient(90deg, #8B5CF6, #22D3EE) !important;
            border-radius: 999px !important;
            box-shadow: 0 0 12px rgba(139, 92, 246, 0.5);
        }


        /* ---------- Inputs ---------- */
        .stTextArea textarea, .stTextInput input, [data-baseweb="select"] > div {
            background-color: var(--surface) !important;
            color: var(--text) !important;
            border: 1px solid var(--border-strong) !important;
            border-radius: 12px !important;
            font-family: var(--font-body);
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }
        .react-aria-ComboBox [role="group"], .react-aria-ComboBox input {
            background-color: var(--surface) !important; color: var(--text) !important;
            border-color: var(--border-strong) !important; border-radius: 12px !important;
        }
        .react-aria-ComboBox [role="group"]:focus-within { border-color: var(--purple) !important; box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.25) !important; }
        .react-aria-ComboBox button svg { color: var(--muted) !important; }
        [role="listbox"], [role="option"] { background-color: var(--surface-2) !important; color: var(--text) !important; }
        [role="option"][data-focused="true"], [role="option"]:hover, [role="option"][data-selected="true"] { background-color: rgba(139, 92, 246, 0.22) !important; }
        [data-baseweb="select"] div, [data-baseweb="select"] input { background-color: var(--surface) !important; color: var(--text) !important; }
        [data-baseweb="select"] svg { fill: var(--muted) !important; }
        [data-baseweb="popover"] ul, [data-baseweb="popover"] li, [data-baseweb="menu"] { background-color: var(--surface-2) !important; color: var(--text) !important; }
        [data-baseweb="popover"] li:hover, [data-baseweb="popover"] li[aria-selected="true"] { background-color: rgba(139, 92, 246, 0.2) !important; }
        .stTextArea textarea:focus, .stTextInput input:focus {
            border-color: var(--purple) !important;
            box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.25) !important;
        }
        .stSelectbox label, .stTextArea label, .stTextInput label {
            font-family: var(--font-mono) !important; font-size: 11.5px !important;
            letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted) !important;
        }


        /* ---------- Alertas ---------- */
        [data-testid="stAlert"] {
            background-color: var(--surface) !important; color: var(--text);
            border: 1px solid var(--border) !important; border-left: 3px solid var(--purple) !important;
            border-radius: 12px !important;
        }


        /* ---------- Métricas ---------- */
        [data-testid="stMetric"] {
            background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 16px 20px;
            position: relative; overflow: hidden;
        }
        [data-testid="stMetric"]::before {
            content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 3px;
            background: linear-gradient(180deg, #8B5CF6, #22D3EE);
        }
        [data-testid="stMetricLabel"] p { font-family: var(--font-mono) !important; font-size: 11px !important; letter-spacing: 0.14em; text-transform: uppercase; color: var(--muted) !important; }
        [data-testid="stMetricValue"] { font-family: var(--font-display) !important; font-weight: 700 !important; }


        /* ---------- Componentes customizados ---------- */
        .q-card { background: var(--surface); border: 1px solid var(--border); border-radius: 18px; padding: 22px 24px 20px 24px; margin: 6px 0 22px 0; position: relative; }
        .q-chip { display: inline-flex; align-items: center; gap: 8px; font-family: var(--font-mono); font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--purple-soft); background: rgba(139, 92, 246, 0.12); border: 1px solid rgba(139, 92, 246, 0.3); padding: 4px 10px; border-radius: 999px; margin-bottom: 14px; }
        .q-text { font-family: var(--font-display); font-weight: 600; font-size: 22px !important; line-height: 1.4 !important; letter-spacing: -0.015em; color: var(--text); margin: 0; padding: 0 !important; }
        .step-row { display: flex; justify-content: space-between; align-items: baseline; font-family: var(--font-mono); font-size: 12px; color: var(--muted); letter-spacing: 0.04em; margin: 4px 0 8px 0; }
        .step-row b { color: var(--text); font-weight: 600; }


        .score-card { position: relative; display: flex; align-items: center; gap: 28px; background: var(--surface); border: 1px solid var(--border); border-radius: 22px; padding: 28px 30px; margin-bottom: 26px; overflow: hidden; }
        .score-card::before { content: ""; position: absolute; inset: 0; background: radial-gradient(420px 220px at 0% 0%, var(--glow), transparent 70%); opacity: 0.22; pointer-events: none; }
        .score-gauge { position: relative; flex: 0 0 auto; width: 168px; height: 168px; }
        .score-gauge svg { transform: rotate(-90deg); }
        .score-gauge .center { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
        .score-num { font-family: var(--font-display); font-weight: 700; font-size: 46px; line-height: 1; letter-spacing: -0.03em; }
        .score-den { font-family: var(--font-mono); font-size: 11.5px; color: var(--muted); margin-top: 4px; letter-spacing: 0.08em; }
        .score-info { position: relative; min-width: 0; }
        .score-kicker { font-family: var(--font-mono); font-size: 11px; letter-spacing: 0.18em; text-transform: uppercase; color: var(--muted); margin-bottom: 8px; }
        .score-class { font-family: var(--font-display); font-weight: 700; font-size: 28px; letter-spacing: -0.02em; line-height: 1.1; margin: 0 0 8px 0; }
        .score-msg { color: var(--muted); font-size: 15px; line-height: 1.5; margin: 0 0 14px 0; }
        .score-meta { display: inline-flex; gap: 8px; flex-wrap: wrap; }
        .tag { font-family: var(--font-mono); font-size: 11px; letter-spacing: 0.06em; color: var(--text); background: var(--surface-2); border: 1px solid var(--border-strong); padding: 4px 10px; border-radius: 8px; }
        .section-title { display: flex; align-items: center; gap: 10px; font-family: var(--font-display); font-weight: 600; font-size: 20px !important; letter-spacing: -0.015em; margin: 26px 0 10px 0; padding: 0 !important; color: var(--text); }
        .section-title::before { content: ""; width: 4px; height: 20px; border-radius: 2px; background: linear-gradient(180deg, #8B5CF6, #22D3EE); }
        .bloco-card { background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 14px 20px; }
        .bloco-row { display: grid; grid-template-columns: 190px 1fr 46px; align-items: center; gap: 14px; padding: 8px 0; }
        .bloco-nome { font-size: 14px; font-weight: 500; }
        .bloco-barra { height: 8px; background: var(--surface-2); border-radius: 999px; overflow: hidden; }
        .bloco-barra > div { height: 100%; border-radius: 999px; }
        .bloco-pct { font-family: var(--font-mono); font-size: 13px; font-weight: 600; text-align: right; }
        /* ---------- Resposta a incidentes ---------- */
        [data-testid="stBaseButton-primary"] {
            border-color: var(--purple) !important;
            background: linear-gradient(90deg, rgba(139, 92, 246, 0.28), rgba(139, 92, 246, 0.06)) !important;
            box-shadow: -4px 0 0 var(--purple) !important;
        }
        .protocolo { list-style: none; padding: 0; margin: 4px 0 8px 0; }
        .protocolo li { display: flex; gap: 16px; padding: 14px 0; border-bottom: 1px solid var(--border); }
        .protocolo li:last-child { border-bottom: none; }
        .passo-num { flex: 0 0 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
            font-family: var(--font-display); font-weight: 700; color: var(--bg); background: linear-gradient(135deg, #A78BFA, #22D3EE); }
        .protocolo b { font-family: var(--font-display); font-size: 16px; }
        .protocolo p { margin: 4px 0 0 0; color: var(--muted) !important; font-size: 14.5px; line-height: 1.5; }
        .cartilhas { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 10px; margin: 6px 0 12px 0; }
        .cartilha { display: flex; flex-direction: column; gap: 4px; padding: 12px 14px; border-radius: 12px; text-decoration: none !important;
            background: var(--surface-2); border: 1px solid var(--border-strong); transition: border-color 0.2s ease, transform 0.2s ease; }
        .cartilha:hover { border-color: var(--cyan); transform: translateY(-2px); }
        .cartilha-titulo { color: var(--text); font-weight: 600; font-size: 14px; line-height: 1.35; }
        .cartilha-fonte { color: var(--cyan); font-family: var(--font-mono); font-size: 11px; letter-spacing: 0.06em; }
        .codigo-card { background: rgba(34, 211, 238, 0.08); border: 1px solid var(--cyan); border-radius: 14px; padding: 16px 20px 6px 20px; margin-bottom: 8px; }
        .codigo-titulo { font-family: var(--font-display); font-weight: 700; font-size: 18px; color: var(--cyan); margin-bottom: 6px; }
        .sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0; }

        /* ---------- Acessibilidade ---------- */
        [data-testid="stHeaderActionElements"] { display: none !important; } /* ícone de âncora nos títulos */
        a:focus-visible, summary:focus-visible, [role="tab"]:focus-visible, input:focus-visible,
        textarea:focus-visible, label:has(input:focus-visible) {
            outline: 2px solid var(--cyan) !important; outline-offset: 2px; border-radius: 8px;
        }
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after { transition: none !important; animation: none !important; }
            div.stButton > button:hover, .cartilha:hover { transform: none !important; }
        }
        @media (max-width: 560px) {
            .bloco-row { grid-template-columns: 1fr 46px; }
            .bloco-barra { grid-column: 1 / -1; grid-row: 2; }
            .score-card { flex-direction: column; text-align: center; padding: 24px 18px; }
            .page-title { font-size: 28px; }
            .q-text { font-size: 19px; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)




def html(texto):
    """Remove indentação/linhas vazias para o Markdown não tratar o HTML como bloco de código."""
    return "\n".join(l.strip() for l in texto.splitlines() if l.strip())




def cabecalho_pagina(titulo, subtitulo=""):
    sub = f'<p class="page-sub">{escape(subtitulo)}</p>' if subtitulo else ""
    st.markdown(
        f'<h1 class="page-title">{escape(titulo)}</h1>{sub}',
        unsafe_allow_html=True,
    )




def titulo_secao(texto):
    st.markdown(f'<h2 class="section-title">{escape(texto)}</h2>', unsafe_allow_html=True)




# ============================================================
# BANCO DE DADOS (via repositorio.py, que aplica as regras de isolamento)
# ============================================================


@st.cache_resource
def obter_repositorio(versao_modulo):
    # versao_modulo muda quando repositorio.py é atualizado: evita reaproveitar a classe antiga da memória.
    # Local: SQLite na pasta do projeto. Produção: DATABASE_URL do Supabase (Postgres) no secrets.
    url = segredo("DATABASE_URL", f"sqlite:///{CAMINHO_BANCO.as_posix()}")
    return Repositorio(url, segredo("PIMENTA_CODIGO"))


try:
    repo = obter_repositorio(id(Repositorio))
except Exception as erro:
    print(f"[banco] falha ao conectar: {erro}")  # detalhes só no log do servidor, nunca na tela
    st.error("O serviço está temporariamente indisponível. Tente novamente em alguns minutos.")
    st.stop()




# ============================================================
# DADOS DO DIAGNÓSTICO E SESSÃO
# ============================================================


SETORES = ["Corporativo", "Pessoal", "Governamental"]
AREAS = [
    "Tecnologia da Informação (TI)", "Administrativo / Operacional", "Financeiro / Contabilidade",
    "Recursos Humanos (RH)", "Saúde e Bem-estar", "Educação / Ensino", "Jurídico / Compliance",
    "Marketing / Comunicação", "Vendas / Comercial", "Atendimento ao Cliente / Suporte",
    "Engenharia / Arquitetura", "Logística / Suprimentos", "Segurança (Pública ou Privada)",
    "Diretoria / Alta Gestão (C-Level)", "Estudante", "Não se aplica", "Outros"
]


# Versão 3: 15 situações do dia a dia focadas em "falsa sensação de segurança", só de prevenção
# (a reação a incidentes fica no módulo de Consultoria). 5 blocos de 3 perguntas.
# Cada pergunta tem um peso (soma = 1000) e cada opção um fator de 0 a 1.
# Pontos da opção = peso × fator. Peso reflete impacto × frequência do golpe.
# "cartilhas" usa as chaves do dicionário CARTILHAS, definido mais abaixo.
VERSAO_QUESTIONARIO = 3

PERGUNTAS = [
    # ---------- Bloco 1: Golpes por mensagem e ligação (250) ----------
    {
        "tema": "repassar código recebido por SMS",
        "bloco": "Golpes por mensagem e ligação",
        "peso": 80,
        "pergunta": "Alguém do grupo do condomínio diz que mandou um código de 6 dígitos para o seu número por engano e pede que você repasse. O que você faz?",
        "opcoes": [
            ("Repasso, afinal o código é dele, não meu.", 0),
            ("Ligo para a pessoa e, se ela confirmar, repasso.", 0.25),
            ("Não repasso: código que chega no meu celular é só meu.", 1),
        ],
        "armadilha": "Esse código é a chave para instalar o SEU WhatsApp em outro celular. Com ele, o golpista assume sua conta e pede Pix para todos os seus contatos. Confirmar com a pessoa não ajuda: o próprio pedido já é o golpe, e a conta dela pode ter sido invadida.",
        "dica": "Nunca repasse códigos e ative a confirmação em duas etapas: WhatsApp > Configurações > Conta > Confirmação em duas etapas.",
        "cartilhas": ["golpes", "autenticacao"],
    },
    {
        "tema": "confirmar pedido de Pix de parente",
        "bloco": "Golpes por mensagem e ligação",
        "peso": 90,
        "pergunta": "Um parente escreve de um número novo (\"troquei de celular\") e pede um Pix urgente. Como você confirma que é ele?",
        "opcoes": [
            ("Pela foto do perfil e pelo jeito de escrever.", 0),
            ("Peço um áudio e confiro se a voz é dele.", 0.25),
            ("Faço uma pergunta que só ele saberia responder.", 0.5),
            ("Ligo para o número antigo ou faço chamada de vídeo.", 1),
        ],
        "armadilha": "Foto e jeito de escrever se copiam em minutos, e a voz hoje é clonada por IA com poucos segundos de gravação, tirados de vídeos ou áudios antigos. Perguntas pessoais ajudam, mas muitas respostas estão nas redes sociais.",
        "dica": "Combine uma \"palavra-senha\" com a família para emergências e confirme sempre por um canal que você já conhecia antes.",
        "cartilhas": ["golpes", "febraban"],
    },
    {
        "tema": "falsa central do banco com app de acesso remoto",
        "bloco": "Golpes por mensagem e ligação",
        "peso": 80,
        "pergunta": "Ligam da \"central de segurança do seu banco\". Sabem seu nome, CPF e final do cartão, e pedem que você instale um app para \"proteger a conta\". O que você faz?",
        "opcoes": [
            ("Instalo: se sabem meus dados, é o banco.", 0),
            ("Peço o número de protocolo antes de instalar.", 0.25),
            ("Desligo e ligo de volta no número que apareceu.", 0.25),
            ("Desligo e falo com o banco pelo app ou pelo cartão.", 1),
        ],
        "armadilha": "Nome, CPF e final do cartão circulam em vazamentos: saber seus dados não prova nada. O app pedido é de acesso remoto, que deixa o golpista controlar seu celular e fazer transferências (a \"mão fantasma\"). O número na tela pode ser falsificado, e protocolo qualquer um inventa.",
        "dica": "Banco não liga pedindo para instalar app, transferir dinheiro ou informar senha. Desligue e procure o banco pelo app ou pelo número do verso do cartão, de preferência de outro telefone.",
        "cartilhas": ["fraudes", "banco"],
    },
    # ---------- Bloco 2: Links, compras e ofertas (180) ----------
    {
        "tema": "SMS de encomenda retida com taxa",
        "bloco": "Links, compras e ofertas",
        "peso": 60,
        "pergunta": "Você está esperando uma compra e chega um SMS: \"Sua encomenda está retida. Pague a taxa de R$ 7,90 para liberar\", com um link. O que você faz?",
        "opcoes": [
            ("Pago: estava esperando a entrega e o valor é baixo.", 0),
            ("Abro o link para ver se o site parece oficial.", 0.25),
            ("Confiro o rastreio no site ou app da loja onde comprei.", 1),
        ],
        "armadilha": "O golpe funciona justamente porque muita gente está esperando alguma entrega, e o valor baixo desarma a desconfiança. O objetivo não são os R$ 7,90: é roubar os dados do seu cartão. Só abrir o link já pode levar a uma página falsa idêntica à oficial.",
        "dica": "Nunca pague taxas por links recebidos. Acompanhe a entrega só pelo app ou site da loja ou da transportadora, digitando o endereço você mesmo.",
        "cartilhas": ["golpes", "comercio"],
    },
    {
        "tema": "confiar em loja online desconhecida",
        "bloco": "Links, compras e ofertas",
        "peso": 60,
        "pergunta": "Você achou um produto bem mais barato numa loja que não conhecia. O que mais te faz confiar no site?",
        "opcoes": [
            ("Apareceu como anúncio no Instagram ou no topo do Google.", 0),
            ("Tem o cadeado (https) na barra do navegador.", 0.25),
            ("Tem muitas avaliações positivas na página do produto.", 0.25),
            ("O CNPJ existe e a reputação no Reclame Aqui é boa.", 1),
        ],
        "armadilha": "O cadeado só mostra que a conexão é criptografada, e sites falsos também têm. Anúncios são pagos por qualquer um, e avaliações na própria página são fáceis de forjar.",
        "dica": "Desconfie de preço muito abaixo do mercado, pesquise o CNPJ e a reputação fora do site e prefira cartão virtual, que dá para contestar. Evite Pix em loja desconhecida.",
        "cartilhas": ["comercio"],
    },
    {
        "tema": "falsa oferta de renda extra",
        "bloco": "Links, compras e ofertas",
        "peso": 60,
        "pergunta": "Oferecem renda extra para curtir vídeos ou avaliar produtos. Nas primeiras tarefas, o pagamento cai mesmo. Depois pedem um \"investimento\" para liberar tarefas que pagam mais. O que você faz?",
        "opcoes": [
            ("Invisto: já recebi antes, então é confiável.", 0),
            ("Continuo só nas tarefas grátis, sem pagar nada.", 0.25),
            ("Paro: trabalho de verdade não cobra para você trabalhar.", 1),
        ],
        "armadilha": "Os primeiros pagamentos são a isca: servem para provar que \"funciona\" e preparar o pedido maior. Mesmo sem pagar, quem continua entrega dados pessoais e chave Pix, que podem ser usados em outros golpes ou para movimentar dinheiro de fraudes.",
        "dica": "Qualquer \"trabalho\" que exige pagamento para continuar é golpe. Saia do grupo, não indique para ninguém e denuncie o perfil na plataforma.",
        "cartilhas": ["fraudes", "golpes"],
    },
    # ---------- Bloco 3: Contas e pagamentos (240) ----------
    {
        "tema": "senha forte, mas repetida",
        "bloco": "Contas e pagamentos",
        "peso": 90,
        "pergunta": "Como são as senhas das suas contas mais importantes (e-mail, banco, redes sociais)?",
        "opcoes": [
            ("Uma senha bem forte, com símbolos, que uso nas principais.", 0),
            ("Uma base que mudo um pouco em cada site (ex.: Maria@1990insta).", 0.25),
            ("Senhas diferentes, anotadas num caderno que fica em casa.", 0.75),
            ("Senhas diferentes, criadas e guardadas pelo celular ou por um gerenciador.", 1),
        ],
        "armadilha": "Senha forte não adianta se for repetida: quando um site vaza, golpistas testam a mesma senha (e variações óbvias) em todos os outros. Já o caderno em casa é mais seguro do que parece: quem ataca pela internet não tem acesso a ele.",
        "dica": "Use o gerenciador que já vem no celular (Google ou iCloud) e comece trocando a senha do e-mail, porque é por ele que se recuperam todas as outras.",
        "cartilhas": ["autenticacao"],
    },
    {
        "tema": "verificação em duas etapas no e-mail",
        "bloco": "Contas e pagamentos",
        "peso": 90,
        "pergunta": "Quando você entra no seu e-mail principal num celular ou computador novo, o que é pedido?",
        "opcoes": [
            ("Só a senha, mais nada.", 0),
            ("Não sei dizer, nunca reparei.", 0),
            ("A senha e um código por SMS.", 0.75),
            ("A senha e uma confirmação no meu celular.", 1),
        ],
        "armadilha": "Sem a verificação em duas etapas, basta a senha vazar para alguém entrar no seu e-mail, que é a \"chave mestra\" de todas as outras contas. O código por SMS já protege muito, mas pode ser desviado em golpes de troca de chip.",
        "dica": "Ative a verificação em duas etapas no e-mail (Conta Google > Segurança, ou ID Apple > Início de sessão e segurança) e depois no banco e nas redes sociais.",
        "cartilhas": ["autenticacao"],
    },
    {
        "tema": "pagar boleto recebido por mensagem",
        "bloco": "Contas e pagamentos",
        "peso": 60,
        "pergunta": "Chega por e-mail ou WhatsApp o boleto da escola ou do condomínio, com o valor certinho. Antes de pagar, você…",
        "opcoes": [
            ("Pago: o valor está certo e eu esperava a cobrança.", 0),
            ("Confiro se quem mandou é o contato de sempre.", 0.25),
            ("Confiro o beneficiário na tela do banco antes de pagar.", 1),
        ],
        "armadilha": "Golpistas interceptam e-mails ou invadem contatos e mandam o boleto com valor e data certinhos. Só muda quem recebe o dinheiro. O remetente \"de sempre\" também pode ter sido invadido.",
        "dica": "Antes de digitar a senha, leia o nome do beneficiário. Se não for a empresa que você conhece, pare e peça a 2ª via pelo site ou app oficial.",
        "cartilhas": ["fraudes", "banco"],
    },
    # ---------- Bloco 4: Celular e apps (190) ----------
    {
        "tema": "documentos e senhas guardados no celular",
        "bloco": "Celular e apps",
        "peso": 60,
        "pergunta": "Você guarda no celular fotos de documentos (RG, CNH, cartão) ou senhas no bloco de notas?",
        "opcoes": [
            ("Sim, guardo os dois para facilitar.", 0),
            ("Só senhas no bloco de notas.", 0.25),
            ("Só fotos de documentos.", 0.5),
            ("Não guardo nenhum dos dois.", 1),
        ],
        "armadilha": "Para a maioria dos brasileiros, o celular virou carteira, cofre e identidade ao mesmo tempo. Se for roubado desbloqueado, o ladrão encontra na galeria e nas notas tudo o que precisa para abrir contas e fazer empréstimos em seu nome.",
        "dica": "Apague fotos de documentos e senhas anotadas, use a CNH e o RG digitais oficiais e guarde senhas num gerenciador. Cadastre o aparelho no Celular Seguro.",
        "cartilhas": ["furto", "celular_seguro"],
    },
    {
        "tema": "senha do app do banco igual à do celular",
        "bloco": "Celular e apps",
        "peso": 70,
        "pergunta": "Como você entra no app do banco no seu celular?",
        "opcoes": [
            ("Com a mesma senha que desbloqueia o celular.", 0),
            ("Com uma senha diferente, mas anotada no próprio celular.", 0.25),
            ("Com uma senha diferente, que só eu sei.", 1),
        ],
        "armadilha": "Quem rouba o celular testa a senha de desbloqueio em todos os apps, a começar pelos bancos. Senha anotada no aparelho tem o mesmo efeito. É o hábito que transforma um furto em prejuízo bancário.",
        "dica": "Use no banco uma senha que não exista em nenhum outro lugar e ative o PIN do chip, para impedir que o ladrão receba seus códigos por SMS.",
        "cartilhas": ["furto", "banco"],
    },
    {
        "tema": "permissões perigosas em apps da loja oficial",
        "bloco": "Celular e apps",
        "peso": 60,
        "pergunta": "Um app simples (lanterna, editor de fotos, \"limpador\") baixado da loja oficial pede permissão de Acessibilidade. O que você faz?",
        "opcoes": [
            ("Aceito: se está na loja oficial, já foi verificado.", 0),
            ("Aceito se o app tiver muitas avaliações boas.", 0.25),
            ("Nego e desinstalo: esse app não precisa disso.", 1),
        ],
        "armadilha": "Lojas oficiais filtram muito, mas não tudo: vários trojans bancários chegaram pela Play Store. A permissão de Acessibilidade deixa o app ler sua tela e tocar por você, inclusive dentro do app do banco.",
        "dica": "Acessibilidade é só para apps que realmente precisam (como leitores de tela). Revise em Configurações > Acessibilidade e mantenha o celular sempre atualizado.",
        "cartilhas": ["malware", "celulares"],
    },
    # ---------- Bloco 5: Dados e privacidade (140) ----------
    {
        "tema": "dados reais em IA gratuita",
        "bloco": "Dados e privacidade",
        "peso": 50,
        "pergunta": "Você precisa resumir um contrato, um exame ou uma planilha com dados de pessoas. Como usa uma IA gratuita (ChatGPT, Gemini…)?",
        "opcoes": [
            ("Colo o documento inteiro, porque é mais rápido.", 0),
            ("Colo, mas antes apago os nomes.", 0.25),
            ("Troco os dados reais por fictícios antes de colar.", 1),
        ],
        "armadilha": "Apagar nomes não basta: CPF, valores, endereços e o contexto ainda identificam pessoas e empresas. Em versões gratuitas, o que você cola pode ser guardado e usado para treinar o modelo, o que pode violar a LGPD.",
        "dica": "Use dados fictícios, desative nas configurações o uso das conversas para treinamento e, no trabalho, use só ferramentas aprovadas pela empresa.",
        "cartilhas": ["ia", "protecao_dados"],
    },
    {
        "tema": "posts em tempo real nas redes sociais",
        "bloco": "Dados e privacidade",
        "peso": 50,
        "pergunta": "Quando você posta stories de uma viagem ou de um passeio, costuma…",
        "opcoes": [
            ("Postar na hora, marcando o lugar.", 0),
            ("Postar na hora, mas sem marcar o lugar.", 0.25),
            ("Postar só depois que já saí do lugar.", 1),
        ],
        "armadilha": "Tirar a marcação não basta: a própria foto mostra onde você está e que sua casa está vazia. E saber que você está viajando é exatamente o que golpistas precisam para aplicar o golpe do falso parente na sua família.",
        "dica": "Poste depois, deixe o perfil fechado para desconhecidos e nunca mostre crachás, cartões de embarque ou documentos. Fuja das \"caixinhas\" do tipo nome do primeiro pet: são perguntas de segurança de bancos.",
        "cartilhas": ["redes_sociais", "privacidade"],
    },
    {
        "tema": "cópia de segurança de fotos e documentos",
        "bloco": "Dados e privacidade",
        "peso": 40,
        "pergunta": "Se você perdesse hoje o acesso ao celular e à sua conta Google ou iCloud, o que aconteceria com suas fotos e documentos?",
        "opcoes": [
            ("Perderia tudo, ficam só no celular.", 0),
            ("Não sei dizer.", 0),
            ("Estão na nuvem, só nessa mesma conta.", 0.5),
            ("Na nuvem e em outra cópia (HD ou pendrive).", 1),
        ],
        "armadilha": "\"Está tudo no Google\" é a falsa segurança: se a conta for invadida, bloqueada ou você perder o acesso, perde tudo de uma vez. Uma única cópia não é backup.",
        "dica": "Mantenha a nuvem ativada e faça, de tempos em tempos, uma segunda cópia num HD externo ou pendrive. Confira também se o e-mail e o telefone de recuperação da conta estão atualizados.",
        "cartilhas": ["backup"],
    },
]


PONTUACAO_MAXIMA = sum(p["peso"] for p in PERGUNTAS)
BLOCOS = list(dict.fromkeys(p["bloco"] for p in PERGUNTAS))


# ============================================================
# CARTILHAS OFICIAIS E PROTOCOLOS DE RESPOSTA A INCIDENTES
# ============================================================

_CERT = "https://cartilha.cert.br/fasciculos/{0}/fasciculo-{0}.pdf"

# chave: (título, fonte, url)
CARTILHAS = {
    "autenticacao": ("Autenticação", "CERT.br", _CERT.format("autenticacao")),
    "backup": ("Backup", "CERT.br", _CERT.format("backup")),
    "banco": ("Banco via Internet", "CERT.br", _CERT.format("banco-via-internet")),
    "celulares": ("Celulares e Tablets", "CERT.br", _CERT.format("celulares-e-tablets")),
    "malware": ("Códigos Maliciosos", "CERT.br", _CERT.format("codigos-maliciosos")),
    "comercio": ("Comércio via Internet", "CERT.br", _CERT.format("comercio-via-internet")),
    "furto": ("Furto de Celular", "CERT.br", _CERT.format("furto-de-celular")),
    "golpes": ("Golpes: Não se Deixe Enganar", "CERT.br", _CERT.format("golpes")),
    "fraudes": ("Golpes: Evite Fraudes", "CERT.br", _CERT.format("golpes-evite-fraudes")),
    "caiu": ("Golpes: Caiu? Veja o que Fazer", "CERT.br", _CERT.format("golpes-o-que-fazer")),
    "ia": ("Inteligência Artificial", "CERT.br", _CERT.format("ia")),
    "privacidade": ("Privacidade", "CERT.br", _CERT.format("privacidade")),
    "protecao_dados": ("Proteção de Dados", "CERT.br", _CERT.format("protecao-de-dados")),
    "redes_sociais": ("Redes Sociais", "CERT.br", _CERT.format("redes-sociais")),
    "vazamento": ("Vazamento de Dados", "CERT.br", _CERT.format("vazamento-de-dados")),
    "celular_seguro": ("Celular Seguro: bloqueio de aparelho roubado", "Governo Federal", "https://celularseguro.mj.gov.br"),
    "febraban": ("Portal Antifraudes", "Febraban", "https://antifraudes.febraban.org.br"),
    "hibp": ("Have I Been Pwned: seu e-mail vazou?", "Ferramenta gratuita", "https://haveibeenpwned.com"),
}

# Framework de resposta: cada incidente tem passos em ordem de urgência
INCIDENTES = [
    {
        "titulo": "Fiz um Pix ou pagamento para golpista",
        "palavras": ["pix", "transferi", "paguei", "boleto", "depositei", "golpe", "dinheiro"],
        "passos": [
            ("Ligue para o seu banco agora", "Use o número do verso do cartão ou o app. Peça a abertura do MED (Mecanismo Especial de Devolução do Pix): quanto antes, maior a chance de recuperar o valor."),
            ("Guarde as provas", "Tire prints da conversa, do comprovante e do perfil do golpista antes que sejam apagados."),
            ("Registre um boletim de ocorrência", "Pode ser na delegacia online do seu estado. O banco pode pedir o número do B.O."),
            ("Avise quem pode ser o próximo alvo", "Se o golpista usou o nome de alguém, avise essa pessoa e os contatos em comum."),
        ],
        "cartilhas": ["caiu", "banco", "febraban"],
    },
    {
        "titulo": "Minha conta foi invadida",
        "palavras": ["invadi", "hack", "clonaram", "whatsapp", "instagram", "facebook", "conta", "senha não"],
        "passos": [
            ("Avise seus contatos por outro canal", "O invasor costuma pedir dinheiro aos seus amigos usando sua conta. Avise por outra rede, SMS ou ligação."),
            ("Recupere pelo caminho oficial", "Use o \"Esqueci a senha\" e o suporte da própria plataforma. Nunca pague ninguém para recuperar a conta."),
            ("Troque a senha do e-mail primeiro", "É por ele que se recuperam as outras contas. Depois troque as senhas repetidas."),
            ("Ative a verificação em duas etapas", "Assim, mesmo com a senha, o invasor não consegue entrar de novo."),
        ],
        "cartilhas": ["caiu", "autenticacao", "redes_sociais"],
    },
    {
        "titulo": "Cliquei num link ou app suspeito",
        "palavras": ["link", "cliquei", "baixei", "instalei", "apk", "vírus", "virus", "propaganda", "tela", "apitando", "estranho"],
        "passos": [
            ("Desconecte o aparelho", "Ative o modo avião ou desligue o Wi-Fi para cortar a comunicação de um possível programa malicioso."),
            ("Não digite senhas nesse aparelho", "Até resolver, use outro aparelho para acessar banco e e-mail."),
            ("Remova o que foi instalado", "Desinstale apps recentes e veja em Configurações > Acessibilidade se algum app desconhecido tem permissão."),
            ("Se digitou dados bancários, ligue para o banco", "Peça o bloqueio do cartão ou da conta. Em último caso, restaure o aparelho para as configurações de fábrica."),
        ],
        "cartilhas": ["malware", "golpes", "celulares"],
    },
    {
        "titulo": "Meu celular foi roubado ou perdido",
        "palavras": ["roubado", "roubaram", "furtado", "perdi", "assalto", "celular sumiu"],
        "passos": [
            ("Bloqueie pelo Celular Seguro", "No programa do Governo Federal, um único alerta bloqueia o aparelho, a linha e os apps de bancos parceiros."),
            ("Ligue para a operadora e para os bancos", "Peça o bloqueio do chip e das contas que estavam no celular."),
            ("Bloqueie ou apague o aparelho à distância", "Use \"Encontre meu dispositivo\" (Android) ou \"Buscar\" (iPhone) a partir de outro aparelho."),
            ("Troque a senha do e-mail e registre B.O.", "O B.O. ajuda a bloquear o IMEI e é exigido por bancos e seguradoras."),
        ],
        "cartilhas": ["furto", "celular_seguro", "celulares"],
    },
    {
        "titulo": "Meus dados vazaram",
        "palavras": ["vazou", "vazamento", "vazaram", "dados", "cpf", "exposto"],
        "passos": [
            ("Descubra o que vazou", "Consulte seu e-mail no Have I Been Pwned e leia o comunicado da empresa, se houver."),
            ("Troque as senhas afetadas e as repetidas", "Se a senha vazada era usada em outros sites, troque em todos."),
            ("Ative a verificação em duas etapas", "Comece por e-mail, banco e redes sociais."),
            ("Desconfie de contatos \"oficiais\"", "Golpistas usam dados vazados para parecer o banco ou a loja. Saber seus dados não prova nada."),
        ],
        "cartilhas": ["vazamento", "protecao_dados", "hibp"],
    },
    {
        "titulo": "Comprei numa loja falsa",
        "palavras": ["loja", "compra", "comprei", "site falso", "não chegou", "nao chegou", "pedido"],
        "passos": [
            ("Pagou com cartão? Conteste", "Ligue para o emissor e peça a contestação da compra. Cartão virtual facilita o cancelamento."),
            ("Pagou com Pix? Ligue para o banco", "Peça a abertura do MED o quanto antes."),
            ("Guarde as provas", "Prints do anúncio, do site, do pedido e das conversas."),
            ("Registre B.O. e reclame", "Delegacia online do seu estado e Procon. Denuncie o anúncio na rede social onde ele apareceu."),
        ],
        "cartilhas": ["comercio", "caiu", "febraban"],
    },
]


def incidentes_relacionados(relato):
    texto = relato.lower()
    return [inc for inc in INCIDENTES if any(p in texto for p in inc["palavras"])]


def exibir_cartilhas(chaves):
    cards = "".join(
        f'<a class="cartilha" href="{url}" target="_blank" rel="noopener noreferrer">'
        f'<span class="cartilha-titulo">{escape(titulo)}</span>'
        f'<span class="cartilha-fonte">{escape(fonte)} <span aria-hidden="true">↗</span></span>'
        f'<span class="sr-only"> (abre em nova aba)</span></a>'
        for titulo, fonte, url in (CARTILHAS[c] for c in dict.fromkeys(chaves))
    )
    st.markdown(f'<div class="cartilhas">{cards}</div>', unsafe_allow_html=True)


VALORES_INICIAIS = {
    "perfil_concluido": False, "setor_usuario": "", "area_usuario": "",
    "etapa_diagnostico": 0, "diagnostico_finalizado": False,
    "respostas_diagnostico": [], "ordem_opcoes": [], "resultado_salvo": False,
    "analise_ia_realizada": False, "dicas_diagnostico_ia": "",
    "guardar_historico": False, "codigo_recem_criado": False,
}

# Valem para a visita inteira: não são zerados ao fazer uma nova auditoria
VALORES_DA_VISITA = {
    "codigo_usuario": None,  # código de acesso ao histórico (fica só na memória desta aba)
    "tentativas_codigo": 0, "aviso_cookies_ok": False, "admin_nonce": 0,
}
MAX_TENTATIVAS_CODIGO = 5


def reiniciar_sessao(apenas_faltantes=False):
    for chave, valor in VALORES_INICIAIS.items():
        if apenas_faltantes and chave in st.session_state:
            continue
        st.session_state[chave] = list(valor) if isinstance(valor, list) else valor  # cópia, não a mesma lista


reiniciar_sessao(apenas_faltantes=True)
for chave, valor in VALORES_DA_VISITA.items():
    st.session_state.setdefault(chave, valor)


def sortear_ordem_opcoes():
    """Embaralha as alternativas uma vez por auditoria, para a 'certa' não ficar sempre na mesma letra."""
    return [random.sample(range(len(p["opcoes"])), len(p["opcoes"])) for p in PERGUNTAS]


def calcular_score(respostas):
    return round(sum(r["pontos"] for r in respostas) / PONTUACAO_MAXIMA * 1000)


def score_por_bloco(respostas):
    obtido = {b: 0 for b in BLOCOS}
    for r in respostas:
        obtido[PERGUNTAS[r["indice_pergunta"]]["bloco"]] += r["pontos"]
    maximo = {b: sum(p["peso"] for p in PERGUNTAS if p["bloco"] == b) for b in BLOCOS}
    return {b: obtido[b] / maximo[b] for b in BLOCOS}




# ============================================================
# ARQUITETURA FAILSAFE E LÓGICA DE SCORE (CORES SEMÂNTICAS)
# ============================================================


def classificar_score_semantico(score):
    if score >= 700:
        return ("Postura Segura", "Indica conformidade e alta resiliência cibernética.", "#10B981") # Emerald Green
    if score >= 400:
        return ("Alerta/Atenção", "Indica higiene cibernética parcial.", "#F59E0B") # Amber
    return ("Risco Crítico", "Indica vulnerabilidade severa que exige correção imediata.", "#EF4444") # Red




@st.cache_resource
def _criar_cliente(chave):
    return Groq(api_key=chave)


def obter_cliente_ia():
    # A chave entra no cache como argumento: trocar a chave cria um cliente novo, sem reiniciar o app
    return _criar_cliente(GROQ_API_KEY) if GROQ_API_KEY else None


def perguntar_ia(prompt):
    """Devolve o texto da IA, ou None se ela não estiver configurada ou falhar (o app funciona sem ela)."""
    cliente = obter_cliente_ia()
    if cliente is None:
        return None
    for modelo in MODELOS_IA:
        try:
            resposta = cliente.chat.completions.create(
                messages=[{"role": "user", "content": prompt}], model=modelo, temperature=0.4,
            )
            return resposta.choices[0].message.content
        except Exception as erro:
            print(f"[IA] falha na Groq com {modelo}: {erro}")
    return None


def gerar_dicas_diagnostico(score_final, temas_vulneraveis):
    lista_de_erros = "; ".join(temas_vulneraveis) if temas_vulneraveis else "nenhum ponto fraco"
    prompt = (
        "Você orienta pessoas comuns (sem conhecimento técnico) sobre segurança digital no Brasil. "
        f"A pessoa tirou {score_final} de 1000 num teste. Pontos fracos, do mais grave ao menos grave: {lista_de_erros}. "
        "Escreva um plano de 3 passos para fazer ainda esta semana, começando pelo mais grave. "
        "Português do Brasil, linguagem simples, tom encorajador, sem jargão técnico, no máximo 2 frases por passo."
    )
    return perguntar_ia(prompt)


def respostas_com_falha():
    """Respostas que não tiraram nota máxima, das que mais custaram pontos para as que menos custaram."""
    falhas = [r for r in st.session_state.respostas_diagnostico if r["fator"] < 1]
    return sorted(falhas, key=lambda r: PERGUNTAS[r["indice_pergunta"]]["peso"] - r["pontos"], reverse=True)


def exibir_analise_ia_do_diagnostico(score):
    if not st.session_state.analise_ia_realizada:
        st.session_state.analise_ia_realizada = True
        temas = [PERGUNTAS[r["indice_pergunta"]]["tema"] for r in respostas_com_falha()]
        if temas and obter_cliente_ia():
            with st.spinner("Montando seu plano de ação..."):
                st.session_state.dicas_diagnostico_ia = gerar_dicas_diagnostico(score, temas)

    if st.session_state.dicas_diagnostico_ia:
        titulo_secao("Seu plano para esta semana (gerado por IA)")
        st.info(st.session_state.dicas_diagnostico_ia)


def painel_blocos(respostas):
    linhas = ""
    for bloco, proporcao in score_por_bloco(respostas).items():
        cor = classificar_score_semantico(proporcao * 1000)[2]
        linhas += (
            f'<div class="bloco-row"><div class="bloco-nome">{escape(bloco)}</div>'
            f'<div class="bloco-barra" aria-hidden="true"><div style="width:{proporcao * 100:.0f}%; background:{cor};"></div></div>'
            f'<div class="bloco-pct" style="color:{cor};">{proporcao * 100:.0f}%</div></div>'
        )
    st.markdown(f'<div class="bloco-card">{linhas}</div>', unsafe_allow_html=True)


def exibir_armadilhas():
    falhas = respostas_com_falha()
    if not falhas:
        st.success("Você não caiu em nenhuma das armadilhas. Mande o teste para alguém da família!")
        return
    for r in falhas:
        p = PERGUNTAS[r["indice_pergunta"]]
        perdidos = p["peso"] - r["pontos"]
        with st.expander(f"{p['tema'][0].upper()}{p['tema'][1:]}  ·  −{perdidos} pts"):
            st.markdown(f"**Você respondeu:** {p['opcoes'][r['opcao']][0]}")
            st.markdown(f"**Por que é arriscado:** {p['armadilha']}")
            st.markdown(f"**O que fazer:** {p['dica']}")
            st.markdown("**Para saber mais:**")
            exibir_cartilhas(p["cartilhas"])




def painel_score(score, classificacao, mensagem, cor):
    """Medidor circular do CyberScore (apenas apresentação)."""
    raio = 74
    circunferencia = 2 * 3.14159265 * raio
    preenchido = circunferencia * max(0, min(score, 1000)) / 1000
    tags = "".join(
        f'<span class="tag">{escape(t)}</span>' for t in (st.session_state.setor_usuario, st.session_state.area_usuario) if t
    )
    st.markdown(
        html(f"""
        <div class="score-card" style="--glow: {cor}; border-color: {cor}55;">
            <div class="score-gauge" role="img" aria-label="CyberScore: {score} de 1000 pontos">
                <svg width="168" height="168" viewBox="0 0 168 168" aria-hidden="true" focusable="false">
                    <circle cx="84" cy="84" r="{raio}" fill="none" stroke="#26262D" stroke-width="12"/>
                    <circle cx="84" cy="84" r="{raio}" fill="none" stroke="{cor}" stroke-width="12"
                            stroke-linecap="{'round' if score > 0 else 'butt'}" stroke-dasharray="{preenchido:.1f} {circunferencia:.1f}"
                            style="filter: drop-shadow(0 0 8px {cor}99);"/>
                </svg>
                <div class="center" aria-hidden="true">
                    <div class="score-num" style="color:{cor};">{score}</div>
                    <div class="score-den">/ 1000</div>
                </div>
            </div>
            <div class="score-info">
                <div class="score-kicker">CyberScore</div>
                <h2 class="score-class" style="color:{cor} !important;">{escape(classificacao)}</h2>
                <p class="score-msg">{escape(mensagem)}</p>
                <div class="score-meta">{tags}</div>
            </div>
        </div>
        """),
        unsafe_allow_html=True,
    )




# ============================================================
# PÁGINAS DA APLICAÇÃO
# ============================================================


def mascarar_codigo(codigo):
    return f"••••-••••-••••-{codigo[-4:]}"


def exibir_codigo_novo(codigo):
    st.markdown(
        html(f"""
        <div class="codigo-card" role="region" aria-label="Seu código de acesso">
            <div class="codigo-titulo">Seu código de acesso ao histórico</div>
            <p>Anote ou tire um print agora. <b>Nós não guardamos este código</b>: sem ele, não dá para
            ver nem apagar o seu histórico depois. Não compartilhe com ninguém.</p>
        </div>
        """),
        unsafe_allow_html=True,
    )
    st.code(codigo, language=None)


def pagina_diagnostico():
    if not st.session_state.perfil_concluido:
        cabecalho_pagina(
            "Antes de começar",
            f"São {len(PERGUNTAS)} situações do dia a dia, cerca de 4 minutos. "
            "Responda o que você realmente faz, não o que acha que é o certo.",
        )
        st.info("Você não precisa se identificar: não pedimos nome, e-mail, CPF nem telefone.", icon="🔒")

        st.markdown("**Perfil (opcional)**: ajuda a comparar resultados por grupo na pesquisa.")
        setor = st.selectbox("Setor de atuação (opcional)", options=SETORES, index=None, key="setor_box", placeholder="Prefiro não informar")
        area = st.selectbox("Área (opcional)", options=AREAS, index=None, key="area_box", placeholder="Prefiro não informar")

        codigo_atual = st.session_state.codigo_usuario
        opcao_historico = (
            f"Guardar no histórico do código {mascarar_codigo(codigo_atual)}" if codigo_atual
            else "Guardar no meu histórico, com um código de acesso anônimo"
        )
        guardar = st.radio(
            "O que fazer com o seu resultado?",
            ["Só ver o resultado agora, sem guardar", opcao_historico],
            index=1 if codigo_atual else 0,
        ) == opcao_historico
        st.caption(
            "📊 Todas as respostas são guardadas **de forma anônima** (sem nome, e-mail ou código) para estatísticas "
            "e para a pesquisa acadêmica do projeto. Só quem escolhe o histórico consegue rever os próprios resultados."
        )
        aceite = st.checkbox(
            "Li a Política de Privacidade e os Termos de Uso, estou ciente de que minhas respostas são guardadas "
            "de forma anônima e tenho 18 anos ou mais."
        )
        with st.expander("Ler o resumo da Política de Privacidade"):
            st.markdown(legal.RESUMO_PRIVACIDADE)
            st.caption("O texto completo está em **Privacidade e Termos**, no menu lateral.")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Iniciar Auditoria", disabled=not aceite, use_container_width=True):
            st.session_state.setor_usuario = setor or ""
            st.session_state.area_usuario = area or ""
            st.session_state.guardar_historico = guardar
            if guardar and not codigo_atual:
                st.session_state.codigo_usuario = gerar_codigo()
                st.session_state.codigo_recem_criado = True
            st.session_state.ordem_opcoes = sortear_ordem_opcoes()
            st.session_state.perfil_concluido = True
            st.rerun()
        return


    if st.session_state.diagnostico_finalizado:
        respostas = st.session_state.respostas_diagnostico
        score_1000 = calcular_score(respostas)
        codigo = st.session_state.codigo_usuario if st.session_state.guardar_historico else None

        if not st.session_state.resultado_salvo:
            try:
                repo.salvar(
                    codigo, st.session_state.setor_usuario or None,
                    st.session_state.area_usuario or None, score_1000, VERSAO_QUESTIONARIO, respostas,
                )
                st.session_state.resultado_salvo = True
            except Exception as erro:
                print(f"[banco] falha ao salvar: {erro}")
                st.warning("Não conseguimos salvar o resultado agora, mas você pode vê-lo abaixo.")


        # Recupera as informações com base nas cores semânticas recomendadas
        classificacao, mensagem, cor_hex = classificar_score_semantico(score_1000)


        cabecalho_pagina("Seu relatório de segurança")
        if codigo and st.session_state.codigo_recem_criado:
            exibir_codigo_novo(codigo)
        painel_score(score_1000, classificacao, mensagem, cor_hex)
        if st.session_state.resultado_salvo:
            st.caption(
                "Resultado guardado no seu histórico e, de forma anônima, nas estatísticas." if codigo
                else "Resultado guardado de forma anônima nas estatísticas. Ele não fica no seu histórico."
            )

        titulo_secao("Desempenho por área")
        painel_blocos(respostas)

        titulo_secao("Onde você está exposto")
        exibir_armadilhas()

        exibir_analise_ia_do_diagnostico(score_1000)


        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Executar Nova Auditoria", use_container_width=True):
            reiniciar_sessao()
            st.rerun()
        return


    etapa = st.session_state.etapa_diagnostico
    total_perguntas = len(PERGUNTAS)
    pergunta = PERGUNTAS[etapa]
    if not st.session_state.ordem_opcoes:  # sessão aberta antes de o código mudar
        st.session_state.ordem_opcoes = sortear_ordem_opcoes()


    # Progresso visual e contexto da pergunta
    progresso = (etapa) / total_perguntas
    st.markdown(
        f'<div class="step-row"><span>PERGUNTA <b>{etapa + 1:02d}</b> / {total_perguntas:02d}</span>'
        f'<span>{int(progresso * 100)}% concluído</span></div>',
        unsafe_allow_html=True,
    )
    st.progress(progresso)


    st.markdown(
        html(f"""
        <div class="q-card">
            <div class="q-chip">{escape(pergunta['bloco'])}</div>
            <h2 class="q-text">{escape(pergunta['pergunta'])}</h2>
        </div>
        """),
        unsafe_allow_html=True,
    )


    # Cartões de resposta na ordem sorteada para esta auditoria
    for letra, i in zip("ABCD", st.session_state.ordem_opcoes[etapa]):
        texto, fator = pergunta["opcoes"][i]
        if st.button(f"{letra}   ·   {texto}", use_container_width=True, key=f"btn_{etapa}_{i}"):
            st.session_state.respostas_diagnostico.append(
                {"indice_pergunta": etapa, "opcao": i, "fator": fator, "pontos": round(pergunta["peso"] * fator)}
            )

            if etapa == total_perguntas - 1:
                st.session_state.diagnostico_finalizado = True
            else:
                st.session_state.etapa_diagnostico += 1
            st.rerun()




# Barreira antes de enviar o relato à IA externa: bloqueia dados pessoais óbvios (LGPD: minimização)
PADROES_SENSIVEIS = {
    "um CPF": re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"),
    "um número de cartão": re.compile(r"\b(?:\d[ .-]?){13,19}\b"),
    "um e-mail": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b"),
    "um telefone": re.compile(r"\(?\b\d{2}\)?\s?9?\d{4}-?\d{4}\b"),
}


def dados_sensiveis_no_texto(texto):
    return [nome for nome, padrao in PADROES_SENSIVEIS.items() if padrao.search(texto)]


def exibir_protocolo(incidente):
    passos = "".join(
        f'<li><span class="passo-num">{n}</span><div><b>{escape(titulo)}</b><p>{escape(texto)}</p></div></li>'
        for n, (titulo, texto) in enumerate(incidente["passos"], start=1)
    )
    st.markdown(f'<ol class="protocolo" role="list">{passos}</ol>', unsafe_allow_html=True)
    titulo_secao("Cartilhas oficiais")
    exibir_cartilhas(incidente["cartilhas"])


def pagina_consultoria():
    cabecalho_pagina(
        "Resposta a Incidentes",
        "Escolha o que aconteceu e siga os passos na ordem. Se o seu caso não estiver na lista, descreva abaixo.",
    )

    # Framework visual: o usuário escolhe o incidente e recebe o protocolo, sem depender da IA
    escolhido = st.session_state.get("incidente_escolhido")
    colunas = st.columns(2)
    for i, incidente in enumerate(INCIDENTES):
        selecionado = escolhido == i
        if colunas[i % 2].button(
            ("✓ " if selecionado else "") + incidente["titulo"],  # indica a seleção sem depender só da cor
            key=f"inc_{i}", use_container_width=True,
            type="primary" if selecionado else "secondary",
        ):
            st.session_state.incidente_escolhido = None if selecionado else i
            st.rerun()

    if escolhido is not None:
        titulo_secao(INCIDENTES[escolhido]["titulo"])
        exibir_protocolo(INCIDENTES[escolhido])

    st.divider()
    titulo_secao("Não encontrou o seu caso?")
    relato = st.text_area("Conte com suas palavras o que aconteceu", height=150, placeholder="Ex.: Cliquei num link que chegou no WhatsApp e agora meu celular está abrindo propagandas sozinho…")
    st.warning(
        "Não escreva senhas, CPF, números de cartão, nomes ou dados de outras pessoas. Ao clicar em "
        "Analisar, o relato é enviado à Groq (serviço de IA nos EUA) e não é guardado pelo CyberScore.",
        icon="⚠️",
    )


    if st.button("Analisar Ameaça"):
        if not relato.strip():
            st.warning("Descreva o que aconteceu antes de enviar.")
            return
        encontrados = dados_sensiveis_no_texto(relato)
        if encontrados:
            st.error(
                f"Parece que o relato contém {', '.join(encontrados)}. Apague essa informação e envie de novo: "
                "ela não é necessária para a análise."
            )
            return


        prompt = (
            "Você ajuda pessoas comuns no Brasil, sem conhecimento técnico, que acabaram de sofrer um problema de segurança digital. "
            "Leia o relato abaixo, identifique o que provavelmente aconteceu (pode haver mais de um problema) e diga o que fazer AGORA, "
            "em no máximo 5 passos numerados, do mais urgente ao menos urgente. Linguagem simples, sem jargão, frases curtas. "
            "Se algo no relato for um mal-entendido (ex.: algo que a pessoa acha que aconteceu mas é improvável), explique em uma frase. "
            "Termine indicando onde buscar ajuda oficial quando fizer sentido (banco, delegacia online, suporte da plataforma). "
            "Não use tabelas. Não escreva links nem endereços de sites (cite só o nome do serviço, ex.: 'delegacia online do seu estado'), "
            "nem recomende marcas de produtos.\n\n"
            f"Relato: {relato.strip()}"
        )


        with st.spinner("Analisando o relato..."):
            resposta = perguntar_ia(prompt)
            if resposta:
                st.success(resposta)
            else:
                st.error(
                    "**Primeiros passos (modo offline):**\n\n"
                    "1. **Desconecte:** ative o modo avião ou desligue o Wi-Fi do aparelho afetado.\n"
                    "2. **Proteja o dinheiro:** se envolve banco ou Pix, ligue para o banco pelo número do verso do cartão e peça bloqueio.\n"
                    "3. **Troque senhas de outro aparelho:** comece pelo e-mail, depois banco e redes sociais, e ative a verificação em duas etapas.\n"
                    "4. **Avise seus contatos** por outro canal, se alguma conta sua foi invadida."
                )
                st.caption("IA indisponível no momento: exibindo os passos padrão.")

        relacionados = incidentes_relacionados(relato)
        titulo_secao("Cartilhas recomendadas")
        exibir_cartilhas([c for inc in relacionados for c in inc["cartilhas"]] or ["caiu", "golpes"])




def pagina_historico():
    cabecalho_pagina(
        "Meu Histórico",
        "Veja a evolução dos seus resultados. Só quem tem o código de acesso consegue ver ou apagar estes dados.",
    )
    codigo = st.session_state.codigo_usuario

    if not codigo:
        if st.session_state.tentativas_codigo >= MAX_TENTATIVAS_CODIGO:
            st.error("Muitas tentativas com código inválido. Feche esta aba e abra o site de novo para tentar outra vez.")
            return
        with st.form("entrar_codigo"):
            digitado = st.text_input("Código de acesso", placeholder="XXXX-XXXX-XXXX-XXXX", max_chars=24)
            entrar = st.form_submit_button("Ver meu histórico")
        if entrar:
            normalizado = normalizar_codigo(digitado)
            if normalizado and repo.codigo_tem_historico(normalizado):
                st.session_state.codigo_usuario = normalizado
                st.session_state.tentativas_codigo = 0
                st.rerun()
            st.session_state.tentativas_codigo += 1
            st.error("Código não encontrado. Confira se digitou certo (letras e números, sem 0, 1, I, L ou O).")
        st.caption(
            "Ainda não tem um código? Ele é criado quando você faz o Diagnóstico e escolhe "
            "**Guardar no meu histórico**."
        )
        return

    c1, c2 = st.columns([3, 1])
    c1.markdown(f"Conectado com o código **{mascarar_codigo(codigo)}**")
    if c2.button("Sair", use_container_width=True):
        st.session_state.codigo_usuario = None
        st.rerun()

    if st.session_state.pop("avaliacao_apagada", False):
        st.success("Avaliação apagada.")
    try:
        historico = repo.historico(codigo)
    except Exception as erro:
        print(f"[banco] falha no histórico: {erro}")
        st.error("Não foi possível carregar o histórico agora.")
        return
    if not historico:
        st.info("Nenhum resultado guardado com este código ainda. Faça o Diagnóstico e escolha guardar no histórico.")
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("Último resultado", historico[0]["score"])
    c2.metric("Melhor resultado", max(h["score"] for h in historico))
    c3.metric("Avaliações", len(historico))
    if len(historico) > 1:
        titulo_secao("Evolução")
        evolucao = pd.DataFrame({"Data": [h["criado_em"] for h in historico], "CyberScore": [h["score"] for h in historico]})
        st.line_chart(evolucao, x="Data", y="CyberScore", color=COR_CIANO)

    titulo_secao("Suas avaliações")
    for h in historico:
        classificacao = classificar_score_semantico(h["score"])[0]
        with st.expander(f"{h['criado_em']:%d/%m/%Y %H:%M}  ·  {h['score']} pontos  ·  {classificacao}"):
            detalhes = [d for d in (h["setor"], h["area"]) if d]
            if detalhes:
                st.caption("Perfil informado: " + " · ".join(detalhes))
            if h["versao"] == VERSAO_QUESTIONARIO:
                for bloco, proporcao in score_por_bloco(h["respostas"]).items():
                    st.markdown(f"- {bloco}: **{proporcao * 100:.0f}%**")
            else:
                st.caption("Feita com uma versão anterior do questionário: só o total está disponível.")
            if st.button("Apagar esta avaliação", key=f"apagar_{h['id']}"):
                repo.apagar_avaliacao(codigo, h["id"])
                st.session_state.avaliacao_apagada = True
                st.rerun()

    st.divider()
    with st.expander("Apagar todo o meu histórico"):
        st.warning("Apaga todas as suas avaliações, inclusive das estatísticas da pesquisa. Não dá para desfazer.")
        confirmado = st.checkbox("Entendo e quero apagar tudo", key="confirma_apagar_historico")
        if st.button("Apagar meu histórico", disabled=not confirmado):
            repo.apagar_historico(codigo)
            st.session_state.codigo_usuario = None
            st.rerun()


def pagina_legal():
    cabecalho_pagina("Privacidade e Termos", f"Última atualização: {legal.DATA_ATUALIZACAO}.")
    aba_privacidade, aba_termos, aba_cookies = st.tabs(["Política de Privacidade", "Termos de Uso", "Cookies"])
    with aba_privacidade:
        st.markdown(legal.POLITICA_PRIVACIDADE)
    with aba_termos:
        st.markdown(legal.TERMOS_USO)
    with aba_cookies:
        st.markdown(legal.POLITICA_COOKIES)


def grafico_medias(grupos, rotulo, cor):
    if not grupos:
        st.caption(f"Ainda não há {rotulo.lower()} com pelo menos {TAMANHO_MINIMO_GRUPO} participantes.")
        return
    tabela = pd.DataFrame(grupos).rename(columns={"grupo": rotulo, "pessoas": "Participantes", "media": "Média"})
    st.bar_chart(tabela, x=rotulo, y="Média", color=cor)
    with st.expander("Ver como tabela"):  # alternativa acessível ao gráfico
        st.dataframe(tabela.round({"Média": 0}), hide_index=True, use_container_width=True)


def pagina_dashboard():
    cabecalho_pagina(
        "Painel da Pesquisa",
        "Médias anônimas de todos os diagnósticos realizados. "
        f"Grupos com menos de {TAMANHO_MINIMO_GRUPO} pessoas ficam ocultos para ninguém ser identificado.",
    )
    try:
        estatisticas = repo.estatisticas_pesquisa(VERSAO_QUESTIONARIO)
        if estatisticas["total"] < TAMANHO_MINIMO_GRUPO:
            st.info(f"Aguardando coleta de dados: as médias aparecem a partir de {TAMANHO_MINIMO_GRUPO} participantes.")
        else:
            c1, c2 = st.columns(2)
            c1.metric("Média do CyberScore", f"{estatisticas['media']:.0f}")
            c2.metric("Participantes", estatisticas["total"])
            titulo_secao("Média por setor")
            grafico_medias(estatisticas["por_setor"], "Setor", COR_ROXO)
            titulo_secao("Média por área")
            grafico_medias(estatisticas["por_area"], "Área", COR_CIANO)
    except Exception as erro:
        print(f"[banco] falha no painel: {erro}")
        st.error("Não foi possível carregar o painel agora.")


    st.divider()
    if not SENHA_ADMIN:
        return  # sem SENHA_ADMIN configurada, a área administrativa fica desativada
    if st.session_state.pop("banco_limpo", False):
        st.success("Banco de dados apagado.")

    with st.expander("Área administrativa"):
        senha = st.text_input(
            "Senha de administrador", type="password", key=f"senha_{st.session_state.admin_nonce}",
            placeholder="Digite e pressione Enter",
        )
        if not senha:
            return
        if not hmac.compare_digest(senha.encode(), SENHA_ADMIN.encode()):
            st.error("Senha incorreta.")
            return

        st.warning("Isso apaga todos os resultados, inclusive os históricos de todos os usuários. Não dá para desfazer.")
        confirmado = st.checkbox("Entendo e quero apagar todos os dados", key=f"confirma_{st.session_state.admin_nonce}")
        if st.button("Purgar Banco de Dados", disabled=not confirmado):
            repo.apagar_tudo()
            st.session_state.admin_nonce += 1  # limpa os campos de senha e confirmação
            st.session_state.banco_limpo = True
            st.rerun()




# ============================================================
# NAVEGAÇÃO
# ============================================================
st.sidebar.markdown(
    html(f"""
    <div class="brand">
        {LOGO_SVG}
        <div>
            <div class="brand-name">Cyber<em>Score</em></div>
            <div class="brand-tag">Central de Segurança</div>
        </div>
    </div>
    <div class="side-label">Módulos</div>
    """),
    unsafe_allow_html=True,
)
PAGINAS = {
    "Diagnóstico de Risco": pagina_diagnostico,
    "Consultoria de Incidentes": pagina_consultoria,
    "Meu Histórico": pagina_historico,
    "Painel da Pesquisa": pagina_dashboard,
    "Privacidade e Termos": pagina_legal,
}
pagina = st.sidebar.radio("Módulos", list(PAGINAS), label_visibility="collapsed")
st.sidebar.caption(
    "🔒 Nunca digite senhas, CPF, dados de cartão ou informações de outras pessoas neste site. "
    "Projeto acadêmico, sem fins lucrativos."
)

# O Streamlit marca a página como inglês; leitores de tela precisam saber que é português
st.iframe("<script>window.parent.document.documentElement.lang = 'pt-BR';</script>", height=1)

if not st.session_state.aviso_cookies_ok:
    with st.container(border=True):
        st.markdown(legal.AVISO_COOKIES)
        if st.button("Entendi", key="ok_cookies"):
            st.session_state.aviso_cookies_ok = True
            st.rerun()

PAGINAS[pagina]()
