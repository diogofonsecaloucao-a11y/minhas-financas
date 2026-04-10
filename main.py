import streamlit as st
import pandas as pd

# Design Estilo Banco
st.set_page_config(page_title="Diogo Finance", layout="centered")

st.markdown("""
    <style>
    .stMetric { background-color: #111; border-radius: 10px; padding: 15px; border: 1px solid #333; }
    [data-testid="stForm"] { border: 1px solid #007bff; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTkPyqbur5kLkAIXNVIDIx1UAU3C-6xxhwAezQqPj0O06fl3TjT0BRJRgt3okezk2FEh4t5gGG6bAev/pub?gid=2004968702&single=true&output=csv"

def get_clean_data():
    # Lê os dados e encontra onde a tabela começa mesmo
    raw = pd.read_csv(URL_CSV, header=None)
    header_idx = raw.index[raw.astype(str).apply(lambda x: x.str.contains('DATE', case=False)).any(axis=1)].tolist()[0]
    df = pd.read_csv(URL_CSV, skiprows=header_idx)
    df.columns = [c.strip().upper() for c in df.columns]
    
    # Limpa valores: remove € e converte para número
    df['AMOUNT'] = df['AMOUNT'].astype(str).str.replace('€', '').str.replace(' ', '').str.replace(',', '.').astype(float)
    return df.dropna(subset=['AMOUNT', 'TYPE'])

try:
    data = get_clean_data()

    # --- 1. ÁREA DE REGISTO (NO TOPO) ---
    st.title("🏦 Diogo Digital Bank")
    with st.form("new_entry"):
        st.write("### ➕ Novo Registo")
        c1, c2 = st.columns(2)
        f_tipo = c1.selectbox("Tipo", ["Expense", "Income"])
        f_valor = c2.number_input("Valor (€)", min_value=0.0, step=0.01)
        f_cat = st.selectbox("Conta / Categoria", ["Cash", "PPR", "Certificados Aforro", "Banco", "Tabaco", "Alimentação"])
        f_desc = st.text_input("Descrição (Ex: Jantar, Reforço PPR)")
        if st.form_submit_button("CONFIRMAR E GUARDAR"):
            st.warning("⚠️ Para gravar permanentemente, insere no teu Google Sheets. Esta App está em modo visualização.")

    st.divider()

    # --- 2. DASHBOARD DE SALDOS ---
    total_in = data[data['TYPE'].str.contains('Income', case=False)]['AMOUNT'].sum()
    total_out = data[data['TYPE'].str.contains('Expense', case=False)]['AMOUNT'].sum()
    saldo_real = total_in - total_out

    st.metric("SALDO TOTAL DISPONÍVEL", f"{saldo_real:,.2f} €")

    st.write("#### Meus Ativos")
    m1, m2, m3 = st.columns(3)
    
    # Função para somar por conta específica
    def soma_conta(nome):
        mask = data.apply(lambda x: x.astype(str).str.contains(nome, case=False)).any(axis=1)
        return data[mask]['AMOUNT'].sum()

    m1.metric("PPR", f"{soma_conta('PPR'):,.2f} €")
    m2.metric("Aforro", f"{soma_conta('Aforro'):,.2f} €")
    m3.metric("Cash", f"{soma_conta('Cash'):,.2f} €")

    st.divider()

    # --- 3. ÚLTIMOS MOVIMENTOS ---
    st.write("#### Movimentos Recentes")
    st.dataframe(data[['DATE', 'TYPE', 'CATEGORIE', 'AMOUNT', 'DESCRIPTION']].head(10), 
                 use_container_width=True, hide_index=True)

except Exception:
    st.error("A carregar base de dados... Se este erro persistir, verifica se o cabeçalho no Excel está na primeira linha.")
