import streamlit as st
import pandas as pd

st.set_page_config(page_title="Finanças Diogo", layout="wide")

# O teu link CSV direto
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTkPyqbur5kLkAIXNVIDIx1UAU3C-6xxhwAezQqPj0O06fl3TjT0BRJRgt3okezk2FEh4t5gGG6bAev/pub?gid=2004968702&single=true&output=csv"

st.title("💰 Gestão Financeira Real-Time")

try:
    # Lemos o ficheiro sem cabeçalho primeiro para encontrar a linha real dos dados
    raw_df = pd.read_csv(URL_CSV, header=None)
    
    # Procura a linha que contém a palavra 'DATE' ou 'DATE '
    start_line = 0
    for i, row in raw_df.iterrows():
        if row.astype(str).str.contains('DATE', case=False).any():
            start_line = i
            break
            
    # Re-lemos o ficheiro saltando as linhas inúteis do topo
    df = pd.read_csv(URL_CSV, skiprows=start_line)
    
    # Limpeza de nomes de colunas
    df.columns = [str(c).strip().upper() for c in df.columns]

    if 'AMOUNT' in df.columns:
        # Converter AMOUNT para número (lidando com o símbolo €)
        df['AMOUNT'] = df['AMOUNT'].astype(str).replace(r'[€\s]', '', regex=True).replace(',', '.', regex=True)
        df['AMOUNT'] = pd.to_numeric(df['AMOUNT'], errors='coerce').fillna(0)

        # Filtros de Receitas e Despesas
        receitas = df[df['TYPE'].astype(str).str.contains('Income', case=False, na=False)]['AMOUNT'].sum()
        despesas = df[df['TYPE'].astype(str).str.contains('Expense', case=False, na=False)]['AMOUNT'].sum()
        saldo = receitas - despesas

        # Dashboard
        c1, c2, c3 = st.columns(3)
        c1.metric("Receitas", f"{receitas:,.2f} €")
        c2.metric("Despesas", f"{despesas:,.2f} €")
        c3.metric("Saldo Atual", f"{saldo:,.2f} €")

        st.divider()
        st.subheader("Histórico Detetado")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Ainda não encontrei a coluna 'AMOUNT'.")
        st.write("Colunas detetadas na linha de dados:", df.columns.tolist())

except Exception as e:
    st.error(f"Erro na leitura: {e}")
