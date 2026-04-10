import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuração de Janela
st.set_page_config(page_title="MyFinance", layout="centered")

# --- CSS PREMIUM: NEUMORPHISM & DARK MODE ---
st.markdown("""
    <style>
    .stApp { background-color: #000; color: #fff; }
    
    /* Cartões e Botões Pílula */
    .pill-button {
        background: #111;
        border: 1px solid #333;
        border-radius: 50px;
        padding: 15px 25px;
        margin: 10px 0;
        text-align: center;
        transition: 0.3s;
        cursor: pointer;
    }
    .pill-button:hover { border-color: #007bff; background: #161616; }
    
    /* Menu Inferior Estilizado */
    .stTabs [data-baseweb="tab-list"] {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: #000;
        border-top: 1px solid #222;
        justify-content: space-around;
        z-index: 1000;
    }
    
    /* Dashboard Header */
    .balance-header {
        background: linear-gradient(180deg, #111 0%, #000 100%);
        padding: 40px 20px;
        border-radius: 0 0 30px 30px;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MEMÓRIA DA APP (Session State) ---
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'new_entry' not in st.session_state:
    st.session_state.new_entry = {}
if 'contas' not in st.session_state:
    st.session_state.contas = ["Moey", "Crédito Agrícola", "Trade Republic"]

DB_FILE = "myfinance_v3.csv"
def save_entry(data):
    df = pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame()
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

# --- NAVEGAÇÃO ---
tab_home, tab_add, tab_settings = st.tabs(["🏠 Home", "➕ Novo", "⚙️ Ajustes"])

# --- ABA 1: DASHBOARD ---
with tab_home:
    st.markdown("<div class='balance-header'>", unsafe_allow_html=True)
    df = pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame(columns=['Type', 'Amount', 'Account'])
    
    total = 0
    if not df.empty:
        inc = df[df['Type'] == 'Receita']['Amount'].sum()
        exp = df[df['Type'] == 'Despesa']['Amount'].sum()
        total = inc - exp
    
    st.markdown(f"<p style='color:#888;'>Saldo Disponível</p><h1 style='font-size:40px;'>{total:,.2f} €</h1>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Lista de Bancos
    for conta in st.session
