from __future__ import annotations

import cv2
import streamlit as st

from core.database import ensure_db, execute, fetch_df
from core.recognition import blob_to_image


ensure_db()
st.title("Validar Duplicados")

st.subheader("Nomear rostos sem nome")
unnamed = fetch_df(
    """
    SELECT ord_id, id_rosto, turma, data_imagem, rosto_embeddings
    FROM rostos
    WHERE nome IS NULL OR TRIM(nome) = ''
    ORDER BY ord_id ASC
    """
)

if unnamed.empty:
    st.info("Nao ha rostos sem nome.")
else:
    chosen = st.selectbox("Selecione ord_id sem nome", unnamed["ord_id"].tolist(), key="unnamed_select")
    row = unnamed[unnamed["ord_id"] == chosen].iloc[0]
    img = blob_to_image(row["rosto_embeddings"])
    if img is not None:
        st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), caption=f"ord_id {row['ord_id']} | id {row['id_rosto']}")
    new_name = st.text_input("Nome para o rosto selecionado", key="new_name_unnamed")
    if st.button("Salvar nome", key="save_unnamed"):
        if new_name.strip():
            execute(
                "UPDATE rostos SET nome = ?, origem_nome = 'manual' WHERE ord_id = ?",
                (new_name.strip(), int(chosen)),
            )
            st.success("Nome salvo com sucesso.")
        else:
            st.warning("Informe um nome valido.")

st.subheader("Comparar nomes repetidos")

duplicados = fetch_df(
    """
    SELECT LOWER(TRIM(nome)) AS nome_key, MIN(TRIM(nome)) AS nome_exibicao, COUNT(*) AS total
    FROM rostos
    WHERE nome IS NOT NULL AND TRIM(nome) <> ''
    GROUP BY LOWER(TRIM(nome))
    HAVING COUNT(*) > 1
    ORDER BY nome_exibicao
    """
)

if duplicados.empty:
    st.info("Nao ha nomes duplicados para validar.")
    st.stop()

label_map = {
    f"{row['nome_exibicao']} ({int(row['total'])} registros)": row["nome_key"]
    for _, row in duplicados.iterrows()
}
selected_label = st.selectbox("Escolha um nome duplicado", list(label_map.keys()))
selected_key = label_map[selected_label]

regs = fetch_df(
    """
    SELECT ord_id, id_rosto, nome, turma, data_imagem, rosto_embeddings
    FROM rostos
    WHERE LOWER(TRIM(nome)) = ?
    ORDER BY ord_id ASC
    """,
    (selected_key,),
)

if len(regs) < 2:
    st.warning("Nao ha ao menos dois registros para comparar.")
    st.stop()

older = regs.iloc[0]
newer = regs.iloc[-1]

c1, c2 = st.columns(2)
with c1:
    img_old = blob_to_image(older["rosto_embeddings"])
    if img_old is not None:
        st.image(cv2.cvtColor(img_old, cv2.COLOR_BGR2RGB), caption=f"Mais antigo ord_id={older['ord_id']}")
    st.write(f"id_rosto: {older['id_rosto']}")
    st.write(f"nome: {older['nome']}")
with c2:
    img_new = blob_to_image(newer["rosto_embeddings"])
    if img_new is not None:
        st.image(cv2.cvtColor(img_new, cv2.COLOR_BGR2RGB), caption=f"Mais recente ord_id={newer['ord_id']}")
    st.write(f"id_rosto: {newer['id_rosto']}")
    st.write(f"nome: {newer['nome']}")

st.caption("Se for a mesma pessoa, mantemos o mais antigo e removemos o mais recente.")

col_a, col_b = st.columns(2)
with col_a:
    if st.button("Mesma pessoa (mesclar)"):
        execute("DELETE FROM rostos WHERE ord_id = ?", (int(newer["ord_id"]),))
        st.success("Duplicidade mesclada. Registro mais recente removido.")
with col_b:
    renamed = st.text_input("Novo nome para o mais recente", key="rename_recent")
    if st.button("Pessoas diferentes (renomear)"):
        if not renamed.strip():
            st.warning("Informe um novo nome antes de confirmar.")
        else:
            execute(
                "UPDATE rostos SET nome = ?, origem_nome = 'manual' WHERE ord_id = ?",
                (renamed.strip(), int(newer["ord_id"])),
            )
            st.success("Registro mais recente renomeado.")

st.subheader("Detalhamento")
detail = regs[["ord_id", "id_rosto", "nome", "turma", "data_imagem"]].copy()
st.dataframe(detail, use_container_width=True)
