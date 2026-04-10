import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuração Base
st.set_page_config(page_title="MyFinance", layout="centered")

# --- CSS LIGHT MODE PREMIUM ---
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; color: #1E293B; }
    
    /* Cartão de Saldo */
    .balance-header {
        background: white;
        padding: 40px 20px;
        border-radius: 24px;
        text-align: center;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05);
        margin-bottom: 25px;
        border: 1px solid #E2E8F0;
    }

    /* Botões de Pílula */
    .stButton > button {
        background-color: white;
        color: #1E293B;
        border: 1px solid #E2E8F0;
        border-radius: 50px;
        padding: 12px 24px;
        width: 100%;
        font-weight: 500;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        border-color: #3B82F6;
        color: #3B82F6;
        background-color: #EFF6FF;
    }

    /* Histórico de Transações */
    .trans-card {
        background: white;
        padding: 16px;
        border-radius: 16px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #F1F5F9;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MEMÓRIA ---
if 'step' not in st.session_state: st.session_state.step = 0
if 'new_entry' not in st.session_state: st.session_state.new_entry = {}
if 'contas' not in st.session_state: st.session_state.contas = ["Moey", "Crédito Agrícola", "Trade Republic"]

DB_FILE = "myfinance_v5.csv"
CATEGORIAS = ["Tabaco", "Alimentação", "Casa", "Transportes", "Lazer", "Salário", "Investimentos", "Outros"]

def save_entry(data):
    df = pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame()
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

# --- LÓGICA DE INTERFACE ---

# 1. DASHBOARD (HOME)
if st.session_state.step == 0:
    st.markdown("<h2 style='text-align:center;'>MyFinance</h2>", unsafe_allow_html=True)
    
    df = pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame(columns=['Date', 'Type', 'Amount', 'Account', 'Category'])
    
    # Saldo Total
    inc = df[df['Type'] == 'Receita']['Amount'].sum()
    exp = df[df['Type'] == 'Despesa']['Amount'].sum()
    st.markdown(f"""
        <div class='balance-header'>
            <small style='color:#64748B; text-transform:uppercase; letter-spacing:1px;'>Património Total</small>
            <h1 style='margin:10px 0 0 0; font-size:42px;'>{inc - exp:,.2f} €</h1>
        </div>
    """, unsafe_allow_html=True)

    # Lista de Movimentos
    st.write("### Atividade Recente")
    if not df.empty:
        for _, row in df.tail(6)[::-1].iterrows():
            simbolo = "+" if row['Type'] == 'Receita' else "-"
            cor_valor = "#10B981" if row['Type'] == 'Receita' else "#EF4444"
            st.markdown(f"""
                <div class='trans-card'>
                    <div>
                        <div style='font-weight:bold; font-size:16px;'>{row['Category']}</div>
                        <div style='color:#94A3B8; font-size:12px;'>{row['Account']}</div>
                    </div>
                    <div style='color:{cor_valor}; font-weight:bold; font-size:18px;'>
                        {simbolo}{row['Amount']:.2f} €
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Ainda não registaste nenhum movimento.")

    # Botão Flutuante (FAB)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➕ ADICIONAR NOVO", use_container_width=True):
        st.session_state.step = 1
        st.rerun()

# 2. FLUXO DE INSERÇÃO
else:
    st.markdown(f"<p style='text-align:center; color:#94A3B8;'>Pergunta {st.session_state.step} de 5</p>", unsafe_allow_html=True)
    
    if st.session_state.step == 1:
        st.header("O que queres registar?")
        if st.button("🔴 Despesa"):
            st.session_state.new_entry['Type'] = 'Despesa'
            st.session_state.step = 2
            st.rerun()
        if st.button("🟢 Receita"):
            st.session_state.new_entry['Type'] = 'Receita'
            st.session_state.step = 2
            st.rerun()
        if st.button("Cancelar"): st.session_state.step = 0; st.rerun()

    elif st.session_state.step == 2:
        st.header("Qual o valor?")
        val = st.number_input("Introduz o valor", min_value=0.0, format="%.2f", label_visibility="collapsed")
        if st.button("Próximo →"):
            st.session_state.new_entry['Amount'] = val
            st.session_state.step = 3
            st.rerun()

    elif st.session_state.step == 3:
        st.header("De que conta?")
        for acc in st.session_state.contas:
            if st.button(acc):
                st.session_state.new_entry['Account'] = acc
                st.session_state.step = 4
                st.rerun()

    elif st.session_state.step == 4:
        st.header("Qual a categoria?")
        for cat in CATEGORIAS:
            if st.button(cat):
                st.session_state.new_entry['Category'] = cat
                st.session_state.step = 5
                st.rerun()

    elif st.session_state.step == 5:
        st.header("Confirmar dados?")
        res = st.session_state.new_entry
        st.markdown(f"""
            <div style='background:#F1F5F9; padding:20px; border-radius:15px; text-align:center;'>
                <p style='margin:0;'>{res['Type']} em <b>{res['Account']}</b></p>
                <h2 style='margin:5px 0;'>{res['Amount']:.2f} €</h2>
                <p style='color:#3B82F6;'>Categoria: {res['Category']}</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("✅ GUARDAR"):
            res['Date'] = datetime.now().strftime("%Y-%m-%d")
            save_entry(res)
            st.session_state.step = 0
            st.rerun()
        if st.button("❌ Recomeçar"): st.session_state.step = 1; st.rerun()
