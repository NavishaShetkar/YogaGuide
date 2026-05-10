import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
import os
import joblib
import time
import gc

# ==========================================
# GPU MEMORY FIX
# ==========================================
gpus = tf.config.experimental.list_physical_devices('GPU')

if gpus:

    try:

        for gpu in gpus:

            tf.config.experimental.set_memory_growth(
                gpu,
                True
            )

    except RuntimeError as e:

        print(f"GPU Error: {e}")

# ==========================================
# GLOBAL VARIABLES
# ==========================================
latest_pose = "Detecting..."

latest_confidence = 0

correction_message = ""

last_pose = ""

pose_counter = 0

missing_frames = 0

# ==========================================
# LOAD MODEL
# ==========================================
BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "cnn_model",
    "pose_model.h5"
)

SCALER_PATH = os.path.join(
    BASE_DIR,
    "cnn_model",
    "scaler.pkl"
)

model = None
scaler = None

try:

    model = tf.keras.models.load_model(
        MODEL_PATH,
        compile=False
    )

    scaler = joblib.load(
        SCALER_PATH
    )

    print("Model loaded successfully")

    print("Scaler loaded successfully")

except Exception as e:

    print(f"Error loading model/scaler: {e}")

# ==========================================
# LABELS
# ==========================================
labels = [

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

# ==========================================
# MEDIAPIPE
# ==========================================
mp_pose = mp.solutions.pose

mp_draw = mp.solutions.drawing_utils

pose_detector = mp_pose.Pose(

    static_image_mode=False,

    model_complexity=0,

    smooth_landmarks=True,

    enable_segmentation=False,

    min_detection_confidence=0.6,

    min_tracking_confidence=0.6
)

# ==========================================
# IMPORTANT BODY LANDMARKS
# ==========================================
selected_points = [

    0,

    11, 12,

    13, 14,

    15, 16,

    23, 24,

    25, 26,

    27, 28,

    29, 30,

    31, 32
]

# ==========================================
# ANGLE FUNCTION
# ==========================================
def calculate_angle(a, b, c):

    a = np.array(a)

    b = np.array(b)

    c = np.array(c)

    radians = (

        np.arctan2(
            c[1] - b[1],
            c[0] - b[0]
        )

        -

        np.arctan2(
            a[1] - b[1],
            a[0] - b[0]
        )
    )

    angle = np.abs(
        radians * 180.0 / np.pi
    )

    if angle > 180:

        angle = 360 - angle

    return angle

# ==========================================
# NORMALIZATION
# ==========================================
def normalize_landmarks(
    landmarks_raw,
    lms
):

    landmarks = np.array(
        landmarks_raw
    ).reshape(-1, 3)

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

# ==========================================
# POSTURE CORRECTION
# ==========================================
def get_pose_correction(
    pose_name,
    angles
):

    correction = ""

    left_knee = angles[2]

    right_knee = angles[3]

    shoulder = angles[6]

    leg_spread = angles[7]

    knee_symmetry = angles[11]

    # ======================================
    # GODDESS
    # ======================================
    if pose_name == "UtkataKonasana":

        if knee_symmetry > 25:

            correction = (
                "Keep both knees equally bent"
            )

        elif left_knee > 120 or right_knee > 120:

            correction = "Bend your knees more"

        elif leg_spread < 90:

            correction = "Spread legs wider"

        else:

            correction = "Good posture"

    # ======================================
    # WARRIOR
    # ======================================
    elif pose_name == "Veerabhadrasana":

        if knee_symmetry < 15:

            correction = (
                "One knee should bend more"
            )

        elif shoulder < 150:

            correction = (
                "Raise arms straighter"
            )

        else:

            correction = "Good posture"

    # ======================================
    # TRIANGLE
    # ======================================
    elif pose_name == "Triangle":

        if shoulder < 140:

            correction = "Raise upper arm"

        else:

            correction = "Good posture"

    # ======================================
    # TREE
    # ======================================
    elif pose_name == "Vrukshasana":

        if left_knee > 160 and right_knee > 160:

            correction = (
                "Lift one leg higher"
            )

        else:

            correction = "Good posture"

    return correction

# ==========================================
# WEBCAM
# ==========================================
def generate_frames():

    global latest_pose

    global latest_confidence

    global correction_message

    global last_pose

    global pose_counter

    global missing_frames

    if model is None:

        print("Model not loaded")

        return

    cap = cv2.VideoCapture(0)

    # ======================================
    # CAMERA OPTIMIZATION
    # ======================================
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    cap.set(cv2.CAP_PROP_FPS, 30)

    CONFIDENCE_THRESHOLD = 75

    STABLE_FRAMES = 4

    frame_count = 0

    try:

        while True:

            try:

                success, frame = cap.read()

                # ======================================
                # CAMERA RECONNECT
                # ======================================
                if not success:

                    print("Reconnecting camera...")

                    cap.release()

                    time.sleep(1)

                    cap = cv2.VideoCapture(0)

                    continue

                frame_count += 1

                # MIRROR
                frame = cv2.flip(frame, 1)

                # ======================================
                # REDUCE CPU LOAD
                # ======================================
                small_frame = cv2.resize(
                    frame,
                    (320, 240)
                )

                rgb = cv2.cvtColor(
                    small_frame,
                    cv2.COLOR_BGR2RGB
                )

                rgb.flags.writeable = False

                results = pose_detector.process(rgb)

                rgb.flags.writeable = True

                # ======================================
                # PROCESS EVERY 5 FRAMES
                # ======================================
                if (
                    results.pose_landmarks
                    and
                    frame_count % 5 == 0
                ):

                    lms = results.pose_landmarks.landmark

                    # ======================================
                    # DRAW SKELETON
                    # ======================================
                    mp_draw.draw_landmarks(

                        frame,

                        results.pose_landmarks,

                        mp_pose.POSE_CONNECTIONS,

                        mp_draw.DrawingSpec(
                            color=(245,117,66),
                            thickness=2,
                            circle_radius=2
                        ),

                        mp_draw.DrawingSpec(
                            color=(245,66,230),
                            thickness=2,
                            circle_radius=2
                        )
                    )

                    # ======================================
                    # VISIBILITY CHECK
                    # ======================================
                    visible_points = sum(

                        1 for idx in selected_points

                        if lms[idx].visibility > 0.55
                    )

                    if visible_points < 12:

                        missing_frames += 1

                        if missing_frames > 20:

                            latest_pose = (
                                "Show Full Body"
                            )

                            correction_message = ""

                            pose_counter = 0

                    else:

                        # ======================================
                        # EXTRACT LANDMARKS
                        # ======================================
                        landmarks_raw = []

                        for idx in selected_points:

                            lm = lms[idx]

                            landmarks_raw.extend([
                                lm.x,
                                lm.y,
                                lm.z
                            ])

                        # 17 landmarks × 3
                        if len(landmarks_raw) == 51:

                            # NORMALIZE
                            normalized = normalize_landmarks(
                                landmarks_raw,
                                lms
                            )

                            # ======================================
                            # ANGLES
                            # ======================================
                            angles = [

                                calculate_angle(
                                    [lms[11].x, lms[11].y],
                                    [lms[13].x, lms[13].y],
                                    [lms[15].x, lms[15].y]
                                ),

                                calculate_angle(
                                    [lms[12].x, lms[12].y],
                                    [lms[14].x, lms[14].y],
                                    [lms[16].x, lms[16].y]
                                ),

                                calculate_angle(
                                    [lms[23].x, lms[23].y],
                                    [lms[25].x, lms[25].y],
                                    [lms[27].x, lms[27].y]
                                ),

                                calculate_angle(
                                    [lms[24].x, lms[24].y],
                                    [lms[26].x, lms[26].y],
                                    [lms[28].x, lms[28].y]
                                ),

                                calculate_angle(
                                    [lms[11].x, lms[11].y],
                                    [lms[23].x, lms[23].y],
                                    [lms[25].x, lms[25].y]
                                ),

                                calculate_angle(
                                    [lms[12].x, lms[12].y],
                                    [lms[24].x, lms[24].y],
                                    [lms[26].x, lms[26].y]
                                ),

                                calculate_angle(
                                    [lms[13].x, lms[13].y],
                                    [lms[11].x, lms[11].y],
                                    [lms[23].x, lms[23].y]
                                ),

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
                                ),

                                calculate_angle(
                                    [lms[14].x, lms[14].y],
                                    [lms[12].x, lms[12].y],
                                    [lms[24].x, lms[24].y]
                                ),

                                calculate_angle(
                                    [lms[11].x, lms[11].y],
                                    [lms[15].x, lms[15].y],
                                    [lms[27].x, lms[27].y]
                                ),

                                calculate_angle(
                                    [lms[12].x, lms[12].y],
                                    [lms[16].x, lms[16].y],
                                    [lms[28].x, lms[28].y]
                                ),

                                abs(

                                    calculate_angle(
                                        [lms[23].x, lms[23].y],
                                        [lms[25].x, lms[25].y],
                                        [lms[27].x, lms[27].y]
                                    )

                                    -

                                    calculate_angle(
                                        [lms[24].x, lms[24].y],
                                        [lms[26].x, lms[26].y],
                                        [lms[28].x, lms[28].y]
                                    )
                                )
                            ]

                            # ======================================
                            # FINAL FEATURES
                            # ======================================
                            final_features = np.concatenate([
                                normalized,
                                angles
                            ])

                            processed_input = np.array(
                                final_features
                            ).reshape(
                                1,
                                len(final_features)
                            )

                            # SCALE
                            processed_input = scaler.transform(
                                processed_input
                            )

                            # ======================================
                            # PREDICT
                            # ======================================
                            prediction = model.predict(
                                processed_input,
                                verbose=0
                            )

                            class_id = np.argmax(
                                prediction
                            )

                            current_conf = float(
                                prediction[0][class_id] * 100
                            )

                            latest_confidence = round(
                                current_conf,
                                2
                            )

                            predicted_label = labels[class_id]

                            # ======================================
                            # FILTER
                            # ======================================
                            if (
                                predicted_label == "NoPose"
                                or
                                current_conf < CONFIDENCE_THRESHOLD
                            ):

                                pose_counter = 0

                                missing_frames += 1

                                if missing_frames > 20:

                                    latest_pose = (
                                        "Detecting..."
                                    )

                                    correction_message = ""

                            else:

                                if predicted_label == last_pose:

                                    pose_counter += 1

                                else:

                                    last_pose = predicted_label

                                    pose_counter = 1

                                missing_frames = 0

                                if pose_counter >= STABLE_FRAMES:

                                    latest_pose = predicted_label

                                    correction_message = get_pose_correction(
                                        predicted_label,
                                        angles
                                    )

                # ======================================
                # MEMORY CLEANUP
                # ======================================
                if frame_count % 100 == 0:

                    gc.collect()

                # ======================================
                # STREAM
                # ======================================
                ret, buffer = cv2.imencode(
                    '.jpg',
                    frame,
                    [
                        int(cv2.IMWRITE_JPEG_QUALITY),
                        50
                    ]
                )

                yield (

                    b'--frame\r\n'

                    b'Content-Type: image/jpeg\r\n\r\n'

                    + buffer.tobytes()

                    + b'\r\n'
                )

            except Exception as e:

                print(f"Frame Error: {e}")

                continue

    finally:

        cap.release()

        gc.collect()