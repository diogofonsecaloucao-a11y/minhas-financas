import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Finanças Diogo", layout="wide")

URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTkPyqbur5kLkAIXNVIDIx1UAU3C-6xxhwAezQqPj0O06fl3TjT0BRJRgt3okezk2FEh4t5gGG6bAev/pub?gid=2004968702&single=true&output=csv"

@st.cache_data(ttl=300) # Atualiza a cada 5 min
def load_data():
    raw_df = pd.read_csv(URL_CSV, header=None)
    start_line = 0
    for i, row in raw_df.iterrows():
        if row.astype(str).str.contains('DATE', case=False).any():
            start_line = i
            break
    df = pd.read_csv(URL_CSV, skiprows=start_line)
    df.columns = [str(c).strip().upper() for c in df.columns]
    df = df.loc[:, ~df.columns.str.contains('^UNNAMED')]
    
    # Tratamento de Datas e Valores
    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
    df['AMOUNT'] = pd.to_numeric(df['AMOUNT'].astype(str).replace(r'[€\s,]', '', regex=True), errors='coerce').fillna(0)
    df['MONTH'] = df['DATE'].dt.strftime('%b %Y')
    df['YEAR'] = df['DATE'].dt.year
    return df.dropna(subset=['DATE'])

try:
    df = load_data()

    # --- SIDEBAR FILTERS ---
    st.sidebar.title("⚙️ Filtros")
    # Se não tiveres a coluna ACCOUNT no Excel, o código usará categorias como contas
    lista_anos = sorted(df['YEAR'].unique().tolist(), reverse=True)
    filtro_ano = st.sidebar.selectbox("Ano", lista_anos)
    
    lista_meses = df[df['YEAR'] == filtro_ano]['MONTH'].unique().tolist()
    filtro_mes = st.sidebar.multiselect("Meses", lista_meses, default=lista_meses)

    # --- DASHBOARD PRINCIPAL ---
    st.title("📊 Resumo Financeiro")
    
    # Filtrar DF para os cálculos
    df_filtered = df[(df['YEAR'] == filtro_ano) & (df['MONTH'].isin(filtro_mes))]

    # Cálculos Totais
    total_receitas = df_filtered[df_filtered['TYPE'].str.contains('Income', case=False, na=False)]['AMOUNT'].sum()
    total_despesas = df_filtered[df_filtered['TYPE'].str.contains('Expense', case=False, na=False)]['AMOUNT'].sum()
    patrimonio = total_receitas - total_despesas

    # Layout de Métricas
    m1, m2, m3 = st.columns(3)
    m1.metric("Património (Período)", f"{patrimonio:,.2f} €")
    m2.metric("Receitas", f"{total_receitas:,.2f} €", delta_color="normal")
    m3.metric("Despesas", f"{total_despesas:,.2f} €", delta=f"-{total_despesas:,.2f}", delta_color="inverse")

    st.divider()

    # --- CONTAS ESPECÍFICAS ---
    st.subheader("💰 Saldos por Ativo")
    c1, c2, c3 = st.columns(3)
    
    # Nota: Aqui o código assume que tens uma coluna CATEGORIE ou ACCOUNT 
    # Vou filtrar por categorias comuns que pediste
    ppr_val = df[df.astype(str).apply(lambda x: x.str.contains('PPR', case=False)).any(axis=1)]['AMOUNT'].sum()
    aforro_val = df[df.astype(str).apply(lambda x: x.str.contains('Aforro', case=False)).any(axis=1)]['AMOUNT'].sum()
    cash_val = df[df.astype(str).apply(lambda x: x.str.contains('Cash|Dinheiro', case=False)).any(axis=1)]['AMOUNT'].sum()

    c1.info(f"**PPR**\n\n {ppr_val:,.2f} €")
    c2.info(f"**Cert. Aforro**\n\n {aforro_val:,.2f} €")
    c3.info(f"**Cash**\n\n {cash_val:,.2f} €")

    st.divider()

    # --- GRÁFICOS ---
    col_graph1, col_graph2 = st.columns(2)
    
    with col_graph1:
        st.write("### Despesas por Categoria")
        despesas_cat = df_filtered[df_filtered['TYPE'].str.contains('Expense', case=False, na=False)].groupby('CATEGORIE')['AMOUNT'].sum()
        st.bar_chart(despesas_cat)

    with col_graph2:
        st.write("### Evolução Mensal")
        evolucao = df_filtered.groupby('MONTH')['AMOUNT'].sum()
        st.line_chart(evolucao)

    # --- FORMULÁRIO DE INSERÇÃO (Flutuante no fundo ou nova aba) ---
    with st.expander("➕ Inserir Novo Registo"):
        with st.form("form_novo"):
            f_tipo = st.selectbox("Tipo", ["Expense", "Income"])
            f_conta = st.selectbox("Conta/Ativo", ["Banco", "PPR", "Aforro", "Cash"])
            f_valor = st.number_input("Valor", min_value=0.0)
            f_submit = st.form_submit_button("Submeter")
            if f_submit:
                st.warning("A submissão direta para o Sheets requer configuração de API. O registo foi simulado.")

except Exception as e:
    st.error(f"Erro ao processar dashboard: {e}")
