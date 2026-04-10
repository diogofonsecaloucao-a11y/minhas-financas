import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração de App Profissional
st.set_page_config(page_title="Diogo Finance", layout="centered")

# --- ESTILO BANCO (CSS) ---
st.markdown("""
    <style>
    .stMetric { background-color: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    button[kind="primary"] { background-color: #007bff; border: None; width: 100%; height: 3em; }
    .stDataFrame { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTkPyqbur5kLkAIXNVIDIx1UAU3C-6xxhwAezQqPj0O06fl3TjT0BRJRgt3okezk2FEh4t5gGG6bAev/pub?gid=2004968702&single=true&output=csv"

def load_data():
    # Lê o CSV ignorando linhas vazias iniciais
    df = pd.read_csv(URL_CSV, skiprows=range(0, 5)) # Salta o cabeçalho decorativo do Excel
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    # Limpeza rigorosa de valores
    def clean_currency(x):
        if isinstance(x, str):
            return x.replace('€', '').replace(' ', '').replace(',', '.').strip()
        return x

    df['AMOUNT'] = df['AMOUNT'].apply(clean_currency).astype(float)
    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
    return df.dropna(subset=['AMOUNT', 'TYPE'])

try:
    data = load_data()

    # --- TOP: INSERIR REGISTO (Sempre visível) ---
    with st.expander("➕ NOVO MOVIMENTO", expanded=True):
        with st.form("quick_form"):
            col_a, col_b = st.columns(2)
            f_tipo = col_a.selectbox("Tipo", ["Expense", "Income"])
            f_valor = col_b.number_input("Valor (€)", min_value=0.0, step=0.01)
            f_cat = st.selectbox("Categoria / Conta", ["Cash", "PPR", "Aforro", "Casa", "Tabaco", "Alimentação"])
            f_desc = st.text_input("Descrição")
            if st.form_submit_button("CONFIRMAR REGISTO"):
                st.info("Para gravar no Excel, use o formulário do Google Sheets. App em modo leitura.")

    st.divider()

    # --- DASHBOARD DE BANCO ---
    # Cálculo total (Income - Expense)
    total_in = data[data['TYPE'].str.contains('Income', case=False, na=False)]['AMOUNT'].sum()
    total_out = data[data['TYPE'].str.contains('Expense', case=False, na=False)]['AMOUNT'].sum()
    balance = total_in - total_out

    st.metric("SALDO TOTAL", f"{balance:,.2f} €")

    st.write("### As minhas Contas")
    c1, c2, c3 = st.columns(3)
    
    # Filtros por conta (procurando na coluna CATEGORIE ou DESCRIPTION)
    def get_val(name):
        return data[data.apply(lambda row: row.astype(str).str.contains(name, case=False).any(), axis=1)]['AMOUNT'].sum()

    # Nota: O cálculo abaixo é uma estimativa baseada nos nomes
    c1.metric("PPR", f"{get_val('PPR'):,.2f} €")
    c2.metric("Aforro", f"{get_val('Aforro'):,.2f} €")
    c3.metric("Cash", f"{get_val('Cash'):,.2f} €")

    st.divider()

    # --- ÚLTIMOS MOVIMENTOS ---
    st.write("### Últimos Movimentos")
    st.dataframe(
        data[['DATE', 'TYPE', 'CATEGORIE', 'AMOUNT', 'DESCRIPTION']]
        .sort_values(by='DATE', ascending=False)
        .head(10),
        use_container_width=True,
        hide_index=True
    )

except Exception as e:
    st.error("Erro ao carregar dados. Verifique se o Excel tem a coluna 'AMOUNT' e 'TYPE' preenchidas corretamente.")
