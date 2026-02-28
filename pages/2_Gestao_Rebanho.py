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

tab1, tab2, tab3 = st.tabs(["Cadastro Animal", "Rebanho Atual", "Importar Dados"])

with get_db_session() as db:
    # --- Tab 1: Cadastro Animal ---
    with tab1:
        st.header("Novo Animal")
        
        # Session state para o RFID escaneado e controle da câmera
        if 'scanned_rfid' not in st.session_state:
            st.session_state.scanned_rfid = ""
        if 'show_camera' not in st.session_state:
            st.session_state.show_camera = False
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
                st.info("Aponte o QR Code para a câmera.")
                img_file_buffer = st.camera_input("Scanner")
                if img_file_buffer is not None:
                    try:
                        import cv2
                        import numpy as np
                        import zxingcpp
                        
                        file_bytes = np.asarray(bytearray(img_file_buffer.read()), dtype=np.uint8)
                        image = cv2.imdecode(file_bytes, 1)
                        
                        # DEBUG: Salvar localmente a foto para verificar o que o Streamlit enxerga
                        cv2.imwrite("debug_camera.png", image)
                        st.info("ℹ️ Debug: Foto da câmera foi salva em 'debug_camera.png'.")
                        
                        # 1. Tenta a imagem original
                        resultados = zxingcpp.read_barcodes(image)
                        
                        # 2. Tenta em escala de cinza + Equalização de Histograma (CLAHE para lidar com sombra/luz ruim)
                        if not resultados:
                            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                            gray_clahe = clahe.apply(gray)
                            resultados = zxingcpp.read_barcodes(gray_clahe)

                        # 3. Tenta thresholding automático para códigos desbotados
                        if not resultados:
                            _, thresh = cv2.threshold(gray_clahe, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
                            resultados = zxingcpp.read_barcodes(thresh)

                        # 4. Tenta aumentar a imagem (útil se o celular mandar uma foto de resolução baixa no Streamlit)
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
                
                if st.button("Cancelar Leitura"):
                    st.session_state.show_camera = False
                    st.rerun()

            col1, col2 = st.columns(2)
            with col1:
                # Coluna para os inputs com botão lado-a-lado
                col_rfid, col_btn = st.columns([5, 1])
                with col_rfid:
                    rfid = st.text_input("RFID/Brinco Eletrônico", value=st.session_state.scanned_rfid)
                    # Atualiza o state caso o usuário digite algo manualmente
                    if rfid != st.session_state.scanned_rfid:
                        st.session_state.scanned_rfid = rfid
                with col_btn:
                    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                    if st.button("📷", help="Ler QR Code ou Código de Barras", use_container_width=True):
                        st.session_state.show_camera = not st.session_state.show_camera
                        st.rerun()

                breed = st.selectbox("Raça", ["Nelore", "Angus", "Brahman", "Hereford", "Cruzado"])
                birth_date = st.date_input("Data de Nascimento", datetime.date.today())
            with col2:
                # Coluna para os inputs com botão lado-a-lado
                col_weight, col_w_btn = st.columns([5, 1])
                with col_weight:
                    initial_weight = st.number_input("Peso Inicial (kg)", min_value=0.0, step=0.1, value=float(st.session_state.scanned_weight))
                    if initial_weight != st.session_state.scanned_weight:
                        st.session_state.scanned_weight = initial_weight
                with col_w_btn:
                    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                    if st.button("📷", key="btn_camera_peso", help="Ler Peso pela Câmera", use_container_width=True):
                        st.session_state.show_weight_camera = not st.session_state.show_weight_camera
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
                            status=status
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
                data.append({
                    "ID": a.id,
                    "RFID": a.rfid,
                    "Raça": a.breed,
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

    # --- Tab 3: Importar Dados ---
    with tab3:
        st.header("Importação de Dispositivos (RFID/Balança)")
        st.markdown("Carregue arquivos `.csv` gerados por bastões ou balanças eletrônicas.")
        
        uploaded_file = st.file_uploader("Escolha um arquivo CSV", type="csv")
        
        if uploaded_file is not None:
            try:
                df_import = pd.read_csv(uploaded_file)
                st.write("Pré-visualização dos dados:")
                st.dataframe(df_import.head())
                
                if st.button("Processar Importação"):
                    st.metric(
                        "Simulação: Dados importados com sucesso!",
                        "(Lógica a implementar)"
                    )
                    # Here we would implement logic to match RFID and update weights
            except Exception as e:
                st.error(f"Erro ao ler arquivo: {e}")
