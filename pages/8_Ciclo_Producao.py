import os
import sys
import datetime
import streamlit as st
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_session
from models import Animal, Event
from auth import check_auth

st.set_page_config(page_title="Ciclo Produtivo", page_icon="🔄", layout="wide")
check_auth()

st.title("🔄 Ciclo Produtivo Bovino")
st.markdown("Acompanhe e gerencie as fases de **Cria → Recria → Engorda → Venda** do seu rebanho.")

# ─── Constantes ───────────────────────────────────────────────────────────────
FASES = ["cria", "recria", "engorda", "venda"]
FASE_LABELS = {
    "cria":    "🐮 Cria",
    "recria":  "🌱 Recria",
    "engorda": "🍽️ Engorda",
    "venda":   "💰 Venda",
}
FASE_CORES = {
    "cria":    "#4CAF50",
    "recria":  "#2196F3",
    "engorda": "#FF9800",
    "venda":   "#9C27B0",
}
# Tempo máximo esperado (em dias) em cada fase — usado para alertas
FASE_ALERTA_DIAS = {
    "cria":    240,   # 8 meses
    "recria":  730,   # 24 meses
    "engorda": 548,   # 18 meses
    "venda":   60,    # 2 meses sem vender após marcação
}
PROXIMA_FASE = {
    "cria":    "recria",
    "recria":  "engorda",
    "engorda": "venda",
    "venda":   None,
}


def dias_na_fase(animal):
    hoje = datetime.date.today()
    if animal.data_fase:
        data = animal.data_fase if isinstance(animal.data_fase, datetime.date) \
               else datetime.date.fromisoformat(str(animal.data_fase))
        return (hoje - data).days
    return 0


tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🐄 Animais por Fase", "🔄 Transição de Fase"])

with get_db_session() as db:

    animais = db.query(Animal).filter(Animal.status == "active").all()

    # ─── TAB 1: DASHBOARD ────────────────────────────────────────────────────
    with tab1:
        st.header("Visão Geral do Ciclo Produtivo")

        if not animais:
            st.warning("Nenhum animal ativo cadastrado.")
        else:
            # KPI cards por fase
            cols = st.columns(4)
            for i, fase in enumerate(FASES):
                grupo = [a for a in animais if (a.fase or "cria") == fase]
                total = len(grupo)
                peso_medio = (
                    sum(a.current_weight or 0 for a in grupo) / total if total else 0
                )
                dias_medio = (
                    sum(dias_na_fase(a) for a in grupo) / total if total else 0
                )
                with cols[i]:
                    st.markdown(
                        f"""
                        <div style="background:{FASE_CORES[fase]};border-radius:12px;
                                    padding:18px 14px;color:#fff;text-align:center;">
                          <div style="font-size:28px;font-weight:700;">{total}</div>
                          <div style="font-size:15px;font-weight:600;">{FASE_LABELS[fase]}</div>
                          <div style="font-size:12px;margin-top:6px;">
                            ⚖️ {peso_medio:.0f} kg médio<br>
                            📅 {dias_medio:.0f} dias na fase
                          </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            st.markdown("<br>", unsafe_allow_html=True)

            # Gráfico de distribuição
            st.subheader("Distribuição por Fase")
            dist_data = {FASE_LABELS[f]: len([a for a in animais if (a.fase or "cria") == f])
                         for f in FASES}
            df_dist = pd.DataFrame.from_dict(
                dist_data, orient="index", columns=["Animais"]
            )
            st.bar_chart(df_dist)

            # ─── Alertas ───────────────────────────────────────────────────
            st.subheader("⚠️ Alertas — Animais com tempo excessivo na fase")

            alertas = [
                a for a in animais
                if (a.fase or "cria") in FASE_ALERTA_DIAS
                and dias_na_fase(a) > FASE_ALERTA_DIAS.get(a.fase or "cria", 9999)
            ]
            if alertas:
                rows = []
                for a in alertas:
                    fase_atual = a.fase or "cria"
                    dias = dias_na_fase(a)
                    limite = FASE_ALERTA_DIAS[fase_atual]
                    rows.append({
                        "RFID": a.rfid,
                        "Raça": a.breed,
                        "Fase": FASE_LABELS[fase_atual],
                        "Dias na Fase": dias,
                        "Limite (dias)": limite,
                        "Excesso (dias)": dias - limite,
                    })
                st.dataframe(pd.DataFrame(rows), use_container_width=True)
            else:
                st.success("✅ Todos os animais estão dentro do tempo esperado para cada fase.")

    # ─── TAB 2: ANIMAIS POR FASE ─────────────────────────────────────────────
    with tab2:
        st.header("Animais por Fase")

        if not animais:
            st.warning("Nenhum animal ativo cadastrado.")
        else:
            fases_sel = st.multiselect(
                "Filtrar por fase",
                options=FASES,
                default=FASES,
                format_func=lambda f: FASE_LABELS[f]
            )

            hoje = datetime.date.today()
            rows = []
            for a in animais:
                fase_atual = a.fase or "cria"
                if fase_atual not in fases_sel:
                    continue
                rows.append({
                    "RFID": a.rfid,
                    "Raça": a.breed,
                    "Fase": FASE_LABELS[fase_atual],
                    "Peso Atual (kg)": round(a.current_weight or 0, 1),
                    "Peso Entrada Fase (kg)": round(a.peso_entrada_fase or 0, 1),
                    "Ganho na Fase (kg)": round(
                        (a.current_weight or 0) - (a.peso_entrada_fase or a.current_weight or 0), 1
                    ),
                    "Data Entrada Fase": str(a.data_fase) if a.data_fase else "—",
                    "Dias na Fase": dias_na_fase(a),
                    "Piquete": a.paddock.name if a.paddock else "N/A",
                    "Status": a.status,
                })

            if rows:
                df = pd.DataFrame(rows).sort_values(
                    ["Fase", "Dias na Fase"], ascending=[True, False]
                )
                st.dataframe(df, use_container_width=True)
                st.caption(f"Total: {len(df)} animais")
            else:
                st.info("Nenhum animal nas fases selecionadas.")

    # ─── TAB 3: TRANSIÇÃO DE FASE ─────────────────────────────────────────────
    with tab3:
        st.header("Transição de Fase")
        st.info(
            "Selecione um animal e registre a mudança de fase. "
            "O evento fica registrado no histórico do animal."
        )

        if not animais:
            st.warning("Nenhum animal ativo cadastrado.")
        else:
            # Seleção do animal
            rfid_map = {
                f"{a.rfid} — {FASE_LABELS.get(a.fase or 'cria','?')} — {a.breed}": a
                for a in animais
            }
            sel_label = st.selectbox(
                "Selecionar Animal",
                ["— selecione —"] + list(rfid_map.keys())
            )

            if sel_label != "— selecione —":
                animal_sel = rfid_map[sel_label]
                fase_atual = animal_sel.fase or "cria"
                prox = PROXIMA_FASE.get(fase_atual)

                # Card resumo
                dias = dias_na_fase(animal_sel)
                st.success(f"✅ Animal **{animal_sel.rfid}** selecionado")
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Fase Atual", FASE_LABELS[fase_atual])
                    c2.metric("⚖️ Peso Atual", f"{animal_sel.current_weight or 0:.1f} kg")
                    c3.metric("📅 Dias na Fase", dias)
                    c4.metric("🐄 Raça", animal_sel.breed)

                st.divider()

                if prox is None:
                    st.warning(
                        "Este animal já está na fase **Venda**. "
                        "Use a Gestão de Rebanho para marcar como vendido."
                    )
                else:
                    # Formulário de transição
                    col_f, col_p = st.columns(2)
                    with col_f:
                        fases_disponiveis = FASES[FASES.index(fase_atual) + 1:]
                        nova_fase = st.selectbox(
                            "Nova Fase",
                            fases_disponiveis,
                            format_func=lambda f: FASE_LABELS[f]
                        )
                    with col_p:
                        novo_peso = st.number_input(
                            "Peso na Transição (kg)",
                            min_value=0.0,
                            step=0.5,
                            value=float(animal_sel.current_weight or 0)
                        )

                    obs = st.text_input(
                        "Observações (opcional)",
                        placeholder="Ex: Animal atingiu peso de desmame"
                    )

                    if st.button("✅ Confirmar Transição", type="primary"):
                        try:
                            # Atualiza o animal
                            animal_sel.fase = nova_fase
                            animal_sel.data_fase = datetime.date.today()
                            animal_sel.peso_entrada_fase = novo_peso
                            animal_sel.current_weight = novo_peso

                            # Registra evento
                            evento = Event(
                                animal_id=animal_sel.id,
                                date=datetime.date.today(),
                                event_type="fase_transition",
                                value=novo_peso,
                                details=(
                                    f"{FASE_LABELS[fase_atual]} → {FASE_LABELS[nova_fase]}"
                                    + (f" | {obs}" if obs else "")
                                )
                            )
                            db.add(evento)
                            db.commit()
                            st.success(
                                f"🎉 Animal **{animal_sel.rfid}** avançou para "
                                f"**{FASE_LABELS[nova_fase]}** com sucesso!"
                            )
                            st.balloons()
                        except Exception as e:
                            st.error(f"Erro ao registrar transição: {e}")
