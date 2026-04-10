import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuração Base
st.set_page_config(page_title="MyFinance", layout="centered", initial_sidebar_state="collapsed")

# --- CSS ULTRA CUSTOMIZADO (LIGHT MODE & FLOATING BUTTON) ---
st.markdown("""
    <style>
    /* 1. FUNDO LIGHT E FONTES */
    .stApp { background-color: #F9FAFB; color: #1F2937; font-family: 'Inter', sans-serif; }
    h1, h2, h3 { color: #111827; }

    /* 2. HEADER DE SALDO (SOFT GRADIENT) */
    .balance-header {
        background: linear-gradient(135deg, #FFFFFF 0%, #EFF6FF 100%);
        padding: 40px 20px;
        border-radius: 0 0 30px 30px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid #E5E7EB;
    }

    /* 3. CARTÕES DE BANCO (SOFT NEUMORPHISM) */
    .bank-card {
        background: #FFFFFF;
        padding: 15px;
        border-radius: 16px;
        border: 1px solid #E5E7EB;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.03);
    }

    /* 4. BOTÕES "PÍLULA" (PERGUNTA A PERGUNTA) */
    .stButton>button {
        background-color: #FFFFFF;
        color: #1F2937;
        border: 1px solid #D1D5DB;
        border-radius: 50px;
        padding: 12px 24px;
        font-weight: 500;
        width: 100%;
        transition: 0.2s;
    }
    .stButton>button:hover {
        border-color: #3B82F6;
        background-color: #EFF6FF;
        color: #1D4ED8;
    }

    /* 5. BOTÃO FLUTUANTE (FLOATING ACTION BUTTON - FAB) */
    /* O Streamlit não suporta FAB nativo fixo, por isso simulamos 
       no topo da área de inserção para UX mobile */
    .fab-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
    }
    .fab-button {
        background: linear-gradient(90deg, #3B82F6, #2563EB);
        color: white;
        border: none;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        font-size: 30px;
        box-shadow: 0px 4px 10px rgba(37, 99, 235, 0.5);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Ocultar Tabs Padrão para UX Limpa */
    .stTabs [data-baseweb="tab-list"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

# --- MEMÓRIA DA APP (Session State) ---
if 'step' not in st.session_state: st.session_state.step = 0 # 0 = Dashboard, 1+ = Inserção
if 'new_entry' not in st.session_state: st.session_state.new_entry = {}
if 'contas' not in st.session_state: st.session_state.contas = ["Moey", "Crédito Agrícola", "Trade Republic"]

DB_FILE = "myfinance_v3.csv"
def save_entry(data):
    df = pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame()
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

# --- FUNÇÃO PARA RESETAR INSERÇÃO ---
def reset_insertion():
    st.session_state.step = 0
    st.session_state.new_entry = {}
    st.rerun()

# --- HEADER (MyFinance Logo & Nome) ---
st.markdown("<h2 style='text-align: center; color: #111827;'>MyFinance</h2>", unsafe_allow_html=True)

# --- FLUXO DE TELAS ---

# ECRÃ 0: DASHBOARD (HOME)
if st.session_state.step == 0:
    # Cabeçalho de Saldo
    st.markdown("<div class='balance-header'>", unsafe_allow_html=True)
    df = pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame(columns=['Type', 'Amount', 'Account'])
    
    total = 0
    if not df.empty:
        inc = df[df['Type'] == 'Receita']['Amount'].sum()
        exp = df[df['Type'] == 'Despesa']['Amount'].sum()
        total = inc - exp
    
    st.markdown(f"<p style='color:#6B7280; margin:0;'>Saldo Total</p><h1 style='font-size:48px; margin:0; color:#111827;'>{total:,.2f} €</h1>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Lista de Bancos
    st.write("### Minhas Contas")
    for conta in st.session_state.contas:
        c_val = 0
        if not df.empty:
            c_inc = df[(df['Account'] == conta) & (df['Type'] == 'Receita')]['Amount'].sum()
            c_exp = df[(df['Account'] == conta) & (df['Type'] == 'Despesa')]['Amount'].sum()
            c_val = c_inc - c_exp
        st.markdown(f"""
            <div class='bank-card'>
                <span style='color:#374151; font-weight:500;'>{conta}</span>
                <span style='font-weight:bold; color:#111827;'>{c_val:,.2f} €</span>
            </div>
        """, unsafe_allow_html=True)

    st.write("---")
    # Botão para gerir contas (Ajustes simplificados)
    with st.expander("⚙️ Gerir Bancos"):
        novo_b = st.text_input("Nome do novo ativo")
        if st.button("Adicionar"):
            if novo_b and novo_b not in st.session_state.contas:
                st.session_state.contas.append(novo_b)
                st.success(f"{novo_b} adicionado!")
                st.rerun()

    # --- SIMULAÇÃO DO BOTÃO FLUTUANTE (FAB) ---
    # Como o Streamlit bloqueia CSS fixo externo, usamos um botão padrão 
    # estilizado no fundo da página para simular a UX do FAB
    st.markdown("<br><br><br>", unsafe_allow_html=True) # Espaço para o botão
    if st.button("➕", key="fab_sim", use_container_width=False):
        st.session_state.step = 1
        st.rerun()
    st.markdown("<p style='text-align:center; color:#6B7280; font-size:12px;'>Adicionar Novo</p>", unsafe_allow_html=True)

# ECRÃS DE INSERÇÃO (PERGUNTA A PERGUNTA)
else:
    st.markdown(f"<p style='text-align:center; color:#6B7280;'>Passo {st.session_state.step} de 4</p>", unsafe_allow_html=True)
    
    # Passo 1: Tipo
    if st.session_state.step == 1:
        st.markdown("<h2 style='text-align:center;'>O que deseja registar?</h2>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        if col1.button("🔴 Despesa", key="btn_desp"):
            st.session_state.new_entry['Type'] = 'Despesa'
            st.session_state.step = 2
            st.rerun()
        if col2.button("🟢 Receita", key="btn_rece"):
            st.session_state.new_entry['Type'] = 'Receita'
            st.session_state.step = 2
            st.rerun()
        if st.button("Cancel", key="canc_1"): reset_insertion()

    # Passo 2: Valor
    elif st.session_state.step == 2:
        st.markdown("<h2 style='text-align:center;'>Qual o valor?</h2>", unsafe_allow_html=True)
        # Campo numérico limpo
        valor = st.number_input("Introduza o valor (€)", min_value=0.0, format="%.2f", key="val_input", label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Próximo →", key="btn_next_2"):
            if valor > 0:
                st.session_state.new_entry['Amount'] = valor
                st.session_state.step = 3
                st.rerun()
            else: st.warning("Introduza um valor válido.")
        if st.button("Voltar", key="back_2"): 
            st.session_state.step = 1
            st.rerun()

    # Passo 3: Conta
    elif st.session_state.step == 3:
        st.markdown("<h2 style='text-align:center;'>Qual a conta?</h2>", unsafe_allow_html=True)
        # Botões pílula para as contas
        for c in st.session_state.contas:
            if st.button(c, key=f"btn_acc_{c}"):
                st.session_state.new_entry['Account'] = c
                st.session_state.step = 4
                st.rerun()
        if st.button("Voltar", key="back_3"): 
            st.session_state.step = 2
            st.rerun()

    # Passo 4: Confirmar
    elif st.session_state.step == 4:
        st.markdown("<h2 style='text-align:center;'>Confirmar Registo?</h2>", unsafe_allow_html=True)
        
        # Resumo Visual
        entry = st.session_state.new_entry
        st.markdown(f"""
            <div style='background:#EFF6FF; padding:20px; border-radius:16px; text-align:center; border:1px solid #DBEAFE;'>
                <p style='color:#1D4ED8; font-size:18px; font-weight:bold; margin:0;'>{entry['Type']}</p>
                <h1 style='color:#111827; font-size:40px; margin:10px 0;'>{entry['Amount']:.2f} €</h1>
                <p style='color:#6B7280; margin:0;'>na conta {entry['Account']}</p>
            </div>
            <br>
        """, unsafe_allow_html=True)
        
        if st.button("✅ FINALIZAR", key="btn_fin"):
            save_entry(st.session_state.new_entry)
            st.success("Movimento guardado com sucesso!")
            # Pequeno delay para mostrar o sucesso antes de resetar
            import time
            time.sleep(1)
            reset_insertion()
            
        if st.button("❌ Cancelar", key="btn_canc_fin"): reset_insertion()
