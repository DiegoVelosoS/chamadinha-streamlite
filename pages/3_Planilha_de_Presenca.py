from __future__ import annotations

import streamlit as st

from core.database import ensure_db, fetch_df
from core.presence import build_presence_sheet, dataframe_to_csv_bytes, dataframe_to_xlsx_bytes
from core.theme import setup_theme


ensure_db()
setup_theme(show_toggle=True, toggle_location="sidebar")
st.title("Planilha de Presenca")

base_df = fetch_df(
    """
    SELECT ord_id, id_rosto, nome, numero_imagem, turma, data_imagem
    FROM rostos
    ORDER BY ord_id ASC
    """
)

if base_df.empty:
    st.info("Nao ha registros no banco para consolidar.")
    st.stop()

presence_df = build_presence_sheet(base_df)

if presence_df.empty:
    st.warning("Nao foi possivel consolidar a planilha com os dados atuais.")
    st.stop()

st.subheader("Previa")
st.dataframe(presence_df, use_container_width=True)

csv_bytes = dataframe_to_csv_bytes(presence_df)
st.download_button(
    label="Baixar CSV",
    data=csv_bytes,
    file_name="planilha_presenca.csv",
    mime="text/csv",
)

try:
    xlsx_bytes = dataframe_to_xlsx_bytes(presence_df)
    st.download_button(
        label="Baixar XLSX",
        data=xlsx_bytes,
        file_name="planilha_presenca.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
except Exception as exc:
    st.warning(f"Nao foi possivel gerar XLSX: {exc}")
