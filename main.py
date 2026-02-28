import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_db_session
from models import Animal, Paddock, Task
from auth import check_auth

# Verifica se o usuário está autenticado
check_auth()



st.set_page_config(
    page_title="Fazenda Digital - Gestão Inteligente",
    page_icon="🐄",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📊 Dashboard Executivo")

with get_db_session() as db:
    # Fetch Key Metrics
    total_animals = db.query(Animal).filter(Animal.status == 'active').count()
    total_paddocks = db.query(Paddock).count()
    pending_tasks = db.query(Task).filter(Task.status == 'pending').count()

    # Mock GMD calculation (avg of recent weight events - simplified)
    avg_gmd = 0.85  # Placeholder

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Total de Cabeças",
            f"{total_animals}",
            delta="+2 esta semana"
        )
    with col2:
        st.metric("GMD Médio (Rebanho)", f"{avg_gmd:.2f} kg/dia", delta="0.05")
    with col3:
        st.metric("Piquetes em Uso", f"{total_paddocks}", delta="100%")
    with col4:
        st.metric(
            "Tarefas Pendentes",
            f"{pending_tasks}",
            delta_color="inverse"
        )

    st.markdown("---")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("Evolução do Rebanho")
        # Mock data for chart
        chart_data = pd.DataFrame({
            "Mês": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"],
            "Peso Médio": [420, 435, 450, 468, 485, 500],
            "Cabeças": [480, 485, 490, 492, 495, 500]
        })

        tab_chart1, tab_chart2 = st.tabs(["Peso Médio", "Total de Cabeças"])
        with tab_chart1:
            fig_weight = px.line(chart_data, x="Mês", y="Peso Médio", markers=True)
            st.plotly_chart(
                fig_weight,
                width="stretch"
            )
        with tab_chart2:
            fig_heads = px.bar(chart_data, x="Mês", y="Cabeças")
            st.plotly_chart(
                fig_heads,
                width="stretch"
            )

    with col_right:
        st.subheader("Alertas Recentes")
        st.warning("⚠️ Piquete 2: Escore de Pasto Baixo (3.0)")
        st.error("🚨 Animal 1042: Perda de Peso Brusca (-5kg)")
        st.info("ℹ️ Campanha de Vacinação Aftosa em 10 dias")

        st.markdown("### Tarefas Urgentes")
        tasks = db.query(Task).filter(Task.status == 'pending').limit(3).all()
        for task in tasks:
            st.checkbox(
                f"{task.description} ({task.assignee})",
                key=f"task_{task.id}"
            )
