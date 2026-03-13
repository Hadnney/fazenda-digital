import os
import sys
import datetime
import streamlit as st
import pandas as pd

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_session
from models import Animal, Paddock, Event
from auth import check_auth

st.set_page_config(page_title="Gestão de Rebanho", page_icon="🐮", layout="wide")

# Verifica se o usuário está autenticado
check_auth()

st.title("🐮 Gestão de Ciclo de Vida e Logística")

tab1, tab2, tab3, tab4 = st.tabs(["Cadastro Animal", "Rebanho Atual", "Importar Dados", "📄 Documentos de Transporte"])

with get_db_session() as db:
    # --- Tab 1: Cadastro Animal ---
    with tab1:
        st.header("Novo Animal")
        
        # Session state para o RFID escaneado e controle da câmera
        if 'scanned_rfid' not in st.session_state:
            st.session_state.scanned_rfid = ""
        if 'show_camera' not in st.session_state:
            st.session_state.show_camera = False
        if 'show_ocr_camera' not in st.session_state:
            st.session_state.show_ocr_camera = False
        if 'scanned_weight' not in st.session_state:
            st.session_state.scanned_weight = 0.0
        if 'show_weight_camera' not in st.session_state:
            st.session_state.show_weight_camera = False

        container = st.container()
        with container:
            if st.session_state.show_weight_camera:
                st.info("Aponte a câmera para o visor da balança para ler o peso.")
                img_file_buffer_w = st.camera_input("Scanner de Peso")
                if img_file_buffer_w is not None:
                    try:
                        import cv2
                        import numpy as np
                        import easyocr
                        import re
                        
                        # Usa EasyOCR apenas para os números da balança (mais resiliente com LEDs digitais)
                        reader = easyocr.Reader(['en'], gpu=False)
                        
                        # Extrai a imagem do buffer do Streamlit
                        file_bytes_w = np.asarray(bytearray(img_file_buffer_w.read()), dtype=np.uint8)
                        image = cv2.imdecode(file_bytes_w, 1)

                        # O EasyOCR lida muito bem com as telinhas sem precisar distorcer a imagem toda com cv2
                        result = reader.readtext(image, allowlist="0123456789.,", detail=0)
                        
                        if result:
                            # EasyOCR retorna uma lista de strings encontradas
                            text = " ".join(result)
                            
                            # Encontrar o primeiro número válido com possível casa decimal
                            numbers = re.findall(r'\d+[.,]?\d*', text)
                            
                            if numbers:
                                # Tratar vírgula e ponto para float Python
                                weight_value = float(numbers[0].replace(',', '.'))
                                st.session_state.scanned_weight = weight_value
                                st.session_state.show_weight_camera = False
                                st.rerun()
                            else:
                                st.warning("Números não detectados na foto clara. Tente focar melhor no visor.")
                        else:
                            st.warning("Nenhum texto/peso detectado. Tente focar no visor da balança.")
                            
                    except Exception as e:
                        st.error(f"Erro ao processar imagem para peso com EasyOCR: {e}")
                
                if st.button("Cancelar Leitura de Peso"):
                    st.session_state.show_weight_camera = False
                    st.rerun()

            if st.session_state.show_camera:
                st.info("📷 Aponte o **QR Code / Código de Barras** da etiqueta para a câmera.")
                img_file_buffer = st.camera_input("Scanner QR/Barras")
                if img_file_buffer is not None:
                    try:
                        import cv2
                        import numpy as np
                        import zxingcpp
                        
                        file_bytes = np.asarray(bytearray(img_file_buffer.read()), dtype=np.uint8)
                        image = cv2.imdecode(file_bytes, 1)
                        
                        # 1. Tenta a imagem original
                        resultados = zxingcpp.read_barcodes(image)
                        
                        # 2. Tenta em escala de cinza + Equalização de Histograma (CLAHE)
                        if not resultados:
                            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                            gray_clahe = clahe.apply(gray)
                            resultados = zxingcpp.read_barcodes(gray_clahe)

                        # 3. Tenta thresholding automático para códigos desbotados
                        if not resultados:
                            _, thresh = cv2.threshold(gray_clahe, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
                            resultados = zxingcpp.read_barcodes(thresh)

                        # 4. Tenta aumentar a imagem (útil se o celular mandar foto de baixa resolução)
                        if not resultados:
                            resized = cv2.resize(gray_clahe, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
                            resultados = zxingcpp.read_barcodes(resized)
                        
                        data = resultados[0].text if resultados else None
                        
                        if data:
                            st.session_state.scanned_rfid = data
                            st.session_state.show_camera = False
                            st.rerun()
                        else:
                            st.warning("Nenhum código detectado. Tente aproximar ou melhorar a iluminação.")
                    except Exception as e:
                        st.error(f"Erro ao processar imagem: {e}")
                
                if st.button("Cancelar Leitura QR"):
                    st.session_state.show_camera = False
                    st.rerun()

            if st.session_state.show_ocr_camera:
                st.info("🔢 Aponte a câmera para o **número impresso** na etiqueta/brinco.")
                img_file_buffer_ocr = st.camera_input("Scanner Número Etiqueta")
                if img_file_buffer_ocr is not None:
                    try:
                        import cv2
                        import numpy as np
                        import easyocr
                        import re
                        
                        file_bytes_ocr = np.asarray(bytearray(img_file_buffer_ocr.read()), dtype=np.uint8)
                        image_ocr = cv2.imdecode(file_bytes_ocr, 1)

                        # Pré-processamento para melhorar leitura de números em etiquetas
                        gray_ocr = cv2.cvtColor(image_ocr, cv2.COLOR_BGR2GRAY)
                        # Aumento de contraste
                        clahe_ocr = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                        gray_ocr = clahe_ocr.apply(gray_ocr)
                        # Upscale para facilitar o OCR
                        gray_ocr = cv2.resize(gray_ocr, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

                        # Usa EasyOCR para ler o número da etiqueta
                        reader_rfid = easyocr.Reader(['en'], gpu=False)
                        resultado_ocr = reader_rfid.readtext(
                            gray_ocr,
                            allowlist="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-",
                            detail=0,
                            paragraph=False
                        )
                        
                        if resultado_ocr:
                            # Concatena os fragmentos e limpa espaços extras
                            numero_etiqueta = "".join(resultado_ocr).strip().replace(" ", "")
                            if numero_etiqueta:
                                st.session_state.scanned_rfid = numero_etiqueta
                                st.session_state.show_ocr_camera = False
                                st.rerun()
                            else:
                                st.warning("Número não detectado. Aproxime mais a câmera do número na etiqueta.")
                        else:
                            st.warning("Nenhum número detectado. Tente com melhor iluminação e foco no número.")
                            
                    except Exception as e:
                        st.error(f"Erro ao ler número da etiqueta: {e}")
                
                if st.button("Cancelar Leitura Número"):
                    st.session_state.show_ocr_camera = False
                    st.rerun()

            col1, col2 = st.columns(2)
            with col1:
                # Coluna para os inputs com botão lado-a-lado
                col_rfid, col_btn_qr, col_btn_ocr = st.columns([5, 1, 1])
                with col_rfid:
                    rfid = st.text_input("RFID/Brinco Eletrônico", value=st.session_state.scanned_rfid,
                                        placeholder="Digite, leia QR Code (📷) ou número (🔢)")
                    # Atualiza o state caso o usuário digite algo manualmente
                    if rfid != st.session_state.scanned_rfid:
                        st.session_state.scanned_rfid = rfid
                with col_btn_qr:
                    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                    if st.button("📷", key="btn_qr_rfid", help="Ler QR Code ou Código de Barras", use_container_width=True):
                        st.session_state.show_camera = not st.session_state.show_camera
                        st.session_state.show_ocr_camera = False  # Fecha o outro modo
                        st.rerun()
                with col_btn_ocr:
                    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                    if st.button("🔢", key="btn_ocr_rfid", help="Ler Número Impresso na Etiqueta", use_container_width=True):
                        st.session_state.show_ocr_camera = not st.session_state.show_ocr_camera
                        st.session_state.show_camera = False  # Fecha o outro modo
                        st.rerun()

                breed = st.selectbox("Raça", ["Nelore", "Angus", "Brahman", "Hereford", "Cruzado"])
                fase_inicial = st.selectbox(
                    "Fase Inicial",
                    ["cria", "recria", "engorda"],
                    format_func=lambda f: {"cria": "🐮 Cria", "recria": "🌱 Recria", "engorda": "🍽️ Engorda"}[f]
                )
                birth_date = st.date_input("Data de Nascimento", datetime.date.today())
            with col2:
                # Coluna para os inputs com botão lado-a-lado
                col_weight, col_w_btn, col_w_clear = st.columns([5, 1, 1])
                with col_weight:
                    initial_weight = st.number_input("Peso Inicial (kg)", min_value=0.0, step=0.1, value=float(st.session_state.scanned_weight))
                    if initial_weight != st.session_state.scanned_weight:
                        st.session_state.scanned_weight = initial_weight
                with col_w_btn:
                    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                    if st.button("📷", key="btn_camera_peso", help="Ler Peso pela Câmera", use_container_width=True):
                        st.session_state.show_weight_camera = not st.session_state.show_weight_camera
                        st.rerun()
                with col_w_clear:
                    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                    if st.button("❌", key="btn_clear_peso", help="Limpar Peso", use_container_width=True):
                        st.session_state.scanned_weight = 0.0
                        st.rerun()
                paddock_options = db.query(Paddock).all()
                paddock_map = {p.name: p.id for p in paddock_options}
                if paddock_map:
                    selected_paddock = st.selectbox("Piquete Inicial", list(paddock_map.keys()))
                else:
                    st.warning("Nenhum piquete cadastrado.")
                    selected_paddock = None
                status = st.selectbox("Status", ["active", "quarantine", "sick"])

            submitted = st.button("Cadastrar Animal", type="primary")
            
            if submitted:
                if not rfid:
                    st.error("O campo RFID/Brinco Eletrônico é obrigatório.")
                elif not selected_paddock:
                    st.error("É necessário selecionar um piquete.")
                else:
                    try:
                        new_animal = Animal(
                            rfid=rfid,
                            breed=breed,
                            birth_date=birth_date,
                            initial_weight=initial_weight,
                            current_weight=initial_weight,
                            paddock_id=paddock_map[selected_paddock],
                            status=status,
                            fase=fase_inicial,
                            data_fase=datetime.date.today(),
                            peso_entrada_fase=initial_weight,
                        )
                        db.add(new_animal)
                        
                        # Log birth/entry event automatically
                        new_event = Event(
                            animal=new_animal,
                            event_type="birth_entry",
                            value=initial_weight,
                            details=f"Entrada no {selected_paddock}"
                        )
                        db.add(new_event)
                        
                        db.commit()
                        st.session_state.scanned_rfid = ""
                        st.session_state.scanned_weight = 0.0
                        st.success(f"Animal {rfid} cadastrado com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao cadastrar: {e}")

    # --- Tab 2: Rebanho Atual ---
    with tab2:
        st.header("Visão Geral do Rebanho")
        
        animals = db.query(Animal).all()
        
        if animals:
            data = []
            for a in animals:
                paddock_name = a.paddock.name if a.paddock else "N/A"
                fase_labels = {
                    "cria": "🐮 Cria", "recria": "🌱 Recria",
                    "engorda": "🍽️ Engorda", "venda": "💰 Venda"
                }
                data.append({
                    "ID": a.id,
                    "RFID": a.rfid,
                    "Raça": a.breed,
                    "Fase": fase_labels.get(a.fase or "cria", a.fase or "cria"),
                    "Peso (kg)": a.current_weight,
                    "Piquete": paddock_name,
                    "Status": a.status,
                    "Nascimento": a.birth_date
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df)
            
            # Simple stats
            st.info(f"Total de Animais: {len(animals)}")
            st.info(f"Peso Médio: {df['Peso (kg)'].mean():.2f} kg")
            
        else:
            st.warning("Nenhum animal cadastrado.")

    # --- Tab 4: Documentos de Transporte ---
    with tab4:
        st.header("📄 Documentos de Transporte Animal")
        st.markdown(
            "Registre e arquive as fotos dos documentos obrigatórios para "
            "movimentação de animais. Cada documento fica vinculado ao RFID do animal."
        )

        # --- Session state dos documentos ---
        if 'doc_rfid' not in st.session_state:
            st.session_state.doc_rfid = ""
        if 'foto_gta' not in st.session_state:
            st.session_state.foto_gta = None
        if 'foto_caminhao' not in st.session_state:
            st.session_state.foto_caminhao = None

        # --- Seleção do animal ---
        st.subheader("Animal / RFID")
        animais_lista = db.query(Animal).all()
        rfid_opcoes = {f"{a.rfid} — {a.breed} ({a.status})": a.rfid for a in animais_lista} if animais_lista else {}

        col_sel, col_dig = st.columns([3, 2])
        with col_sel:
            if rfid_opcoes:
                sel = st.selectbox(
                    "Selecionar animal cadastrado",
                    ["— selecione —"] + list(rfid_opcoes.keys())
                )
                if sel != "— selecione —":
                    st.session_state.doc_rfid = rfid_opcoes[sel]
            else:
                st.warning("Nenhum animal cadastrado ainda.")
        with col_dig:
            rfid_doc = st.text_input(
                "Ou digite o RFID manualmente",
                value=st.session_state.doc_rfid,
                placeholder="Ex: BR-001"
            )
            if rfid_doc != st.session_state.doc_rfid:
                st.session_state.doc_rfid = rfid_doc

        rfid_doc = st.session_state.doc_rfid

        st.divider()

        # --- Campos de foto ---
        col_gta, col_cam = st.columns(2)

        # ── Campo 1: GTA – Guia de Trânsito Animal ──
        with col_gta:
            st.subheader("🐄 GTA — Guia de Trânsito Animal")
            st.caption(
                "Fotografia do documento GTA emitido pelo órgão estadual de "
                "defesa agropecuária. Obrigatório para todo transporte de bovinos."
            )

            metodo_gta = st.radio(
                "Como deseja capturar?",
                ["📷 Câmera", "📁 Upload de arquivo"],
                key="metodo_gta",
                horizontal=True
            )

            foto_gta_bytes = None

            if metodo_gta == "📷 Câmera":
                img_gta = st.camera_input("Fotografar GTA", key="cam_gta")
                if img_gta is not None:
                    foto_gta_bytes = img_gta.getvalue()
                    st.session_state.foto_gta = foto_gta_bytes
            else:
                upload_gta = st.file_uploader(
                    "Selecionar foto da GTA",
                    type=["jpg", "jpeg", "png", "pdf"],
                    key="upload_gta"
                )
                if upload_gta is not None:
                    foto_gta_bytes = upload_gta.getvalue()
                    st.session_state.foto_gta = foto_gta_bytes

            # Preview e download
            if st.session_state.foto_gta:
                st.image(
                    st.session_state.foto_gta,
                    caption="✅ GTA capturada",
                    use_container_width=True
                )
                st.download_button(
                    "⬇️ Baixar foto da GTA",
                    data=st.session_state.foto_gta,
                    file_name=f"GTA_{rfid_doc or 'sem_rfid'}_{datetime.date.today()}.jpg",
                    mime="image/jpeg",
                    key="dl_gta"
                )
            else:
                st.info("Nenhuma foto da GTA capturada ainda.")

        # ── Campo 2: Guia do Caminhão de Transporte ──
        with col_cam:
            st.subheader("🚛 Guia do Caminhão de Transporte")
            st.caption(
                "Fotografia do documento de habilitação/registro do veículo "
                "transportador. Inclua também o CIOT quando aplicável."
            )

            metodo_cam = st.radio(
                "Como deseja capturar?",
                ["📷 Câmera", "📁 Upload de arquivo"],
                key="metodo_cam",
                horizontal=True
            )

            foto_cam_bytes = None

            if metodo_cam == "📷 Câmera":
                img_cam = st.camera_input("Fotografar Guia do Caminhão", key="cam_caminhao")
                if img_cam is not None:
                    foto_cam_bytes = img_cam.getvalue()
                    st.session_state.foto_caminhao = foto_cam_bytes
            else:
                upload_cam = st.file_uploader(
                    "Selecionar foto do Guia do Caminhão",
                    type=["jpg", "jpeg", "png", "pdf"],
                    key="upload_cam"
                )
                if upload_cam is not None:
                    foto_cam_bytes = upload_cam.getvalue()
                    st.session_state.foto_caminhao = foto_cam_bytes

            # Preview e download
            if st.session_state.foto_caminhao:
                st.image(
                    st.session_state.foto_caminhao,
                    caption="✅ Guia do Caminhão capturado",
                    use_container_width=True
                )
                st.download_button(
                    "⬇️ Baixar foto do Guia do Caminhão",
                    data=st.session_state.foto_caminhao,
                    file_name=f"GuiaCaminhao_{rfid_doc or 'sem_rfid'}_{datetime.date.today()}.jpg",
                    mime="image/jpeg",
                    key="dl_cam"
                )
            else:
                st.info("Nenhuma foto do Guia do Caminhão capturada ainda.")

        st.divider()

        # --- Salvar documentos em disco ---
        if st.button("💾 Salvar Documentos", type="primary", key="btn_salvar_docs"):
            if not rfid_doc:
                st.error("Informe o RFID do animal antes de salvar.")
            elif not st.session_state.foto_gta and not st.session_state.foto_caminhao:
                st.warning("Capture ao menos uma foto antes de salvar.")
            else:
                try:
                    pasta = os.path.join(
                        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "doc_transporte"
                    )
                    os.makedirs(pasta, exist_ok=True)

                    salvos = []
                    if st.session_state.foto_gta:
                        nome_gta = f"GTA_{rfid_doc}_{datetime.date.today()}.jpg"
                        with open(os.path.join(pasta, nome_gta), "wb") as f:
                            f.write(st.session_state.foto_gta)
                        salvos.append(f"GTA → `{nome_gta}`")

                    if st.session_state.foto_caminhao:
                        nome_cam = f"GuiaCaminhao_{rfid_doc}_{datetime.date.today()}.jpg"
                        with open(os.path.join(pasta, nome_cam), "wb") as f:
                            f.write(st.session_state.foto_caminhao)
                        salvos.append(f"Guia do Caminhão → `{nome_cam}`")

                    st.success(
                        f"✅ Documentos salvos com sucesso na pasta `doc_transporte/`:\n\n"
                        + "\n".join(f"- {s}" for s in salvos)
                    )
                    # Limpa o estado após salvar
                    st.session_state.foto_gta = None
                    st.session_state.foto_caminhao = None
                    st.session_state.doc_rfid = ""

                except Exception as e:
                    st.error(f"Erro ao salvar documentos: {e}")

