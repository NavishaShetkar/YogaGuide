import os
import json
import numpy as np
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

LANDMARK_DIR = "landmarks"
MODEL_DIR = "models"

os.makedirs(MODEL_DIR, exist_ok=True)

def load_landmarks():
    X = []  # features
    y = []  # labels

    for pose_name in os.listdir(LANDMARK_DIR):
        pose_folder = os.path.join(LANDMARK_DIR, pose_name)

        if not os.path.isdir(pose_folder):
            continue

        for file in os.listdir(pose_folder):
            if not file.endswith(".json"):
                continue
            
            filepath = os.path.join(pose_folder, file)

            with open(filepath, "r") as f:
                data = json.load(f)

            # Convert landmark list → flat feature vector
            flat = []
            for lm in data:
                flat.extend([lm["x"], lm["y"], lm["z"]])  # using xyz only

            X.append(flat)
            y.append(pose_name)

    return np.array(X), np.array(y)


def train_svm_model():
    print("📌 Loading dataset...")
    X, y = load_landmarks()

    print("📌 Scaling features...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    print("📌 Splitting train/test...")
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )

    print("📌 Training SVM model...")
    model = SVC(kernel="rbf", probability=True)
    model.fit(X_train, y_train)

    print("📌 Testing model...")
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print(f"✅ Model Accuracy: {acc * 100:.2f}%")

    print("📌 Saving model...")
    joblib.dump(model, os.path.join(MODEL_DIR, "svm_pose_model.pkl"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.pkl"))

    print("🎉 Training complete!")
    print("📂 Saved: models/svm_pose_model.pkl")
    print("📂 Saved: models/scaler.pkl")


if __name__ == "__main__":
    train_svm_model()