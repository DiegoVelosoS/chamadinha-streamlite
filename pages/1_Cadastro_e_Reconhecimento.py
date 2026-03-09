from __future__ import annotations

from datetime import datetime

import cv2
import numpy as np
import streamlit as st

from core.database import ensure_db, execute_many, next_image_number
from core.detection import detect_faces
from core.recognition import (
    calculate_embedding,
    image_to_jpeg_bytes,
    load_named_references,
    recognize_name,
)
from core.theme import setup_theme


ensure_db()
setup_theme(show_toggle=True, toggle_location="sidebar")
st.title("Cadastro e Reconhecimento")
st.caption("Upload de imagem, deteccao de rostos e cadastro com reconhecimento automatico.")

if "detected_items" not in st.session_state:
    st.session_state.detected_items = []
if "current_image" not in st.session_state:
    st.session_state.current_image = None
if "current_image_number" not in st.session_state:
    st.session_state.current_image_number = None

uploaded = st.file_uploader("Imagem", type=["jpg", "jpeg", "png", "bmp", "webp"])
turma = st.text_input("Turma", value="Turma A")
data_imagem = st.text_input("Data e hora (AAAA-MM-DD HH:MM)", value=datetime.now().strftime("%Y-%m-%d %H:%M"))

if st.button("Detectar rostos", type="primary"):
    if uploaded is None:
        st.error("Envie uma imagem antes de detectar.")
    else:
        file_bytes = np.asarray(bytearray(uploaded.read()), dtype=np.uint8)
        image_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if image_bgr is None:
            st.error("Nao foi possivel decodificar a imagem enviada.")
        else:
            refs = load_named_references()
            faces = detect_faces(image_bgr)

            detected_items: list[dict[str, object]] = []
            for idx, (x, y, w, h) in enumerate(faces):
                crop = image_bgr[y : y + h, x : x + w]
                emb = calculate_embedding(crop)
                suggested_name, suggested_ord_id, suggested_face_id, distance = recognize_name(emb, refs)

                detected_items.append(
                    {
                        "idx": idx,
                        "bbox": (int(x), int(y), int(w), int(h)),
                        "crop": crop,
                        "embedding_ok": emb is not None,
                        "suggested_name": suggested_name,
                        "suggested_ord_id": suggested_ord_id,
                        "suggested_face_id": suggested_face_id,
                        "distance": distance,
                    }
                )

            st.session_state.current_image = image_bgr
            st.session_state.current_image_number = next_image_number()
            st.session_state.detected_items = detected_items
            st.success(f"{len(detected_items)} rosto(s) detectado(s).")

items = st.session_state.detected_items
image_bgr = st.session_state.current_image
image_number = st.session_state.current_image_number

if image_bgr is not None and items:
    preview = image_bgr.copy()
    for item in items:
        x, y, w, h = item["bbox"]
        cv2.rectangle(preview, (x, y), (x + w, y + h), (255, 255, 0), 1)

    st.image(cv2.cvtColor(preview, cv2.COLOR_BGR2RGB), caption="Rostos detectados", use_container_width=True)

    st.subheader("Confirmacao antes de salvar")
    rows_to_insert: list[tuple[bytes, str, str | None, int, str, str, str | None]] = []

    for item in items:
        idx = int(item["idx"])
        crop = item["crop"]
        suggested = item["suggested_name"]
        suggested_ord_id = item.get("suggested_ord_id")
        suggested_face_id = item.get("suggested_face_id")
        distance = item["distance"]

        key_suffix = f"{int(image_number)}_{idx}"
        yes_key = f"yes_{key_suffix}"
        manual_key = f"manual_name_{key_suffix}"
        noname_key = f"noname_{key_suffix}"
        direct_name_key = f"direct_name_{key_suffix}"

        c1, c2 = st.columns([1, 2])
        with c1:
            st.image(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB), caption=f"Rosto {idx + 1}")
        with c2:
            if suggested:
                ord_id_text = str(suggested_ord_id) if suggested_ord_id is not None else "desconhecido"
                id_rosto_text = str(suggested_face_id) if suggested_face_id is not None else "desconhecido"
                st.write(
                    f"Reconhecido como: {suggested} (ID {ord_id_text}) | id_rosto {id_rosto_text}"
                )
                if distance is not None:
                    st.write(f"Distancia do reconhecimento: {distance:.3f}")

                action_col, input_col = st.columns([1, 2])
                with action_col:
                    if st.button(f"Sim, e {suggested}", key=f"confirm_yes_{key_suffix}"):
                        st.session_state[yes_key] = True
                    if st.session_state.get(yes_key, False):
                        st.success("Confirmado")
                with input_col:
                    st.text_input(
                        "Se nao for a mesma pessoa, digite o nome correto",
                        key=manual_key,
                        placeholder="Nome correto",
                    )
            else:
                st.text_input(
                    f"Nome do rosto {idx + 1}",
                    key=direct_name_key,
                    placeholder="Digite o nome",
                )

            st.checkbox("Salvar sem nome", key=noname_key)
            st.write(f"Embedding valido: {'sim' if item['embedding_ok'] else 'nao'}")

    submit = st.button("Salvar todos os rostos", type="primary")

    if submit:
        try:
            datetime.strptime(data_imagem, "%Y-%m-%d %H:%M")
        except ValueError:
            st.error("Data invalida. Use o formato AAAA-MM-DD HH:MM.")
        else:
            invalid_confirmations: list[str] = []
            for item in items:
                idx = int(item["idx"])
                crop = item["crop"]
                suggested = item["suggested_name"]

                key_suffix = f"{int(image_number)}_{idx}"
                yes_key = f"yes_{key_suffix}"
                manual_key = f"manual_name_{key_suffix}"
                noname_key = f"noname_{key_suffix}"
                direct_name_key = f"direct_name_{key_suffix}"

                keep_without_name = st.session_state.get(noname_key, False)
                manual_name = st.session_state.get(manual_key, "").strip()
                direct_name = st.session_state.get(direct_name_key, "").strip()
                confirmed_yes = bool(st.session_state.get(yes_key, False))

                final_name = ""
                if suggested:
                    if manual_name:
                        final_name = manual_name
                    elif confirmed_yes:
                        final_name = str(suggested)
                    elif not keep_without_name:
                        invalid_confirmations.append(
                            f"Rosto {idx + 1}: clique em 'Sim' para confirmar '{suggested}' ou digite outro nome."
                        )
                else:
                    final_name = direct_name

                if keep_without_name:
                    final_name = ""

                ord_str = f"{int(image_number):03d}"
                idx_str = f"{idx:03d}"
                data_str = datetime.strptime(data_imagem, "%Y-%m-%d %H:%M").strftime("%Y%m%d%H%M")
                id_rosto = f"{ord_str}-{idx_str}-{data_str}"

                origem_nome = None
                if final_name:
                    origem_nome = "automatico" if suggested and final_name == suggested else "manual"

                rows_to_insert.append(
                    (
                        image_to_jpeg_bytes(crop),
                        id_rosto,
                        final_name if final_name else None,
                        int(image_number),
                        turma.strip() if turma.strip() else "Turma sem nome",
                        data_imagem,
                        origem_nome,
                    )
                )

            if invalid_confirmations:
                for msg in invalid_confirmations:
                    st.error(msg)
                st.stop()

            execute_many(
                """
                INSERT INTO rostos (rosto_embeddings, id_rosto, nome, numero_imagem, turma, data_imagem, origem_nome)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                rows_to_insert,
            )
            st.success(f"{len(rows_to_insert)} registro(s) salvo(s) no banco.")
            st.session_state.detected_items = []

elif image_bgr is not None and not items:
    st.warning("Nenhum rosto detectado para a imagem atual.")
