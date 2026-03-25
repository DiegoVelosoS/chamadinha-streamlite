from __future__ import annotations

import cv2
import numpy as np

from core.database import fetch_df

EMBEDDING_TOLERANCE = 0.60
EMBEDDING_MARGIN = 0.10

try:
    import face_recognition
except ImportError:
    face_recognition = None


def blob_to_image(blob: bytes | None) -> np.ndarray | None:
    if not blob:
        return None
    arr = np.frombuffer(blob, dtype=np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)


def image_to_jpeg_bytes(image_bgr: np.ndarray) -> bytes:
    ok, buffer = cv2.imencode(".jpg", image_bgr)
    if not ok:
        raise ValueError("Falha ao codificar imagem para JPEG.")
    return buffer.tobytes()


def calculate_embedding(face_bgr: np.ndarray | None) -> np.ndarray | None:
    if face_recognition is None:
        return None
    if face_bgr is None or face_bgr.size == 0:
        return None

    variants = [face_bgr]
    h, w = face_bgr.shape[:2]

    if min(h, w) < 160:
        up = cv2.resize(face_bgr, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
        variants.append(up)

    ycrcb = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2YCrCb)
    y, cr, cb = cv2.split(ycrcb)
    y_eq = cv2.equalizeHist(y)
    eq = cv2.cvtColor(cv2.merge([y_eq, cr, cb]), cv2.COLOR_YCrCb2BGR)
    variants.append(eq)

    for variant in variants:
        rgb = cv2.cvtColor(variant, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb, model="small")
        if encodings:
            return encodings[0].astype(np.float32)
    return None


def load_named_references() -> list[dict[str, object]]:
    df = fetch_df(
        """
        SELECT ord_id, id_rosto, nome, rosto_embeddings
        FROM rostos
        WHERE nome IS NOT NULL
          AND TRIM(nome) <> ''
          AND rosto_embeddings IS NOT NULL
        """
    )

    refs: list[dict[str, object]] = []
    for _, row in df.iterrows():
        img = blob_to_image(row["rosto_embeddings"])
        emb = calculate_embedding(img)
        if emb is not None and emb.size == 128:
            refs.append(
                {
                    "ord_id": int(row["ord_id"]),
                    "id_rosto": str(row["id_rosto"]),
                    "nome": str(row["nome"]),
                    "embedding": emb,
                }
            )
    return refs


def recognize_name(
    embedding: np.ndarray | None,
    refs: list[dict[str, object]],
) -> tuple[str | None, int | None, str | None, float | None]:
    if embedding is None or not refs:
        return None, None, None, None

    ranking: list[tuple[float, dict[str, object]]] = []
    for ref in refs:
        dist = float(np.linalg.norm(ref["embedding"] - embedding))
        ranking.append((dist, ref))

    ranking.sort(key=lambda x: x[0])
    best_dist, best_ref = ranking[0]
    second_dist = ranking[1][0] if len(ranking) > 1 else None

    if second_dist is not None and (second_dist - best_dist) < EMBEDDING_MARGIN:
        return None, None, None, best_dist

    if best_dist <= EMBEDDING_TOLERANCE:
        return (
            str(best_ref["nome"]),
            int(best_ref["ord_id"]),
            str(best_ref["id_rosto"]),
            best_dist,
        )
    return None, None, None, best_dist
