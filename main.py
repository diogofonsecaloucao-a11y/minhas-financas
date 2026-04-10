import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import os

# Configuração Base
st.set_page_config(page_title="MyFinance", layout="centered", initial_sidebar_state="collapsed")

# --- CSS ULTRA CUSTOMIZADO (REVOLUT DARK STYLE) ---
st.markdown("""
    <style>
    /* Fundo e Geral */
    .stApp { background-color: #000000; color: #FFFFFF; }
    
    /* Cartão de Saldo Principal */
    .balance-card {
        background: linear-gradient(135deg, #1e3a8a 0%, #000000 100%);
        padding: 30px;
        border-radius: 25px;
        text-align: center;
        border: 1px solid #222;
        margin-bottom: 25px;
        box-shadow: 0px 10px 20px rgba(0,0,0,0.5);
    }
    
    /* Carrossel de Bancos (Simulado) */
    .bank-card {
        background: #111111;
        padding: 15px;
        border-radius: 18px;
        border: 1px solid #333;
        min-width: 140px;
        text-align: center;
        margin-right: 10px;
        display: inline-block;
    }

    /* Menu Inferior Fixo */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #000;
        border-top: 1px solid #222;
        padding: 10px;
        text-align: center;
        z-index: 999;
    }
    
    /* Inputs e Botões */
    div[data-testid="stForm"] { border: none; padding: 0; }
    .stButton>button {
        background: linear-gradient(90deg, #007bff, #00d4ff);
        border: none;
        border-radius: 12px;
        color: white;
        font-weight: bold;
        height: 3.5em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE DADOS ---
DB_FILE = "myfinance_data.csv"
def load_db():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=['Date', 'Type', 'Account', 'Category', 'Amount'])

df = load_db()

# --- NAVEGAÇÃO POR TABS ---
# Como o Streamlit não tem menu inferior nativo, usamos as Tabs do Streamlit estilizadas
tab_home, tab_new, tab_config = st.tabs(["🏠 Início", "➕ Novo", "⚙️ Bancos"])

# --- TAB INÍCIO ---
with tab_home:
    # Cabeçalho com Logo
    st.markdown("<h2 style='text-align: center;'>MyFinance</h2>", unsafe_allow_html=True)
    
    # Saldo Total
    total_in = df[df['Type'] == 'Receita']['Amount'].sum()
    total_out = df[df['Type'] == 'Despesa']['Amount'].sum()
    st.markdown(f"""
        <div class='balance-card'>
            <p style='color: #aaa; margin-bottom: 5px;'>Saldo Total</p>
            <h1 style='font-size: 45px; margin: 0;'>{total_in - total_out:,.2f} €</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Bancos (Carrossel Horizontal)
    st.write("### Meus Bancos")
    bancos = ["Moey", "Crédito Agrícola", "Trade Republic"]
    cols = st.columns(3)
    for i, b in enumerate(bancos):
        b_in = df[(df['Account'] == b) & (df['Type'] == 'Receita')]['Amount'].sum()
        b_out = df[(df['Account'] == b) & (df['Type'] == 'Despesa')]['Amount'].sum()
        cols[i].markdown(f"""
            <div class='bank-card'>
                <p style='font-size: 12px; color: #888; margin:0;'>{b}</p>
                <p style='font-size: 16px; font-weight: bold; margin:0;'>{b_in - b_out:,.0f}€</p>
            </div>
        """, unsafe_allow_html=True)

    # Gráfico de Barras Comparativo
    st.write("### Ganhos vs Gastos")
    if not df.empty:
        fig = go.Figure(data=[
            go.Bar(name='Receitas', x=['Total'], y=[total_in], marker_color='#00d4ff'),
            go.Bar(name='Despesas', x=['Total'], y=[total_out], marker_color='#ff4b4b')
        ])
        fig.update_layout(barmode='group', template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300)
        st.plotly_chart(fig, use_container_width=True)

# --- TAB NOVO (O FORMULÁRIO) ---
with tab_new:
    st.subheader("➕ Registar Movimento")
    with st.form("revolut_form"):
        tipo = st.selectbox("O que aconteceu?", ["Despesa", "Receita"])
        valor = st.number_input("Valor (€)", min_value=0.0, format="%.2f")
        conta = st.selectbox("Qual a conta?", bancos)
        cat = st.selectbox("Categoria", ["Tabaco", "Alimentação", "Casa", "Lazer", "Salário", "Outros"])
        data_mov = st.date_input("Data", datetime.now())
        
        if st.form_submit_button("CONFIRMAR"):
            new_data = pd.DataFrame([{'Date': data_mov, 'Type': tipo, 'Account': conta, 'Category': cat, 'Amount': valor}])
            df = pd.concat([df, new_data], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.success("Registado!")
            st.rerun()

# --- TAB CONFIG ---
with tab_config:
    st.subheader("Configurações")
    st.write("Aqui poderás gerir os nomes dos teus bancos e exportar os teus dados.")
    if st.button("Limpar Todos os Dados"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            st.rerun()
