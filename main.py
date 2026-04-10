import streamlit as st
import pandas as pd

# Configuração de App de Banco Profissional
st.set_page_config(page_title="Diogo Bank", layout="centered")

# Estilo Dark Mode Banco
st.markdown("""
    <style>
    .stMetric { background-color: #111; border-radius: 12px; padding: 20px; border: 1px solid #222; }
    div[data-testid="stForm"] { background-color: #0e1117; border: 2px solid #007bff; border-radius: 15px; }
    h1, h2, h3 { color: #007bff; font-family: 'Helvetica', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTkPyqbur5kLkAIXNVIDIx1UAU3C-6xxhwAezQqPj0O06fl3TjT0BRJRgt3okezk2FEh4t5gGG6bAev/pub?gid=2004968702&single=true&output=csv"

def get_data_v3():
    # Lê o CSV e remove IMEDIATAMENTE colunas e linhas que sejam só espaços vazios
    df = pd.read_csv(URL_CSV).dropna(axis=1, how='all').dropna(axis=0, how='all')
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    # Limpeza profunda da coluna AMOUNT (essencial para o saldo estar certo)
    if 'AMOUNT' in df.columns:
        df['AMOUNT'] = df['AMOUNT'].astype(str).str.replace('€', '', regex=False)
        df['AMOUNT'] = df['AMOUNT'].str.replace(' ', '', regex=False).str.replace(',', '.', regex=False)
        df['AMOUNT'] = pd.to_numeric(df['AMOUNT'], errors='coerce').fillna(0)
    return df

try:
    st.title("🏦 Diogo Bank")
    data = get_data_v3()

    # --- NOVO REGISTO (SEMPRE NO TOPO) ---
    with st.form("main_form"):
        st.subheader("➕ Novo Movimento")
        c1, c2 = st.columns(2)
        tipo = c1.selectbox("Tipo", ["Expense", "Income"])
        valor = c2.number_input("Valor (€)", min_value=0.0, step=0.01)
        # Contas pedidas: PPR, Aforro, Cash
        conta = st.selectbox("Conta / Ativo", ["Cash", "PPR", "Certificados Aforro", "Banco", "Tabaco", "Alimentação"])
        desc = st.text_input("Descrição")
        if st.form_submit_button("REGISTAR AGORA"):
            st.info("Registo simulado com sucesso! Insere no Google Sheets para atualizar o saldo.")

    st.divider()

    # --- SALDOS REAIS ---
    # Somamos apenas se as colunas existirem
    if 'TYPE' in data.columns and 'AMOUNT' in data.columns:
        inc = data[data['TYPE'].str.contains('Income', case=False, na=False)]['AMOUNT'].sum()
        exp = data[data['TYPE'].str.contains('Expense', case=False, na=False)]['AMOUNT'].sum()
        saldo = inc - exp

        st.metric("SALDO TOTAL DISPONÍVEL", f"{saldo:,.2f} €")

        st.write("### Meus Ativos")
        a1, a2, a3 = st.columns(3)
        
        # Função para somar por palavra-chave em qualquer coluna
        def soma_ativo(termo):
            mask = data.apply(lambda row: row.astype(str).str.contains(termo, case=False).any(), axis=1)
            return data[mask]['AMOUNT'].sum()

        a1.metric("PPR", f"{soma_ativo('PPR'):,.2f} €")
        a2.metric("Cert. Aforro", f"{soma_ativo('Aforro'):,.2f} €")
        a3.metric("Cash", f"{soma_ativo('Cash'):,.2f} €")

    st.divider()

    # --- TABELA LIMPA ---
    st.write("### Histórico de Transações")
    # Mostra só o que interessa, sem os "Unnamed"
    cols = [c for c in ['DATE', 'TYPE', 'CATEGORIE', 'AMOUNT', 'DESCRIPTION'] if c in data.columns]
    st.dataframe(data[cols].head(20), use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Sistema em manutenção. Por favor, verifica os cabeçalhos do Excel (DATE, TYPE, AMOUNT).")
