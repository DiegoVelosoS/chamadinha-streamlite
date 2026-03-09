from __future__ import annotations

import cv2
import streamlit as st

from core.database import ensure_db, execute, fetch_df
from core.recognition import blob_to_image
from core.theme import setup_theme


ensure_db()
setup_theme(show_toggle=True, toggle_location="sidebar")
st.title("Validar Duplicados")


def _select_next_option(options: list, current_value, state_key: str) -> None:
    if not options:
        return
    try:
        idx = options.index(current_value)
    except ValueError:
        idx = -1
    next_idx = min(idx + 1, len(options) - 1)
    st.session_state[state_key] = options[next_idx]

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
    unnamed_options = unnamed["ord_id"].tolist()
    state_key_unnamed = "unnamed_select"

    if "auto_next_unnamed" in st.session_state and st.session_state["auto_next_unnamed"] in unnamed_options:
        st.session_state[state_key_unnamed] = st.session_state.pop("auto_next_unnamed")

    if state_key_unnamed not in st.session_state or st.session_state[state_key_unnamed] not in unnamed_options:
        st.session_state[state_key_unnamed] = unnamed_options[0]

    chosen = st.selectbox("Selecione ord_id sem nome", unnamed_options, key=state_key_unnamed)
    row = unnamed[unnamed["ord_id"] == chosen].iloc[0]
    img = blob_to_image(row["rosto_embeddings"])
    if img is not None:
        st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), caption=f"ord_id {row['ord_id']} | id {row['id_rosto']}")
    new_name = st.text_input("Nome para o rosto selecionado", key="new_name_unnamed")
    if st.button("Salvar nome", key="save_unnamed"):
        if new_name.strip():
            _select_next_option(unnamed_options, chosen, "auto_next_unnamed")
            execute(
                "UPDATE rostos SET nome = ?, origem_nome = 'manual' WHERE ord_id = ?",
                (new_name.strip(), int(chosen)),
            )
            st.success("Nome salvo com sucesso.")
            st.rerun()
        else:
            st.warning("Informe um nome valido.")

st.subheader("Comparar nomes repetidos")

duplicados = fetch_df(
    """
    SELECT
        LOWER(TRIM(nome)) AS nome_key,
        MIN(TRIM(nome)) AS nome_exibicao,
        COUNT(DISTINCT TRIM(id_rosto)) AS total_ids,
        COUNT(*) AS total_registros
    FROM rostos
    WHERE nome IS NOT NULL AND TRIM(nome) <> ''
    GROUP BY LOWER(TRIM(nome))
    HAVING COUNT(DISTINCT TRIM(id_rosto)) > 1
    ORDER BY nome_exibicao
    """
)

if duplicados.empty:
    st.info("Nao ha nomes duplicados para validar.")
    st.stop()

label_map = {
    f"{row['nome_exibicao']} ({int(row['total_ids'])} IDs, {int(row['total_registros'])} registros)": row["nome_key"]
    for _, row in duplicados.iterrows()
}
dup_options = list(label_map.keys())
dup_state_key = "dup_selected_label"

if "auto_next_dup" in st.session_state and st.session_state["auto_next_dup"] in dup_options:
    st.session_state[dup_state_key] = st.session_state.pop("auto_next_dup")

if dup_state_key not in st.session_state or st.session_state[dup_state_key] not in dup_options:
    st.session_state[dup_state_key] = dup_options[0]

selected_label = st.selectbox("Escolha um nome duplicado", dup_options, key=dup_state_key)
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

# Seleciona um representante por id_rosto para comparacao.
by_id = (
    regs.sort_values(by=["ord_id"], ascending=True)
    .groupby("id_rosto", as_index=False, sort=False)
    .first()
)

if len(by_id) < 2:
    st.warning("Nao ha IDs diferentes para este nome.")
    st.stop()

older = by_id.iloc[0]
newer = by_id.iloc[-1]

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

st.caption("Se for a mesma pessoa, mantemos o id mais antigo e mesclamos os registros do id mais recente.")

col_a, col_b = st.columns(2)
with col_a:
    if st.button("Mesma pessoa (mesclar)"):
        _select_next_option(dup_options, selected_label, "auto_next_dup")
        execute(
            """
            UPDATE rostos
            SET id_rosto = ?,
                nome = COALESCE(NULLIF(TRIM(nome), ''), ?)
            WHERE TRIM(id_rosto) = ?
            """,
            (str(older["id_rosto"]).strip(), str(older["nome"]).strip(), str(newer["id_rosto"]).strip()),
        )
        st.success("Duplicidade mesclada. IDs unificados e registros preservados.")
        st.rerun()
with col_b:
    renamed = st.text_input("Novo nome para o mais recente", key="rename_recent")
    if st.button("Pessoas diferentes (renomear)"):
        if not renamed.strip():
            st.warning("Informe um novo nome antes de confirmar.")
        else:
            _select_next_option(dup_options, selected_label, "auto_next_dup")
            execute(
                "UPDATE rostos SET nome = ?, origem_nome = 'manual' WHERE ord_id = ?",
                (renamed.strip(), int(newer["ord_id"])),
            )
            st.success("Registro mais recente renomeado.")
            st.rerun()

st.subheader("Detalhamento")
detail = regs[["ord_id", "id_rosto", "nome", "turma", "data_imagem"]].copy()
st.dataframe(detail, use_container_width=True)
