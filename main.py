import streamlit as st
import pandas as pd
import plotly.express as px # Precisas disto para o gráfico
from datetime import datetime
import os

# ... (Manteve-se o CSS e a configuração inicial do código anterior) ...

# DASHBOARD (HOME)
if st.session_state.step == 0:
    st.markdown("<h2 style='text-align:center;'>MyFinance</h2>", unsafe_allow_html=True)
    
    df = pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame(columns=['Date', 'Type', 'Amount', 'Account', 'Category'])
    
    # 1. SALDO TOTAL
    inc = df[df['Type'] == 'Receita']['Amount'].sum()
    exp = df[df['Type'] == 'Despesa']['Amount'].sum()
    st.markdown(f"<div class='balance-header'><small>Património Total</small><h1>{inc - exp:,.2f} €</h1></div>", unsafe_allow_html=True)

    # 2. NOVO: GRÁFICO DE GASTOS (ONDE VAO OS EUROS?)
    if not df.empty and exp > 0:
        st.write("### Onde gasto o meu dinheiro?")
        # Filtramos apenas as despesas
        df_gastos = df[df['Type'] == 'Despesa']
        
        # Criamos o gráfico circular moderno
        fig = px.pie(df_gastos, values='Amount', names='Category', 
                     hole=0.6, # Transforma em Donut
                     color_discrete_sequence=px.colors.sequential.RdBu)
        
        fig.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0), height=250)
        st.plotly_chart(fig, use_container_width=True)

    # 3. LISTA DE MOVIMENTOS
    st.write("### Atividade Recente")
    # ... (Resto do código do histórico que já tinhas) ...
