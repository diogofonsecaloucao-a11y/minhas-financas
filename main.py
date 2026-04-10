import streamlit as st
import pandas as pd

st.set_page_config(page_title="Finanças Diogo", layout="wide")

# O teu link de Publicar na Web (CSV)
URL_CSV = "COLA_AQUI_O_TEU_LINK_CSV" 

st.title("💰 Gestão Financeira Real-Time")

try:
    # Lê os dados
    df = pd.read_csv(URL_CSV)
    
    # Converter nomes das colunas para MAIÚSCULAS e tirar espaços para evitar erros
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    # Debug: Mostra as colunas encontradas se houver erro (ajuda a descobrir o nome)
    colunas_disponiveis = df.columns.tolist()

    if 'AMOUNT' in df.columns:
        # Limpeza do valor
        df['AMOUNT'] = df['AMOUNT'].astype(str).replace(r'[€\s]', '', regex=True).replace(',', '.', regex=True)
        df['AMOUNT'] = pd.to_numeric(df['AMOUNT'], errors='coerce').fillna(0)

        # Cálculos de Receitas e Despesas
        # Procura por 'INCOME' ou 'EXPENSE' na coluna TYPE
        receitas = df[df['TYPE'].astype(str).str.contains('Income', case=False, na=False)]['AMOUNT'].sum()
        despesas = df[df['TYPE'].astype(str).str.contains('Expense', case=False, na=False)]['AMOUNT'].sum()
        saldo = receitas - despesas

        # Dashboard
        c1, c2, c3 = st.columns(3)
        c1.metric("Receitas", f"{receitas:,.2f} €")
        c2.metric("Despesas", f"{despesas:,.2f} €")
        c3.metric("Saldo Atual", f"{saldo:,.2f} €")

        st.divider()
        st.subheader("Histórico Completo")
        st.dataframe(df, use_container_width=True)
    else:
        st.error(f"Não encontrei a coluna AMOUNT. As colunas que detetei são: {colunas_disponiveis}")
        st.info("Verifica se o cabeçalho na tua folha de Excel está na primeira linha.")

except Exception as e:
    st.error(f"Erro: {e}")
