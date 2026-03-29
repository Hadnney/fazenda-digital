import streamlit as st
import os
from auth import check_auth

st.set_page_config(page_title="Configurações do Sistema", page_icon="⚙️")

check_auth()

st.title("⚙️ Configurações do Sistema")

st.markdown("---")

st.subheader("Modo de Manutenção")
st.write("Ativar o modo de manutenção ocultará todo o conteúdo do aplicativo e exibirá uma tela informando que o sistema está em manutenção.")

if st.button("Desabilitar Aplicação (Entrar em Manutenção)", type="primary"):
    with open("maintenance.flag", "w") as f:
        f.write("maintenance")
    st.rerun()
