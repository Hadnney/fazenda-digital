import os
import sys
import datetime
import streamlit as st
import pandas as pd

# Adiciona o diretório raiz ao path para as importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_session
from models import Inventory
from auth import check_auth

st.set_page_config(page_title="Estoque", page_icon="📦", layout="wide")

# Verifica se o usuário está autenticado
check_auth()

st.title("📦 Gestão de Estoque Global")

with get_db_session() as db:
    tab1, tab2, tab3 = st.tabs(["Visão Geral", "Movimentação (Entrada/Saída)", "Cadastrar Novo Produto"])

    # --- Tab 1: Visão Geral ---
    with tab1:
        st.header("Inventário Atual")
        items = db.query(Inventory).all()
        
        if items:
            data = []
            total_value = 0.0
            
            for item in items:
                value = (item.quantity or 0) * (item.cost_per_unit or 0)
                total_value += value
                data.append({
                    "ID": item.id,
                    "Produto": item.item_name,
                    "Categoria": item.category,
                    "Quantidade": item.quantity,
                    "Unidade": item.unit,
                    "Custo Unitário (R$)": item.cost_per_unit,
                    "Valor Total (R$)": round(value, 2),
                    "Vencimento": item.expiry_date if item.expiry_date else "N/A"
                })
            
            df = pd.DataFrame(data)
            
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric("Total de Produtos Únicos", len(items))
            with col_m2:
                # Format currency dynamically
                val_str = f"R$ {total_value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                st.metric("Valor Total em Estoque", val_str)
            with col_m3:
                low_stock = sum(1 for i in items if i.quantity <= 0)
                st.metric("Itens Sem Estoque", low_stock, delta_color="inverse")
                
            st.dataframe(df, use_container_width=True, hide_index=True)
            
        else:
            st.warning("Nenhum produto cadastrado no estoque ainda.")

    # --- Tab 2: Movimentação (Entrada/Saída) ---
    with tab2:
        st.header("Atualizar Quantidade")
        items = db.query(Inventory).all()
        
        if items:
            item_map = {f"{i.item_name} (Atual: {i.quantity} {i.unit})": i.id for i in items}
            selected_item_label = st.selectbox("Selecione o Produto", list(item_map.keys()))
            
            col_op_1, col_op_2 = st.columns(2)
            with col_op_1:
                operation = st.radio("Operação", ["Entrada (+)", "Saída (-)"])
            with col_op_2:
                qty_change = st.number_input("Quantidade", min_value=0.01, step=1.0)
            
            if st.button("Registrar Movimentação", type="primary"):
                item_id = item_map[selected_item_label]
                item_to_update = db.query(Inventory).filter(Inventory.id == item_id).first()
                
                if item_to_update:
                    if operation == "Entrada (+)":
                        item_to_update.quantity += qty_change
                        db.commit()
                        st.success(f"Adicionado {qty_change} {item_to_update.unit} de {item_to_update.item_name}.")
                    else:
                        if item_to_update.quantity >= qty_change:
                            item_to_update.quantity -= qty_change
                            db.commit()
                            st.success(f"Retirado {qty_change} {item_to_update.unit} de {item_to_update.item_name}.")
                        else:
                            st.error(f"Estoque insuficiente! Você tentou retirar {qty_change}, mas só há {item_to_update.quantity} disponíveis.")
                    
                    st.rerun()
        else:
            st.info("Cadastre um novo produto primeiro na aba ao lado.")

    # --- Tab 3: Cadastro de Produto ---
    with tab3:
        st.header("Cadastrar Novo Produto")
        with st.form("new_inventory_item"):
            col_form_1, col_form_2 = st.columns(2)
            with col_form_1:
                item_name = st.text_input("Nome do Produto")
                category = st.selectbox("Categoria", ["Nutrição", "Medicamento", "Material Geral", "Ferramentas", "Outros"])
                unit = st.selectbox("Unidade de Medida", ["kg", "Litros", "Sacos", "Frascos", "Doses", "Unidade", "Caixas"])
            
            with col_form_2:
                initial_quantity = st.number_input("Quantidade Inicial", min_value=0.0, step=1.0)
                cost = st.number_input("Custo Unitário (R$)", min_value=0.0, step=0.1)
                
                st.markdown("<br>", unsafe_allow_html=True)
                has_expiry = st.checkbox("Produto Perecível / Possui Validade?", value=False)
                expiry = st.date_input("Data de Validade", datetime.date.today(), disabled=not has_expiry)
            
            submitted_item = st.form_submit_button("Cadastrar Produto", type="primary")
            
            if submitted_item:
                if not item_name:
                    st.error("O nome do produto é obrigatório!")
                else:
                    exp_val = expiry if has_expiry else None
                    new_item = Inventory(
                        item_name=item_name,
                        category=category,
                        quantity=initial_quantity,
                        unit=unit,
                        cost_per_unit=cost,
                        expiry_date=exp_val
                    )
                    db.add(new_item)
                    db.commit()
                    st.success(f"Produto '{item_name}' cadastrado com sucesso!")
