import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Finanças Diogo", layout="wide")

st.title("💰 Gestão Financeira (Google Sheets)")

# URL limpo para evitar o erro 400
url = "https://docs.google.com/spreadsheets/d/12YOiNnEnsnH4P2cEHp8alI2--KtTGbhhtMx8xO2pOcI/edit#gid=0"

try:
    # Criar a conexão
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Ler os dados da folha "Transactions"
    # Adicionei o ttl=0 para garantir que ele lê sempre a versão mais recente
    df = conn.read(spreadsheet=url, worksheet="Transactions", ttl=0)

    # Limpar e converter a coluna AMOUNT para número
    df['AMOUNT'] = df['AMOUNT'].astype(str).replace(r'[€\s]', '', regex=True).replace(',', '.', regex=True).astype(float)

    # --- DASHBOARD ---
    receitas = df[df['TYPE'] == 'Income']['AMOUNT'].sum()
    despesas = df[df['TYPE'] == 'Expense']['AMOUNT'].sum()
    saldo_atual = receitas - despesas

    col1, col2, col3 = st.columns(3)
    col1.metric("Receitas Totais", f"{receitas:,.2f} €")
    col2.metric("Despesas Totais", f"{despesas:,.2f} €", delta=f"-{despesas:,.2f} €", delta_color="inverse")
    col3.metric("Saldo em Carteira", f"{saldo_atual:,.2f} €")

    st.divider()

    # --- TABELA ---
    st.subheader("Histórico de Transações")
    st.dataframe(df.sort_values(by='DATE', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"Erro técnico: {e}")
    st.info("Dica: Abre o teu Google Sheets e confirma se o nome da aba no fundo é exatamente 'Transactions' (com T maiúsculo).")
