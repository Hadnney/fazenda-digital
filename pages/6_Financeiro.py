import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import check_auth

# Verifica se o usuário está autenticado
check_auth()

st.set_page_config(page_title="Financeiro", page_icon="💰", layout="wide")

st.title("💰 Dashboard Financeiro")

# Mock financial data
data = {
    "Categoria": [
        "Nutrição", "Sanidade", "Mão de Obra", "Manutenção", "Outros"
    ],
    "Custo (R$)": [15000, 5000, 12000, 3000, 1500],
    "Mês": ["Janeiro", "Janeiro", "Janeiro", "Janeiro", "Janeiro"]
}
df = pd.DataFrame(data)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribuição de Custos")
    fig = px.pie(
        df,
        values='Custo (R$)',
        names='Categoria',
        title='Custos Operacionais deste Mês'
    )
    st.plotly_chart(fig, width="stretch")

with col2:
    st.subheader("Indicadores")
    st.metric("Custo Médio por Cabeça", "R$ 45,00/mês")
    st.metric("Faturamento Projetado (Próx. Abate)", "R$ 120.000,00")
    st.metric("Lucratividade Estimada", "22%")

st.markdown("### Detalhamento")
st.dataframe(df, width="stretch")
