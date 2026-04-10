import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import os

# Configuração de App Premium
st.set_page_config(page_title="Diogo Bank", layout="centered")

# --- DESIGN REVOLUT (CSS) ---
st.markdown("""
    <style>
    .stMetric { background-color: #111; border-radius: 15px; padding: 20px; border: 1px solid #222; }
    div[data-testid="stForm"] { background-color: #0e1117; border: 1px solid #007bff; border-radius: 20px; padding: 20px; }
    .stButton>button { background-color: #007bff; color: white; border-radius: 10px; width: 100%; height: 3em; font-weight: bold; }
    h1, h2, h3 { font-family: 'Inter', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- GESTÃO DE DADOS ---
DB_FILE = "financas.csv"

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    return pd.DataFrame(columns=['Date', 'Type', 'Account', 'Category', 'Amount', 'Description'])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

df = load_data()

# --- INTERFACE ---
st.title("🏦 Diogo Bank")

# 1. Dashboard de Saldos
total_income = df[df['Type'] == 'Receita']['Amount'].sum()
total_expense = df[df['Type'] == 'Despesa']['Amount'].sum()
balance = total_income - total_expense

st.metric("Saldo Total", f"{balance:,.2f} €")

col1, col2, col3 = st.columns(3)
with col1:
    val = df[(df['Account'] == 'PPR') & (df['Type'] == 'Receita')]['Amount'].sum() - \
          df[(df['Account'] == 'PPR') & (df['Type'] == 'Despesa')]['Amount'].sum()
    st.metric("PPR", f"{val:,.2f} €")
with col2:
    val = df[(df['Account'] == 'Aforro') & (df['Type'] == 'Receita')]['Amount'].sum() - \
          df[(df['Account'] == 'Aforro') & (df['Type'] == 'Despesa')]['Amount'].sum()
    st.metric("Aforro", f"{val:,.2f} €")
with col3:
    val = df[(df['Account'] == 'Cash') & (df['Type'] == 'Receita')]['Amount'].sum() - \
          df[(df['Account'] == 'Cash') & (df['Type'] == 'Despesa')]['Amount'].sum()
    st.metric("Cash", f"{val:,.2f} €")

st.divider()

# 2. Inserção Manual (Estilo Revolut)
with st.expander("➕ NOVO MOVIMENTO", expanded=True):
    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        t_tipo = c1.selectbox("Tipo", ["Despesa", "Receita"])
        t_valor = c2.number_input("Valor (€)", min_value=0.0, step=0.01, format="%.2f")
        
        t_conta = st.selectbox("Conta / Ativo", ["Banco", "PPR", "Aforro", "Cash"])
        t_cat = st.selectbox("Categoria", ["Alimentação", "Tabaco", "Casa", "Lazer", "Saúde", "Trabalho", "Outros"])
        t_desc = st.text_input("Descrição (Ex: Compras Aldi)")
        t_data = st.date_input("Data", datetime.now())
        
        if st.form_submit_button("CONFIRMAR TRANSACÇÃO"):
            new_row = pd.DataFrame([{
                'Date': t_data, 'Type': t_tipo, 'Account': t_conta, 
                'Category': t_cat, 'Amount': t_valor, 'Description': t_desc
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)
            st.success("Movimento registado!")
            st.rerun()

st.divider()

# 3. Gráfico de Gastos
if not df.empty:
    st.subheader("Análise de Gastos")
    df_gastos = df[df['Type'] == 'Despesa']
    if not df_gastos.empty:
        fig = px.pie(df_gastos, values='Amount', names='Category', hole=0.6, 
                     color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig, use_container_width=True)

    # 4. Histórico
    st.subheader("Últimos Movimentos")
    st.dataframe(df.sort_values('Date', ascending=False), use_container_width=True, hide_index=True)
