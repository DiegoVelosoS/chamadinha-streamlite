from __future__ import annotations

import cv2
import pandas as pd
import streamlit as st

from core.database import ensure_db, execute, fetch_df
from core.recognition import blob_to_image
from core.theme import setup_theme


ensure_db()
setup_theme(show_toggle=True, toggle_location="sidebar")
st.title("Galeria e Edição")

query = """
SELECT ord_id, id_rosto, nome, numero_imagem, turma, data_imagem, origem_nome, rosto_embeddings
FROM rostos
ORDER BY ord_id DESC
"""
df = fetch_df(query)

if df.empty:
    st.info("Ainda nao ha registros no banco.")
    st.stop()

f1, f2 = st.columns(2)
with f1:
    filtro_nome = st.text_input("Filtrar por nome")
with f2:
    filtro_turma = st.text_input("Filtrar por turma")

filtrado = df.copy()
if filtro_nome.strip():
    filtrado = filtrado[filtrado["nome"].fillna("").str.contains(filtro_nome, case=False)]
if filtro_turma.strip():
    filtrado = filtrado[filtrado["turma"].fillna("").str.contains(filtro_turma, case=False)]

st.subheader("Tabela de registros")
st.dataframe(
    filtrado[["ord_id", "id_rosto", "nome", "numero_imagem", "turma", "data_imagem", "origem_nome"]],
    use_container_width=True,
)

st.subheader("Mini galeria")
show_n = st.slider("Quantidade de imagens", min_value=1, max_value=min(30, len(filtrado)), value=min(8, len(filtrado)))
cols = st.columns(4)

for i, (_, row) in enumerate(filtrado.head(show_n).iterrows()):
    img = blob_to_image(row["rosto_embeddings"])
    with cols[i % 4]:
        if img is not None:
            st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), caption=f"ord_id {row['ord_id']}")
        st.write(f"nome: {row['nome'] if pd.notna(row['nome']) else '(sem nome)'}")
        st.write(f"turma: {row['turma']}")

st.subheader("Editar registro")
ord_ids = filtrado["ord_id"].tolist()
selected_ord = st.selectbox("Selecione o ord_id", ord_ids)
selected = filtrado[filtrado["ord_id"] == selected_ord].iloc[0]

# Mostra a imagem do rosto do registro selecionado para facilitar a edicao.
selected_img = blob_to_image(selected["rosto_embeddings"])
if selected_img is not None:
    st.image(cv2.cvtColor(selected_img, cv2.COLOR_BGR2RGB), caption=f"Rosto do ord_id {selected_ord}", width=140)
else:
    st.info("Este registro nao possui imagem de rosto valida.")

with st.form("edit_record"):
    new_name = st.text_input("Nome", value=selected["nome"] if pd.notna(selected["nome"]) else "")
    new_class = st.text_input("Turma", value=str(selected["turma"]))
    new_img_num = st.number_input("Numero de Presença(s)", min_value=0, value=int(selected["numero_imagem"]), step=1)
    new_date = st.text_input("Data 1ª Presença", value=str(selected["data_imagem"]))
    submit_edit = st.form_submit_button("Salvar alteracoes")

if submit_edit:
    execute(
        """
        UPDATE rostos
        SET nome = ?, turma = ?, numero_imagem = ?, data_imagem = ?, origem_nome = ?
        WHERE ord_id = ?
        """,
        (
            new_name.strip() if new_name.strip() else None,
            new_class.strip() if new_class.strip() else "Turma sem nome",
            int(new_img_num),
            new_date.strip(),
            "manual" if new_name.strip() else None,
            int(selected_ord),
        ),
    )
    st.success("Registro atualizado.")

if st.button("Excluir registro selecionado", type="secondary"):
    execute("DELETE FROM rostos WHERE ord_id = ?", (int(selected_ord),))
    st.success("Registro excluido.")
