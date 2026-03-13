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

        st.info("Registre eventos para animais individualmente via RFID ou QR Code da etiqueta.")

        # --- Session state ---
        if 'scanned_rfid_coleta' not in st.session_state:
            st.session_state.scanned_rfid_coleta = ""
        if 'show_camera_coleta' not in st.session_state:
            st.session_state.show_camera_coleta = False
        if 'show_ocr_camera_coleta' not in st.session_state:
            st.session_state.show_ocr_camera_coleta = False
        if 'animal_coleta' not in st.session_state:
            st.session_state.animal_coleta = None  # armazena o objeto Animal encontrado

        # --- Scanner de QR Code ---
        container_coleta = st.container()
        with container_coleta:
            if st.session_state.show_camera_coleta:
                st.info("📷 Aponte o **QR Code / Código de Barras** da etiqueta para a câmera.")
                img_file_buffer = st.camera_input("Scanner Manejo")
                if img_file_buffer is not None:
                    try:
                        import cv2
                        import numpy as np
                        import zxingcpp

                        file_bytes = np.asarray(bytearray(img_file_buffer.read()), dtype=np.uint8)
                        image = cv2.imdecode(file_bytes, 1)

                        resultados = zxingcpp.read_barcodes(image)

                        if not resultados:
                            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                            gray_clahe = clahe.apply(gray)
                            resultados = zxingcpp.read_barcodes(gray_clahe)

                        if not resultados:
                            _, thresh = cv2.threshold(gray_clahe, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
                            resultados = zxingcpp.read_barcodes(thresh)

                        if not resultados:
                            resized = cv2.resize(gray_clahe, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
                            resultados = zxingcpp.read_barcodes(resized)

                        data = resultados[0].text if resultados else None

                        if data:
                            # Salva o RFID e busca o animal imediatamente
                            st.session_state.scanned_rfid_coleta = data
                            animal_encontrado = db.query(Animal).filter(Animal.rfid == data).first()
                            st.session_state.animal_coleta = {
                                "id": animal_encontrado.id,
                                "rfid": animal_encontrado.rfid,
                                "breed": animal_encontrado.breed,
                                "birth_date": str(animal_encontrado.birth_date),
                                "current_weight": animal_encontrado.current_weight,
                                "initial_weight": animal_encontrado.initial_weight,
                                "status": animal_encontrado.status,
                                "paddock": animal_encontrado.paddock.name if animal_encontrado.paddock else "N/A",
                            } if animal_encontrado else None
                            st.session_state.show_camera_coleta = False
                            st.rerun()
                        else:
                            st.warning("Nenhum código detectado. Tente aproximar ou melhorar a iluminação.")
                    except Exception as e:
                        st.error(f"Erro ao processar imagem: {e}")

                if st.button("Cancelar Leitura QR", key="cancel_scan_coleta"):
                    st.session_state.show_camera_coleta = False
                    st.rerun()

            # --- Scanner OCR: número impresso na etiqueta ---
            if st.session_state.show_ocr_camera_coleta:
                st.info("🔢 Aponte a câmera para o **número impresso** na etiqueta/brinco.")
                img_file_buffer_ocr = st.camera_input("Scanner Número Etiqueta Manejo")
                if img_file_buffer_ocr is not None:
                    try:
                        import cv2
                        import numpy as np
                        import easyocr

                        file_bytes_ocr = np.asarray(bytearray(img_file_buffer_ocr.read()), dtype=np.uint8)
                        image_ocr = cv2.imdecode(file_bytes_ocr, 1)

                        # Pré-processamento para melhorar leitura de números em etiquetas
                        gray_ocr = cv2.cvtColor(image_ocr, cv2.COLOR_BGR2GRAY)
                        clahe_ocr = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                        gray_ocr = clahe_ocr.apply(gray_ocr)
                        gray_ocr = cv2.resize(gray_ocr, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

                        reader_rfid = easyocr.Reader(['en'], gpu=False)
                        resultado_ocr = reader_rfid.readtext(
                            gray_ocr,
                            allowlist="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-",
                            detail=0,
                            paragraph=False
                        )

                        if resultado_ocr:
                            numero_etiqueta = "".join(resultado_ocr).strip().replace(" ", "")
                            if numero_etiqueta:
                                # Busca o animal com o número lido
                                animal_encontrado = db.query(Animal).filter(Animal.rfid == numero_etiqueta).first()
                                st.session_state.scanned_rfid_coleta = numero_etiqueta
                                st.session_state.animal_coleta = {
                                    "id": animal_encontrado.id,
                                    "rfid": animal_encontrado.rfid,
                                    "breed": animal_encontrado.breed,
                                    "birth_date": str(animal_encontrado.birth_date),
                                    "current_weight": animal_encontrado.current_weight,
                                    "initial_weight": animal_encontrado.initial_weight,
                                    "status": animal_encontrado.status,
                                    "paddock": animal_encontrado.paddock.name if animal_encontrado.paddock else "N/A",
                                } if animal_encontrado else None
                                st.session_state.show_ocr_camera_coleta = False
                                st.rerun()
                            else:
                                st.warning("Número não detectado. Aproxime mais a câmera do número na etiqueta.")
                        else:
                            st.warning("Nenhum número detectado. Tente com melhor iluminação e foco no número.")

                    except Exception as e:
                        st.error(f"Erro ao ler número da etiqueta: {e}")

                if st.button("Cancelar Leitura Número", key="cancel_ocr_coleta"):
                    st.session_state.show_ocr_camera_coleta = False
                    st.rerun()

            # --- Campo RFID + Botões câmera ---
            col_rfid, col_btn_qr, col_btn_ocr = st.columns([5, 1, 1])
            with col_rfid:
                rfid_input = st.text_input(
                    "RFID do Animal",
                    value=st.session_state.scanned_rfid_coleta,
                    placeholder="Digite, leia QR Code (📷) ou número (🔢)"
                )
                # Se o usuário digitou manualmente, atualiza o state e busca o animal
                if rfid_input != st.session_state.scanned_rfid_coleta:
                    st.session_state.scanned_rfid_coleta = rfid_input
                    if rfid_input:
                        animal_manual = db.query(Animal).filter(Animal.rfid == rfid_input).first()
                        st.session_state.animal_coleta = {
                            "id": animal_manual.id,
                            "rfid": animal_manual.rfid,
                            "breed": animal_manual.breed,
                            "birth_date": str(animal_manual.birth_date),
                            "current_weight": animal_manual.current_weight,
                            "initial_weight": animal_manual.initial_weight,
                            "status": animal_manual.status,
                            "paddock": animal_manual.paddock.name if animal_manual.paddock else "N/A",
                        } if animal_manual else None
                    else:
                        st.session_state.animal_coleta = None

            with col_btn_qr:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                if st.button("📷", key="btn_scan_coleta", help="Ler QR Code ou Código de Barras", use_container_width=True):
                    st.session_state.show_camera_coleta = not st.session_state.show_camera_coleta
                    st.session_state.show_ocr_camera_coleta = False  # Fecha o outro modo
                    st.rerun()
            with col_btn_ocr:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                if st.button("🔢", key="btn_ocr_coleta", help="Ler Número Impresso na Etiqueta", use_container_width=True):
                    st.session_state.show_ocr_camera_coleta = not st.session_state.show_ocr_camera_coleta
                    st.session_state.show_camera_coleta = False  # Fecha o outro modo
                    st.rerun()

        # --- Card do animal encontrado ---
        animal_data = st.session_state.animal_coleta

        if rfid_input and animal_data:
            status_emoji = {"active": "🟢", "quarantine": "🟡", "sick": "🔴"}.get(animal_data["status"], "⚪")
            st.success(f"✅ Animal encontrado — RFID: **{animal_data['rfid']}**")
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("🐄 Raça", animal_data["breed"])
                c2.metric("⚖️ Peso Atual", f"{animal_data['current_weight']:.1f} kg")
                c3.metric("🌿 Piquete", animal_data["paddock"])
                c4.metric("📋 Status", f"{status_emoji} {animal_data['status'].capitalize()}")
                st.caption(f"🎂 Nascimento: {animal_data['birth_date']}  |  ⚖️ Peso inicial: {animal_data['initial_weight']:.1f} kg  |  🔑 ID interno: #{animal_data['id']}")
        elif rfid_input and animal_data is None:
            st.error(f"❌ Animal com RFID **{rfid_input}** não encontrado no rebanho. Verifique o cadastro.")

        st.divider()

        # --- Formulário de evento ---
        event_type = st.selectbox(
            "Tipo de Evento",
            ["Pesagem", "Vacinação", "Vermifugação", "Desmama"]
        )

        val = 0.0
        if event_type == "Pesagem":
            # Pré-preenche com o peso atual do animal se disponível
            peso_default = float(animal_data["current_weight"]) if animal_data else 0.0
            val = st.number_input("Novo Peso (kg)", min_value=0.0, value=peso_default)

        details = st.text_input("Detalhes (ex: nome da vacina)")

        if st.button("Registrar Evento", type="primary"):
            if not rfid_input:
                st.error("Por favor, insira ou escaneie um RFID.")
            elif not animal_data:
                st.error("Animal não encontrado. Verifique o RFID.")
            else:
                animal_obj = db.query(Animal).filter(Animal.rfid == rfid_input).first()
                if animal_obj:
                    try:
                        new_event = Event(
                            animal_id=animal_obj.id,
                            date=datetime.date.today(),
                            event_type=event_type,
                            value=val if event_type == "Pesagem" else 0,
                            details=details
                        )

                        if event_type == "Pesagem":
                            animal_obj.current_weight = val

                        db.add(new_event)
                        db.commit()
                        st.session_state.scanned_rfid_coleta = ""
                        st.session_state.animal_coleta = None
                        st.success(f"✅ Evento **{event_type}** registrado para o animal **{rfid_input}**!")
                    except Exception as e:
                        st.error(f"Erro: {e}")
                else:
                    st.error("Animal não encontrado.")
