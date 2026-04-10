import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuração de App Premium
st.set_page_config(page_title="Diogo Bank", layout="centered")

# --- DESIGN REVOLUT (CSS) ---
st.markdown("""
    <style>
    .stMetric { background-color: #111; border-radius: 15px; padding: 20px; border: 1px solid #222; }
    div[data-testid="stForm"] { background-color: #0e1117; border: 2px solid #007bff; border-radius: 20px; padding: 20px; }
    .stButton>button { background-color: #007bff; color: white; border-radius: 10px; width: 100%; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- FICHEIROS DE DADOS ---
DB_FILE = "financas_v2.csv"
CONFIG_FILE = "config_contas.csv"

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    return pd.DataFrame(columns=['Date', 'Type', 'Account', 'Category', 'Amount', 'Description'])

def load_accounts():
    if os.path.exists(CONFIG_FILE):
        return pd.read_csv(CONFIG_FILE)['Account'].tolist()
    return ["Moey", "Crédito Agrícola", "Trade Republic", "Cash", "PPR"] # Valores padrão

# --- INICIALIZAÇÃO ---
df = load_data()
contas_ativas = load_accounts()

st.title("🏦 Diogo Bank")

# --- BARRA LATERAL: GESTÃO DE CONTAS ---
with st.sidebar:
    st.header("⚙️ Configurações")
    nova_conta = st.text_input("Adicionar Novo Banco/Ativo:")
    if st.button("Adicionar"):
        if nova_conta and nova_conta not in contas_ativas:
            contas_ativas.append(nova_conta)
            pd.DataFrame({'Account': contas_ativas}).to_csv(CONFIG_FILE, index=False)
            st.success(f"{nova_conta} adicionado!")
            st.rerun()
    
    conta_remover = st.selectbox("Remover Banco:", [""] + contas_ativas)
    if st.button("Remover"):
        if conta_remover in contas_ativas:
            contas_ativas.remove(conta_remover)
            pd.DataFrame({'Account': contas_ativas}).to_csv(CONFIG_FILE, index=False)
            st.warning(f"{conta_remover} removido!")
            st.rerun()

# --- 1. DASHBOARD DE SALDOS DINÂMICO ---
st.subheader("Meus Saldos")
total_balance = 0
cols = st.columns(3)

for idx, acc in enumerate(contas_ativas):
    # Cálculo de saldo por conta específica
    acc_income = df[(df['Account'] == acc) & (df['Type'] == 'Receita')]['Amount'].sum()
    acc_expense = df[(df['Account'] == acc) & (df['Type'] == 'Despesa')]['Amount'].sum()
    acc_balance = acc_income - acc_expense
    total_balance += acc_balance
    
    # Distribui pelos cartões (3 por linha)
    with cols[idx % 3]:
        st.metric(acc, f"{acc_balance:,.2f} €")

st.metric("SALDO TOTAL", f"{total_balance:,.2f} €")
st.divider()

# --- 2. INSERÇÃO MANUAL (CONTAS ATUALIZADAS) ---
with st.expander("➕ NOVO MOVIMENTO", expanded=True):
    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        t_tipo = c1.selectbox("Tipo", ["Despesa", "Receita"])
        t_valor = c2.number_input("Valor (€)", min_value=0.0, step=0.01, format="%.2f")
        
        # Aqui aparecem automaticamente as contas que configuraste
        t_conta = st.selectbox("Conta / Ativo", contas_ativas)
        t_cat = st.selectbox("Categoria", ["Alimentação", "Tabaco", "Casa", "Lazer", "Saúde", "Trabalho", "PPR/Investimento", "Outros"])
        t_desc = st.text_input("Descrição (Ex: Jantar, Salário)")
        t_data = st.date_input("Data", datetime.now())
        
        if st.form_submit_button("CONFIRMAR TRANSACÇÃO"):
            new_row = pd.DataFrame([{
                'Date': t_data, 'Type': t_tipo, 'Account': t_conta, 
                'Category': t_cat, 'Amount': t_valor, 'Description': t_desc
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.success("Movimento registado com sucesso!")
            st.rerun()

# --- 3. HISTÓRICO ---
st.subheader("Últimos Movimentos")
st.dataframe(df.sort_values('Date', ascending=False), use_container_width=True, hide_index=True)
