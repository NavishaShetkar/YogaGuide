import cv2
import numpy as np
import tensorflow as tf
import mediapipe as mp
import os
import joblib

# ---------- LOAD MODEL ----------
BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "pose_model.h5"
)

SCALER_PATH = os.path.join(
    BASE_DIR,
    "scaler.pkl"
)

model = tf.keras.models.load_model(
    MODEL_PATH,
    compile=False
)

scaler = joblib.load(
    SCALER_PATH
)

# ---------- LABELS ----------
classes = [

    "ArdhaChandrasana",
    "BaddhaKonasana",
    "Downward_dog",
    "Natarajasana",

    "Triangle",
    "UtkataKonasana",

    "Veerabhadrasana",
    "Vrukshasana",

    "NoPose"
]

# ---------- CONFIDENCE ----------
CONFIDENCE_THRESHOLD = 70

# ---------- MEDIAPIPE ----------
mp_pose = mp.solutions.pose

pose = mp_pose.Pose(

    static_image_mode=True,

    model_complexity=0,

    smooth_landmarks=True,

    min_detection_confidence=0.5
)

# ---------- IMPORTANT BODY POINTS ----------
selected_points = [

    11, 12,
    13, 14,
    15, 16,

    23, 24,
    25, 26,
    27, 28
]

# ---------- ANGLE FUNCTION ----------
def calculate_angle(a, b, c):

    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = (

        np.arctan2(
            c[1]-b[1],
            c[0]-b[0]
        )

        -

        np.arctan2(
            a[1]-b[1],
            a[0]-b[0]
        )
    )

    angle = np.abs(
        radians * 180.0 / np.pi
    )

    if angle > 180:
        angle = 360 - angle

    return angle

# ---------- NORMALIZATION ----------
def normalize_landmarks(
    landmarks_raw,
    lms
):

    landmarks = np.array(
        landmarks_raw
    ).reshape(-1, 3)

    # hip center
    mid_hip_x = (
        lms[23].x + lms[24].x
    ) / 2

    mid_hip_y = (
        lms[23].y + lms[24].y
    ) / 2

    mid_hip_z = (
        lms[23].z + lms[24].z
    ) / 2

    landmarks[:, 0] -= mid_hip_x
    landmarks[:, 1] -= mid_hip_y
    landmarks[:, 2] -= mid_hip_z

    # body scale
    hip_width = np.linalg.norm(

        np.array([
            lms[23].x,
            lms[23].y,
            lms[23].z
        ])

        -

        np.array([
            lms[24].x,
            lms[24].y,
            lms[24].z
        ])
    )

    if hip_width > 0:
        landmarks /= hip_width

    return landmarks.flatten()

# ---------- PREDICT ----------
def predict_image(img_path):

    img = cv2.imread(img_path)

    if img is None:
        return "Invalid Image", 0.0

    img_rgb = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2RGB
    )

    results = pose.process(img_rgb)

    if not results.pose_landmarks:
        return "No Pose Detected", 0.0

    lms = results.pose_landmarks.landmark

    # ---------- VISIBILITY CHECK ----------
    visible_points = sum(

        1 for idx in selected_points

        if lms[idx].visibility > 0.5
    )

    if visible_points < 10:
        return "Show Full Body", 0.0

    # ---------- EXTRACT 3D LANDMARKS ----------
    landmarks_raw = []

    for idx in selected_points:

        lm = lms[idx]

        landmarks_raw.extend([
            lm.x,
            lm.y,
            lm.z
        ])

    # 12 landmarks × 3 coords
    if len(landmarks_raw) != 36:
        return "Pose Not Clear", 0.0

    # ---------- NORMALIZATION ----------
    normalized = normalize_landmarks(
        landmarks_raw,
        lms
    )

    # ---------- ANGLES ----------
    angles = [

        # Left elbow
        calculate_angle(
            [lms[11].x, lms[11].y],
            [lms[13].x, lms[13].y],
            [lms[15].x, lms[15].y]
        ),

        # Right elbow
        calculate_angle(
            [lms[12].x, lms[12].y],
            [lms[14].x, lms[14].y],
            [lms[16].x, lms[16].y]
        ),

        # Left knee
        calculate_angle(
            [lms[23].x, lms[23].y],
            [lms[25].x, lms[25].y],
            [lms[27].x, lms[27].y]
        ),

        # Right knee
        calculate_angle(
            [lms[24].x, lms[24].y],
            [lms[26].x, lms[26].y],
            [lms[28].x, lms[28].y]
        ),

        # Left hip
        calculate_angle(
            [lms[11].x, lms[11].y],
            [lms[23].x, lms[23].y],
            [lms[25].x, lms[25].y]
        ),

        # Right hip
        calculate_angle(
            [lms[12].x, lms[12].y],
            [lms[24].x, lms[24].y],
            [lms[26].x, lms[26].y]
        ),

        # Left shoulder
        calculate_angle(
            [lms[13].x, lms[13].y],
            [lms[11].x, lms[11].y],
            [lms[23].x, lms[23].y]
        ),

        # Leg spread
        calculate_angle(

            [lms[27].x, lms[27].y],

            [
                (
                    lms[23].x +
                    lms[24].x
                ) / 2,

                (
                    lms[23].y +
                    lms[24].y
                ) / 2
            ],

            [lms[28].x, lms[28].y]
        )
    ]

    # ---------- FINAL FEATURES ----------
    final_features = np.concatenate([
        normalized,
        angles
    ])

    processed_input = np.array(
        final_features
    ).reshape(1, 44)

    # ---------- SCALE ----------
    processed_input = scaler.transform(
        processed_input
    )

    # ---------- PREDICT ----------
    prediction = model.predict(
        processed_input,
        verbose=0
    )

    class_index = np.argmax(
        prediction
    )

    confidence = float(
        prediction[0][class_index] * 100
    )

    # ---------- RESULT ----------
    if confidence >= CONFIDENCE_THRESHOLD:

        pose_name = classes[class_index]

    else:

        pose_name = "No Pose Detected"

        confidence = 0

    return pose_name, round(confidence, 2)