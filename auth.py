import streamlit as st
import os

# Credenciais de acesso
AUTH_USERNAME = "hoot"
AUTH_PASSWORD = "lavora123"


def check_maintenance():
    FLAG_FILE = "maintenance.flag"
    if os.path.exists(FLAG_FILE):
        st.markdown(
            """
            <style>
                #MainMenu {visibility: hidden;}
                header {visibility: hidden;}
                [data-testid="stSidebar"] {display: none;}
            </style>
            """,
            unsafe_allow_html=True
        )
        st.markdown("<h1 style='text-align: center; margin-top: 20vh;'>Em manutenção</h1>", unsafe_allow_html=True)
        st.write("")
        
        # Apenas mostrar botão de habilitar se rodando localmente (onde .env existe ou está fora da nuvem Streamlit)
        if os.path.exists(".env") or os.path.exists(".vscode"):
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("Habilitar Aplicação Local (Admin)", use_container_width=True):
                    os.remove(FLAG_FILE)
                    st.rerun()
        st.stop()


def check_auth():
    """
    Verifica se o usuário está autenticado.
    Exibe formulário de login com usuário/senha se não estiver logado.
    """
    check_maintenance()
    
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔐 Acesso Restrito - Fazenda Digital")

        with st.form("login_form"):
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            submitted = st.form_submit_button("Entrar", use_container_width=True)

            if submitted:
                if username == AUTH_USERNAME and password == AUTH_PASSWORD:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos.")

        st.stop()

    # Se estiver logado, exibe botão de logout no sidebar
    with st.sidebar:
        if st.button("Sair (Logout)"):
            st.session_state.authenticated = False
            st.rerun()


def is_authenticated():
    """Retorna True se o usuário estiver logado."""
    return st.session_state.get("authenticated", False)
