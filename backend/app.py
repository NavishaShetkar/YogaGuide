from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS

import os
import uuid
import gc

import mysql.connector

import live_pose

from live_pose import generate_frames

from cnn_model.predict_cnn import predict_image

# --------------------------
# MYSQL CONNECTION
# --------------------------
db = mysql.connector.connect(

    host="localhost",

    user="root",

    password="",

    database="yogaguide_db"
)

cursor = db.cursor(
    dictionary=True
)

# --------------------------
# FLASK APP
# --------------------------
app = Flask(__name__)

CORS(app)

# --------------------------
# PATH SETTINGS
# --------------------------
BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

FRONTEND_DIR = os.path.join(
    BASE_DIR,
    "..",
    "frontend"
)

# --------------------------
# FRONTEND ROUTES
# --------------------------
@app.route("/")
def home():

    return send_from_directory(
        FRONTEND_DIR,
        "index.html"
    )

@app.route("/<path:path>")
def static_files(path):

    return send_from_directory(
        FRONTEND_DIR,
        path
    )

# --------------------------
# REGISTER API
# --------------------------
@app.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    cursor.execute(

        "SELECT * FROM users WHERE email = %s",

        (data["email"],)
    )

    if cursor.fetchone():

        return jsonify({
            "error": "User already exists"
        }), 400

    cursor.execute(

        """
        INSERT INTO users
        (username, email, password)
        VALUES (%s,%s,%s)
        """,

        (
            data["username"],
            data["email"],
            data["password"]
        )
    )

    db.commit()

    return jsonify({
        "message": "Registration successful"
    })

# --------------------------
# LOGIN API
# --------------------------
@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    cursor.execute(

        """
        SELECT * FROM users
        WHERE email=%s AND password=%s
        """,

        (
            data["email"],
            data["password"]
        )
    )

    user = cursor.fetchone()

    if user:

        return jsonify({

            "success": True,

            "user_id": user["id"]
        })

    return jsonify({
        "error": "Invalid credentials"
    }), 401

# --------------------------
# GET PROFILE
# --------------------------
@app.route("/get_profile/<int:user_id>")
def get_profile(user_id):

    cursor.execute(

        """
        SELECT * FROM profiles
        WHERE user_id=%s
        """,

        (user_id,)
    )

    profile = cursor.fetchone()

    if profile:

        return jsonify(profile)

    return jsonify({
        "error": "Profile not found"
    }), 404

# --------------------------
# SAVE PROFILE
# --------------------------
@app.route("/save_profile", methods=["POST"])
def save_profile():

    data = request.get_json()

    cursor.execute(

        """
        INSERT INTO profiles

        (
            user_id,
            full_name,
            age,
            gender,
            experience,
            goal,
            height,
            weight,
            injury
        )

        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,

        (
            data["user_id"],
            data["full_name"],
            data["age"],
            data["gender"],
            data["experience"],
            data["goal"],
            data["height"],
            data["weight"],
            data["injury"]
        )
    )

    db.commit()

    return jsonify({
        "message": "Profile saved"
    })

# --------------------------
# WEBCAM STREAM
# --------------------------
@app.route("/video_feed")
def video_feed():

    return Response(

        generate_frames(),

        mimetype=(
            "multipart/x-mixed-replace;"
            " boundary=frame"
        )
    )

# --------------------------
# GET LIVE POSE
# --------------------------
@app.route("/get_pose/<int:user_id>")
def get_pose(user_id):

    # ---------- LIVE DATA ----------
    pose = (

        live_pose.latest_pose

        if live_pose.latest_pose

        else "No Pose Detected"
    )

    confidence = round(

        live_pose.latest_confidence or 0,

        2
    )

    correction = (
        live_pose.correction_message
    )

    # ---------- USER PROFILE ----------
    cursor.execute(

        """
        SELECT * FROM profiles
        WHERE user_id=%s
        """,

        (user_id,)
    )

    user = cursor.fetchone()

    recommendation = "✅ Suitable"

    # --------------------------
    # SAFETY RULES
    # --------------------------
    if user:

        age = user["age"]

        experience = user["experience"]

        injury = user["injury"]

        # ---------- KNEE INJURY ----------
        if (
            injury
            and
            "knee" in str(injury).lower()
        ):

            if pose in [

                "Veerabhadrasana",

                "UtkataKonasana",

                "ArdhaChandrasana"
            ]:

                recommendation = (
                    "❌ Avoid "
                    "(Knee injury)"
                )

        # ---------- BACK INJURY ----------
        elif (
            injury
            and
            "back" in str(injury).lower()
        ):

            if pose in [

                "Downward_dog",

                "Triangle"
            ]:

                recommendation = (
                    "❌ Avoid "
                    "(Back injury)"
                )

        # ---------- BEGINNER ----------
        elif experience == "Beginner":

            if pose in [

                "Natarajasana",

                "ArdhaChandrasana"
            ]:

                recommendation = (
                    "⚠️ Advanced pose "
                    "(Not for beginners)"
                )

        # ---------- AGE ----------
        elif age and int(age) > 50:

            if pose in [

                "Natarajasana",

                "ArdhaChandrasana"
            ]:

                recommendation = (
                    "⚠️ Do carefully "
                    "(Balance pose)"
                )

            else:

                recommendation = (
                    "✅ Safe but go slow"
                )

    # ---------- RESPONSE ----------
    return jsonify({

        "pose": pose,

        "confidence": confidence,

        "recommendation": recommendation,

        "correction": correction
    })

# --------------------------
# IMAGE PREDICTION
# --------------------------
@app.route("/predict", methods=["POST"])
def predict():

    # ---------- CHECK FILE ----------
    if "file" not in request.files:

        return jsonify({
            "error": "No file uploaded"
        }), 400

    file = request.files["file"]

    if file.filename == "":

        return jsonify({
            "error": "Empty file"
        }), 400

    # ---------- UNIQUE FILE ----------
    filename = (
        f"temp_{uuid.uuid4().hex}.jpg"
    )

    upload_path = os.path.join(
        BASE_DIR,
        filename
    )

    # ---------- SAVE ----------
    file.save(upload_path)

    # ---------- PREDICT ----------
    pose, confidence = predict_image(
        upload_path
    )

    # ---------- DELETE TEMP ----------
    try:

        os.remove(upload_path)

        gc.collect()

    except:

        pass

    # ---------- RESPONSE ----------
    return jsonify({

        "pose": pose,

        "confidence": confidence
    })

# --------------------------
# RUN APP
# --------------------------
if __name__ == "__main__":

    app.run(

        debug=False,

        threaded=True
    )
