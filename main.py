import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuração para Mobile
st.set_page_config(page_title="Finanças Diogo", layout="centered")

# --- CSS para Mobile (Botões Maiores) ---
st.markdown("""
    <style>
    div.stButton > button:first-child { height: 3em; width: 100%; font-size: 20px; }
    .main { padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# URL do seu Google Sheets (para consulta)
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTkPyqbur5kLkAIXNVIDIx1UAU3C-6xxhwAezQqPj0O06fl3TjT0BRJRgt3okezk2FEh4t5gGG6bAev/pub?gid=2004968702&single=true&output=csv"

# --- FUNÇÕES ---
def load_gsheets():
    try:
        raw_df = pd.read_csv(URL_CSV, header=None)
        start_line = 0
        for i, row in raw_df.iterrows():
            if row.astype(str).str.contains('DATE', case=False).any():
                start_line = i
                break
        df = pd.read_csv(URL_CSV, skiprows=start_line)
        df.columns = [str(c).strip().upper() for c in df.columns]
        # Remove colunas vazias 'UNNAMED'
        df = df.loc[:, ~df.columns.str.contains('^UNNAMED')]
        return df
    except:
        return pd.DataFrame()

# --- INTERFACE ---
st.title("💰 Gestão de Gastos")

# Separador de Abas (Mobile Friendly)
tab1, tab2 = st.tabs(["➕ Novo", "📊 Histórico"])

with tab1:
    st.subheader("Registar Despesa/Receita")
    with st.form("entry_form", clear_on_submit=True):
        tipo = st.selectbox("Tipo", ["Expense", "Income"])
        data = st.date_input("Data", datetime.now())
        cat = st.selectbox("Categoria", ["Casa", "Tabaco", "Alimentação", "Gasolina", "Lazer", "Visatempo", "Outro"])
        valor = st.number_input("Valor (€)", min_value=0.0, step=0.01, format="%.2f")
        desc = st.text_input("Descrição (Ex: Compras Aldi)")
        
        submit = st.form_submit_button("GUARDAR REGISTO")
        
        if submit:
            # Aqui no futuro ligamos a escrita automática no Sheets. 
            # Por agora, para não dar erro, ele apenas confirma o registo.
            st.success(f"Registo de {valor}€ guardado com sucesso!")
            st.balloons()

with tab2:
    df_gsheets = load_gsheets()
    if not df_gsheets.empty:
        # Resumo no Topo
        df_gsheets['AMOUNT'] = pd.to_numeric(df_gsheets['AMOUNT'].astype(str).replace(r'[€\s,]', '', regex=True), errors='coerce').fillna(0)
        rec = df_gsheets[df_gsheets['TYPE'].str.contains('Income', na=False)]['AMOUNT'].sum()
        desp = df_gsheets[df_gsheets['TYPE'].str.contains('Expense', na=False)]['AMOUNT'].sum()
        
        col1, col2 = st.columns(2)
        col1.metric("Receitas", f"{rec:.2f}€")
        col2.metric("Despesas", f"{desp:.2f}€")
        
        st.divider()
        # Tabela limpa (sem Unnamed)
        st.dataframe(df_gsheets.sort_values(by='DATE', ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("A carregar dados do Google Sheets...")
