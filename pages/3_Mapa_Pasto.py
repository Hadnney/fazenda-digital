import os
import sys
import streamlit as st
import folium
from streamlit_folium import st_folium

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_session
from models import Paddock
from auth import check_auth

# Verifica se o usuário está autenticado
check_auth()

st.set_page_config(page_title="Mapa da Fazenda", page_icon="🗺️", layout="wide")

st.title("🗺️ Mapa Visual da Fazenda")

with get_db_session() as db:
    paddocks = db.query(Paddock).all()

    # Center map on a default location (mock coords for Brazil farm)
    m = folium.Map(location=[-15.793889, -47.882778], zoom_start=15)

    # Add paddocks to map
    for p in paddocks:
        # Simulating coordinates if not present or parsing JSON geometry
        # For this MVP, we will just place markers
        # In a real app, we would parse p.geometry (GeoJSON)
        
        # Mocking offsets for visual separation based on ID
        lat = -15.793889 + (p.id * 0.002)
        lon = -47.882778 + (p.id * 0.002)
        
        color = "green"
        if p.current_load > p.capacity:
            color = "red"
        elif p.current_load > p.capacity * 0.8:
            color = "orange"
            
        folium.Marker(
            [lat, lon], 
            popup=(
                f"<b>{p.name}</b><br>"
                f"Lotação: {p.current_load}/{p.capacity}"
            ),
            icon=folium.Icon(color=color, icon="leaf")
        ).add_to(m)

st_data = st_folium(m, width=1200, height=600)

st.markdown("""
### Legenda
- 🟢 **Verde**: Lotação adequada
- 🟠 **Laranja**: Próximo da capacidade máxima
- 🔴 **Vermelho**: Superlotado
""")
