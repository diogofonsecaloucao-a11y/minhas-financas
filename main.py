import streamlit as st
import pandas as pd

st.set_page_config(page_title="Finanças Diogo", layout="wide")

# O link deve terminar em output=csv
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTkPyqbur5kLkAIXNVIDIx1UAU3C-6xxhwAezQqPj0O06fl3TjT0BRJRgt3okezk2FEh4t5gGG6bAev/pub?gid=2004968702&single=true&output=csv"

st.title("💰 Gestão Financeira Real-Time")

try:
    # Lê os dados diretamente como CSV
    df = pd.read_csv(URL_CSV)
    
    # Ajuste de nomes de colunas (conforme vi no teu ficheiro)
    # DATE, TYPE, CATEGORIE, AMOUNT, DESCRIPTION
    
    # Limpeza do AMOUNT (remove € e converte para número)
    df['AMOUNT'] = df['AMOUNT'].astype(str).replace(r'[€\s]', '', regex=True).replace(',', '.', regex=True).astype(float)

    # Cálculos
    receitas = df[df['TYPE'] == 'Income']['AMOUNT'].sum()
    despesas = df[df['TYPE'] == 'Expense']['AMOUNT'].sum()
    saldo = receitas - despesas

    # Dashboard
    c1, c2, c3 = st.columns(3)
    c1.metric("Receitas", f"{receitas:,.2f} €")
    c2.metric("Despesas", f"{despesas:,.2f} €")
    c3.metric("Saldo Atual", f"{saldo:,.2f} €")

    st.divider()
    st.subheader("Histórico Completo")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Erro na leitura: {e}")
    st.info("Clica em Ficheiro > Publicar na Web > Transactions > CSV e usa esse link.")
