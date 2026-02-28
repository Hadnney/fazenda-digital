import os
import sys
import streamlit as st

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from langchain... (Imports would go here)
from auth import check_auth

st.set_page_config(page_title="IA e Agentes", page_icon="🤖", layout="wide")

# Verifica se o usuário está autenticado
check_auth()

st.title("🤖 Inteligência Artificial e Agentes")
st.warning(
    "⚠️ Nota: É necessário configurar a API KEY da OpenAI no .env "
    "para ativar os agentes."
)

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Agentes Ativos")
    st.success("✅ HealthMonitor (Monitor de Saúde)")
    st.success("✅ LogisticsAgent (Otimizador de Insumos)")
    st.success("✅ SlaughterAdvisor (Previsão de Abate)")
    
    agent_selection = st.radio("Falar com:", ["HealthMonitor", "LogisticsAgent", "SlaughterAdvisor"])

with col2:
    st.subheader("Console do Agente")
    
    chat_container = st.container()
    
    with chat_container:
        st.markdown(f"**{agent_selection} diz:** Olá! Como posso ajudar com a gestão da fazenda hoje?")
        
    user_input = st.text_input("Sua pergunta ou comando:")
    
    if st.button("Enviar"):
        if not os.environ.get("OPENAI_API_KEY"):
            st.error("OpenAI API Key não encontrada.")
        else:
            # Here we would call the LangChain agent
            st.info(f"Processando pergunta para {agent_selection}...")
            # response = agent.run(user_input)
            st.markdown(f"**{agent_selection} diz:** (Simulação) Analisei os dados recentes e detectei que o Piquete 2 tem uma queda no ganho de peso médio. Sugiro verificar a qualidade do pasto.")
