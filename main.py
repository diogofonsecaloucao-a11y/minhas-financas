import streamlit as st
import pandas as pd
import gspread
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="Finanças Diogo", layout="wide")

# --- CONEXÃO GOOGLE SHEETS ---
# URL do teu ficheiro que me passaste
SHEET_URL = "https://docs.google.com/spreadsheets/d/12YOiNnEnsnH4P2cEHp8alI2--KtTGbhhtMx8xO2pOcI/edit?usp=sharing"

def load_data():
    # Ligação pública (funciona porque puseste como "Qualquer pessoa com link pode editar")
    gc = gspread.public_api()
    sh = gc.open_by_url(SHEET_URL)
    worksheet = sh.worksheet("Transactions")
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    # Limpeza de valores monetários (remove € e converte para número)
    if 'AMOUNT' in df.columns:
        df['AMOUNT'] = df['AMOUNT'].replace(r'[€\s,]', '', regex=True).replace('', '0').astype(float)
    return df

# --- INTERFACE ---
st.title("💰 Gestão Financeira (Google Sheets)")

try:
    df = load_data()

    # Sidebar para mostrar que está ligado
    st.sidebar.success("Ligado ao Google Sheets!")
    st.sidebar.info(f"Últimos registos lidos: {len(df)}")

    # DASHBOARD COM DADOS REAIS
    receitas = df[df['TYPE'] == 'Income']['AMOUNT'].sum()
    despesas = df[df['TYPE'] == 'Expense']['AMOUNT'].sum()
    saldo_atual = receitas - despesas

    col1, col2, col3 = st.columns(3)
    col1.metric("Receitas Totais", f"{receitas:,.2f} €")
    col2.metric("Despesas Totais", f"{despesas:,.2f} €", delta=f"-{despesas:,.2f} €", delta_color="inverse")
    col3.metric("Saldo em Carteira", f"{saldo_atual:,.2f} €")

    st.divider()

    # TABELA DE TRANSAÇÕES
    st.subheader("Histórico do Google Sheets")
    st.dataframe(df.sort_values(by='DATE', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"Erro ao ligar ao Sheets: {e}")
    st.info("Verifica se o ficheiro ainda está partilhado como 'Qualquer pessoa com o link pode editar'.")
