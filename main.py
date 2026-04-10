import streamlit as st
import pandas as pd

# Configuração de App de Banco
st.set_page_config(page_title="Diogo Bank", layout="centered")

# Estilo para parecer uma App Profissional no telemóvel
st.markdown("""
    <style>
    .stMetric { background-color: #111; border-radius: 12px; padding: 20px; border: 1px solid #222; }
    div[data-testid="stForm"] { background-color: #0e1117; border: 1px solid #007bff; border-radius: 15px; }
    h1, h2, h3 { color: #007bff; }
    </style>
    """, unsafe_allow_html=True)

URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTkPyqbur5kLkAIXNVIDIx1UAU3C-6xxhwAezQqPj0O06fl3TjT0BRJRgt3okezk2FEh4t5gGG6bAev/pub?gid=2004968702&single=true&output=csv"

def get_data():
    # Lê tudo e limpa colunas e linhas fantasma que o Google envia
    df = pd.read_csv(URL_CSV)
    # Encontra as colunas reais ignorando as vazias
    df = df.dropna(axis=1, how='all').dropna(axis=0, how='all')
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    # Limpa a coluna de valores (tira o € e converte para número real)
    if 'AMOUNT' in df.columns:
        df['AMOUNT'] = df['AMOUNT'].astype(str).str.replace('€', '').str.replace(' ', '').str.replace(',', '.').astype(float)
    return df

try:
    data = get_data()

    st.title("🏦 Diogo Bank")

    # --- ÁREA DE REGISTO (LOGO NO TOPO) ---
    with st.form("add_new"):
        st.subheader("➕ Novo Movimento")
        tipo = st.selectbox("Tipo", ["Expense", "Income"])
        valor = st.number_input("Valor (€)", min_value=0.0, step=0.01)
        # Contas que tu pediste
        conta = st.selectbox("Conta / Ativo", ["Cash", "PPR", "Certificados Aforro", "Banco", "Tabaco", "Alimentação"])
        desc = st.text_input("Descrição")
        if st.form_submit_button("REGISTAR AGORA"):
            st.info("Registo simulado! Para gravar a sério, insere na tua folha de Google Sheets.")

    st.divider()

    # --- DASHBOARD DE SALDOS ---
    # Cálculo de Saldo Total
    total_in = data[data['TYPE'].str.contains('Income', case=False, na=False)]['AMOUNT'].sum()
    total_out = data[data['TYPE'].str.contains('Expense', case=False, na=False)]['AMOUNT'].sum()
    saldo_total = total_in - total_out

    st.metric("SALDO TOTAL", f"{saldo_total:,.2f} €")

    # Saldos por Ativo (PPR, Aforro, Cash)
    st.write("### Meus Ativos")
    c1, c2, c3 = st.columns(3)
    
    def calc_ativo(nome):
        # Procura o nome nas colunas CATEGORIE ou DESCRIPTION
        mask = data.apply(lambda row: row.astype(str).str.contains(nome, case=False).any(), axis=1)
        return data[mask]['AMOUNT'].sum()

    c1.metric("PPR", f"{calc_ativo('PPR'):,.2f} €")
    c2.metric("Aforro", f"{calc_ativo('Aforro'):,.2f} €")
    c3.metric("Cash", f"{calc_ativo('Cash'):,.2f} €")

    st.divider()

    # --- MOVIMENTOS ---
    st.write("### Últimos Movimentos")
    # Mostra apenas as colunas que interessam, sem lixo
    colunas_limpas = [c for c in ['DATE', 'TYPE', 'CATEGORIE', 'AMOUNT', 'DESCRIPTION'] if c in data.columns]
    st.dataframe(data[colunas_limpas].head(15), use_container_width=True, hide_index=True)

except Exception as e:
    st.error("Erro ao ligar ao Banco. Verifica se o teu Excel tem as colunas DATE, TYPE e AMOUNT.")
