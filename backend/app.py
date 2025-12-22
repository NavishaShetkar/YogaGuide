import os
import cv2
import numpy as np
import mediapipe as mp
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from models import db, User
import joblib

app = Flask(__name__)
CORS(app)

# --------------------------
# DATABASE CONFIG
# --------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))     # backend/
DB_PATH = os.path.join(BASE_DIR, "instance", "yogaguide.db")

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# --------------------------
# LOAD AI MODEL + SCALER
# --------------------------
MODEL_PATH = os.path.join(BASE_DIR, "yoga_ai", "models", "svm_pose_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "yoga_ai", "models", "scaler.pkl")

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

mp_pose = mp.solutions.pose


# --------------------------
# FRONTEND ROUTING
# --------------------------
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "home.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(FRONTEND_DIR, path)


# --------------------------
# USER AUTH API
# --------------------------

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    user = User(username=username, email=email)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "You don’t have an account. Please Sign Up!"}), 404

    if not user.check_password(password):
        return jsonify({"error": "Incorrect password."}), 401

    return jsonify({"message": "Login success"}), 200



# --------------------------
# AI POSE PREDICTION API
# --------------------------

@app.route("/predict", methods=["POST"])
def predict_pose():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    temp_path = os.path.join(BASE_DIR, "temp_pose.jpg")
    file.save(temp_path)

    img = cv2.imread(temp_path)
    if img is None:
        return jsonify({"error": "Invalid image"}), 400

    # Use MediaPipe to extract landmarks
    with mp_pose.Pose(static_image_mode=True) as pose:
        results = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

        if not results.pose_landmarks:
            return jsonify({"error": "No pose detected"}), 400

        landmarks = []
        for lm in results.pose_landmarks.landmark:
            landmarks.extend([lm.x, lm.y, lm.z])

    # Model prediction
    X = scaler.transform([landmarks])
    prediction = model.predict(X)[0]

    return jsonify({
        "pose": prediction,
        "message": "Pose detected successfully"
    })


# --------------------------
# RUN SERVER
# --------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
