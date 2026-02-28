import os
import sys
import datetime
import streamlit as st

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_session
from models import Task
from auth import check_auth

# Verifica se o usuário está autenticado
check_auth()

st.set_page_config(page_title="Quadro de Tarefas", page_icon="✅", layout="wide")

st.title("✅ Quadro de Tarefas de Campo")

with get_db_session() as db:
    with st.form("new_task"):
        col1, col2, col3 = st.columns(3)
        with col1:
            desc = st.text_input("Descrição da Tarefa")
        with col2:
            assignee = st.text_input("Responsável (Funcionário)")
        with col3:
            due = st.date_input("Prazo", datetime.date.today())
            
        submitted = st.form_submit_button("Criar Tarefa")
        if submitted and desc:
            new_task = Task(description=desc, assignee=assignee, status="pending", due_date=due)
            db.add(new_task)
            db.commit()
            st.success("Tarefa criada!")

    st.markdown("---")

    tasks = db.query(Task).all()

    col_pending, col_done = st.columns(2)

    with col_pending:
        st.subheader("📋 Pendentes")
        for t in tasks:
            if t.status == "pending":
                with st.container(border=True):
                    st.markdown(f"**{t.description}**")
                    st.caption(f"Responsável: {t.assignee} | Prazo: {t.due_date}")
                    if st.button("Concluir", key=f"finish_{t.id}"):
                        t.status = "completed"
                        db.commit()
                        st.rerun()

    with col_done:
        st.subheader("✔️ Concluídas")
        for t in tasks:
            if t.status == "completed":
                with st.container(border=True):
                    st.markdown(f"~~{t.description}~~")
                    st.caption(f"Responsável: {t.assignee}")
