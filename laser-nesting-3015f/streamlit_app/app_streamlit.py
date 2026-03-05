from __future__ import annotations

import json
import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
import streamlit as st

from backend.app.export.dxf_exporter import export_plan_to_dxf
from backend.app.main import _build_plan
from backend.app.schemas import PlanRequest

st.set_page_config(page_title="Laser Nesting 3015F", layout="wide")
st.title("Laser Nesting 3015F - protótipo Streamlit")

col1, col2 = st.columns([1, 2])
with col1:
    largura = st.number_input("Largura chapa (mm)", value=3000.0, min_value=100.0)
    altura = st.number_input("Altura chapa (mm)", value=1500.0, min_value=100.0)
    margem = st.number_input("Margem (mm)", value=10.0, min_value=0.0)
    espessura = st.number_input("Espessura (mm)", value=3.0, min_value=0.1)
    diam = st.number_input("Diâmetro peça (mm)", value=127.0, min_value=1.0)
    kerf = st.number_input("Kerf (mm)", value=1.5, min_value=0.0)
    spacing = st.number_input("Spacing (mm)", value=2.0, min_value=0.0)
    vel = st.number_input("Velocidade corte (mm/s)", value=35.0, min_value=0.1)
    metodo = st.selectbox("Método", ["auto", "grid", "hex"], index=0)
    run = st.button("Calcular")

if run:
    params = PlanRequest(
        largura_chapa=largura,
        altura_chapa=altura,
        espessura=espessura,
        margem_borda=margem,
        diametro_peca=diam,
        kerf_laser=kerf,
        spacing=spacing,
        velocidade_corte=vel,
        metodo_preferido=metodo,
    )
    plan = _build_plan(params)

    with col2:
        st.metric("Total de peças", plan.total_pecas)
        st.metric("Aproveitamento", f"{plan.aproveitamento:.2f}%")
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.set_xlim(0, params.largura_chapa)
        ax.set_ylim(0, params.altura_chapa)
        ax.set_aspect("equal", adjustable="box")
        for piece in plan.pecas:
            ax.add_patch(plt.Circle((piece.x, piece.y), piece.raio, fill=False, linewidth=0.8))
        ax.set_title(f"Plano de corte - {plan.total_pecas} peças Ø{params.diametro_peca:.0f} mm")
        ax.set_xlabel("mm")
        ax.set_ylabel("mm")
        st.pyplot(fig)

    json_bytes = json.dumps(plan.model_dump(mode="json"), ensure_ascii=False, indent=2).encode("utf-8")
    st.download_button("Baixar JSON", data=json_bytes, file_name="plano_nesting.json", mime="application/json")

    with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as tmp:
        dxf_path = export_plan_to_dxf(params, plan.pecas, Path(tmp.name))
    st.download_button("Baixar DXF", data=dxf_path.read_bytes(), file_name="plano_nesting.dxf", mime="application/dxf")
