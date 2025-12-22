import cv2
import mediapipe as mp
import numpy as np
import joblib
import os
import json

MODEL_PATH = "models/svm_pose_model.pkl"
SCALER_PATH = "models/scaler.pkl"

# Load trained model + scaler
model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

mp_pose = mp.solutions.pose


def extract_landmarks_from_image(img_path):
    """Returns flattened landmark list OR None if no human detected"""
    img = cv2.imread(img_path)

    if img is None:
        print(f"⚠️ Could not load image: {img_path}")
        return None

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    with mp_pose.Pose(static_image_mode=True) as pose:
        result = pose.process(img_rgb)

        if not result.pose_landmarks:
            print("⚠️ No landmarks detected in image.")
            return None

        lm_list = []
        for lm in result.pose_landmarks.landmark:
            lm_list.extend([lm.x, lm.y, lm.z])

        return np.array(lm_list)


def predict_pose(img_path):
    print(f"📌 Processing: {img_path}")
    
    lm = extract_landmarks_from_image(img_path)
    if lm is None:
        return {"error": "No pose detected"}

    lm = lm.reshape(1, -1)       # Shape (1, 99)
    lm_scaled = scaler.transform(lm)

    pred = model.predict(lm_scaled)[0]
    prob = model.predict_proba(lm_scaled)[0].max() * 100

    return {
        "pose": pred,
        "confidence": round(prob, 2)
    }


if __name__ == "__main__":
    # TEST WITH ANY IMAGE
    test_img = "test.jpg"   # ← change this
    result = predict_pose(test_img)
    print(result)