import os
import sys
import datetime
import streamlit as st

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_session
from models import Score, Paddock, Event, Animal
from auth import check_auth

st.set_page_config(page_title="Manejo e Coleta", page_icon="📝", layout="wide")

# Verifica se o usuário está autenticado
check_auth()

st.title("📝 Coleta de Dados e Manejo")

tab1, tab2 = st.tabs(["Escores de Campo", "Manejo de Curral"])

with get_db_session() as db:
    with tab1:
        st.header("Lançamento de Escores")
        
        col1, col2 = st.columns(2)
        with col1:
            paddocks = db.query(Paddock).all()
            paddock_map = {p.name: p.id for p in paddocks}
            if paddock_map:
                selected_paddock_name = st.selectbox(
                    "Selecione o Piquete",
                    list(paddock_map.keys())
                )
            else:
                st.warning("Nenhum piquete cadastrado.")
                selected_paddock_name = None
            
            date = st.date_input("Data da Coleta", datetime.date.today())
        
        with col2:
            score_type = st.selectbox(
                "Tipo de Escore",
                ["Escore de Pasto", "Escore de Fezes", "Escore de Cocho"]
            )
            value = st.slider("Valor (0-10 ou %)", 0.0, 100.0, 50.0)
            notes = st.text_area("Observações")
            
        if st.button("Salvar Escore"):
            if selected_paddock_name:
                try:
                    new_score = Score(
                        paddock_id=paddock_map[selected_paddock_name],
                        date=date,
                        score_type=score_type,
                        value=value,
                        notes=notes
                    )
                    db.add(new_score)
                    db.commit()
                    st.success("Escore registrado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")
            else:
                st.error("Selecione um piquete.")

    with tab2:
        st.header("Manejo de Curral (Rápido)")
        
        st.info("Registre eventos para múltiplos animais ou animal individual.")
        
        if 'scanned_rfid_coleta' not in st.session_state:
            st.session_state.scanned_rfid_coleta = ""
        if 'show_camera_coleta' not in st.session_state:
            st.session_state.show_camera_coleta = False

        container_coleta = st.container()
        with container_coleta:
            if st.session_state.show_camera_coleta:
                st.info("Aponte o QR Code para a câmera.")
                img_file_buffer = st.camera_input("Scanner Manejo")
                if img_file_buffer is not None:
                    try:
                        import cv2
                        import numpy as np
                        import zxingcpp
                        
                        file_bytes = np.asarray(bytearray(img_file_buffer.read()), dtype=np.uint8)
                        image = cv2.imdecode(file_bytes, 1)
                        
                        resultados = zxingcpp.read_barcodes(image)
                        
                        if resultados:
                            data = resultados[0].text
                        else:
                            # Tenta aumentar contraste
                            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                            _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
                            resultados_th = zxingcpp.read_barcodes(thresh)
                            data = resultados_th[0].text if resultados_th else None
                        
                        if data:
                            st.session_state.scanned_rfid_coleta = data
                            st.session_state.show_camera_coleta = False
                            st.rerun()
                        else:
                            st.warning("Nenhum código detectado. Tente aproximar ou melhorar a iluminação.")
                    except Exception as e:
                        st.error(f"Erro ao processar imagem: {e}")
                
                if st.button("Cancelar Leitura", key="cancel_scan_coleta"):
                    st.session_state.show_camera_coleta = False
                    st.rerun()

            col_rfid, col_btn = st.columns([5, 1])
            with col_rfid:
                rfid_input = st.text_input(
                    "RFID do Animal (ou deixe vazio para lote - não implementado lote)",
                    value=st.session_state.scanned_rfid_coleta
                )
                if rfid_input != st.session_state.scanned_rfid_coleta:
                    st.session_state.scanned_rfid_coleta = rfid_input

            with col_btn:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                if st.button("📷", key="btn_scan_coleta", help="Ler QR Code ou Código de Barras", use_container_width=True):
                    st.session_state.show_camera_coleta = not st.session_state.show_camera_coleta
                    st.rerun()

        event_type = st.selectbox(
            "Tipo de Evento",
            ["Pesagem", "Vacinação", "Vermifugação", "Desmama"]
        )
        
        val = 0.0
        if event_type == "Pesagem":
            val = st.number_input("Novo Peso (kg)", min_value=0.0)
        
        details = st.text_input("Detalhes (ex: nome da vacina)")
        
        if st.button("Registrar Evento"):
            if not rfid_input:
                st.error("Por favor, insira um RFID.")
            else:
                animal = db.query(Animal).filter(Animal.rfid == rfid_input).first()
                if animal:
                    try:
                        new_event = Event(
                            animal_id=animal.id,
                            date=datetime.date.today(),
                            event_type=event_type,
                            value=val if event_type == "Pesagem" else 0,
                            details=details
                        )
                        
                        if event_type == "Pesagem":
                            animal.current_weight = val
                            
                        db.add(new_event)
                        db.commit()
                        st.session_state.scanned_rfid_coleta = ""
                        st.success(f"Evento registrado para o animal {rfid_input}!")
                    except Exception as e:
                        st.error(f"Erro: {e}")
                else:
                    st.error("Animal não encontrado.")
