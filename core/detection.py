from __future__ import annotations

import os
import urllib.request

import cv2
import numpy as np
import streamlit as st


@st.cache_resource
def load_yunet() -> cv2.FaceDetectorYN:
    model_path = "face_detection_yunet_2023mar.onnx"
    if not os.path.exists(model_path):
        url = (
            "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/"
            "face_detection_yunet_2023mar.onnx"
        )
        urllib.request.urlretrieve(url, model_path)

    return cv2.FaceDetectorYN.create(model_path, "", (320, 320), 0.6, 0.3, 5000)


def _detect_dnn(image_bgr: np.ndarray, confidence_threshold: float = 0.2) -> np.ndarray:
    model_file = "res10_300x300_ssd_iter_140000.caffemodel"
    config_file = "deploy.prototxt"

    if not (os.path.exists(model_file) and os.path.exists(config_file)):
        base_url = "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector"
        if not os.path.exists(config_file):
            urllib.request.urlretrieve(f"{base_url}/deploy.prototxt", config_file)
        if not os.path.exists(model_file):
            urllib.request.urlretrieve(
                f"{base_url}/res10_300x300_ssd_iter_140000.caffemodel", model_file
            )

    net = cv2.dnn.readNetFromCaffe(config_file, model_file)

    h, w = image_bgr.shape[:2]
    blob = cv2.dnn.blobFromImage(
        cv2.resize(image_bgr, (300, 300)),
        1.0,
        (300, 300),
        (104.0, 177.0, 123.0),
    )
    net.setInput(blob)
    detections = net.forward()

    faces = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence <= confidence_threshold:
            continue

        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        x1, y1, x2, y2 = box.astype(int)
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)

        fw, fh = x2 - x1, y2 - y1
        if fw < 30 or fh < 30:
            continue

        faces.append((x1, y1, fw, fh))

    return np.array(faces)


def detect_faces(image_bgr: np.ndarray) -> np.ndarray:
    try:
        detector = load_yunet()
        h, w = image_bgr.shape[:2]
        detector.setInputSize((w, h))
        _, faces = detector.detect(image_bgr)

        if faces is None:
            return np.array([])

        out = []
        for face in faces:
            x, y, fw, fh = face[:4].astype(int)
            x, y = max(0, x), max(0, y)
            fw, fh = min(fw, w - x), min(fh, h - y)
            out.append((x, y, fw, fh))
        return np.array(out)
    except Exception:
        return _detect_dnn(image_bgr)
