from __future__ import annotations

import cv2
import numpy as np

from core.database import fetch_df

EMBEDDING_TOLERANCE = 0.55
EMBEDDING_MARGIN = 0.03

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


def load_named_references() -> list[dict[str, np.ndarray]]:
    df = fetch_df(
        """
        SELECT nome, rosto_embeddings
        FROM rostos
        WHERE nome IS NOT NULL
          AND TRIM(nome) <> ''
          AND rosto_embeddings IS NOT NULL
        """
    )

    refs: list[dict[str, np.ndarray]] = []
    for _, row in df.iterrows():
        img = blob_to_image(row["rosto_embeddings"])
        emb = calculate_embedding(img)
        if emb is not None and emb.size == 128:
            refs.append({"nome": str(row["nome"]), "embedding": emb})
    return refs


def recognize_name(embedding: np.ndarray | None, refs: list[dict[str, np.ndarray]]) -> tuple[str | None, float | None]:
    if embedding is None or not refs:
        return None, None

    best_by_name: dict[str, float] = {}
    for ref in refs:
        dist = float(np.linalg.norm(ref["embedding"] - embedding))
        name = ref["nome"]
        if name not in best_by_name or dist < best_by_name[name]:
            best_by_name[name] = dist

    ranking = sorted((dist, name) for name, dist in best_by_name.items())
    best_dist, best_name = ranking[0]
    second_dist = ranking[1][0] if len(ranking) > 1 else None

    if second_dist is not None and (second_dist - best_dist) < EMBEDDING_MARGIN:
        return None, best_dist

    if best_dist <= EMBEDDING_TOLERANCE:
        return best_name, best_dist
    return None, best_dist
