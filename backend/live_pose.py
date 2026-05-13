import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
import os
import joblib
import time
import gc
import pyttsx3
import threading

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
# VOICE FEEDBACK
# ==========================================
engine = pyttsx3.init()

engine.setProperty('rate', 145)

engine.setProperty('volume', 1.0)

voices = engine.getProperty('voices')

if len(voices) > 1:

    engine.setProperty(
        'voice',
        voices[1].id
    )

last_speak_time = 0

VOICE_COOLDOWN = 4

is_speaking = False

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

    model_complexity=1,

    smooth_landmarks=True,

    enable_segmentation=False,

    min_detection_confidence=0.5,

    min_tracking_confidence=0.5
)

# ==========================================
# IMPORTANT BODY LANDMARKS
# ==========================================
selected_points = [

    11, 12,   # shoulders

    13, 14,   # elbows

    15, 16,   # wrists

    23, 24,   # hips

    25, 26,   # knees

    27, 28,   # ankles

    31, 32    # foot index
]

# ==========================================
# SAFE SPEAK FUNCTION
# ==========================================
def speak_correction(message):

    global is_speaking

    try:

        is_speaking = True

        engine.say(message)

        engine.runAndWait()

    except Exception as e:

        print(f"Voice Error: {e}")

    finally:

        is_speaking = False

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

    left_shoulder = angles[6]

    right_shoulder = angles[8]

    leg_spread = angles[7]

    torso_left = angles[9]

    torso_right = angles[10]

    # ======================================
    # GODDESS
    # ======================================
    if pose_name == "UtkataKonasana":

        if abs(left_knee - right_knee) > 25:

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

        if abs(left_knee - right_knee) < 15:

            correction = (
                "Bend your front knee more"
            )

        elif left_shoulder < 145:

            correction = (
                "Raise your arms straighter"
            )

        else:

            correction = "Good posture"

    # ======================================
    # TRIANGLE
    # ======================================
    elif pose_name == "Triangle":

        if torso_left < 145 or torso_right < 145:

            correction = (
                "Lean your body sideways more"
            )

        elif right_shoulder < 140:

            correction = (
                "Raise your upper arm"
            )

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

    global last_speak_time

    if model is None:

        print("Model not loaded")

        return

    cap = cv2.VideoCapture(0)

    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    cap.set(cv2.CAP_PROP_FPS, 30)

    CONFIDENCE_THRESHOLD = 90

    STABLE_FRAMES = 4

    frame_count = 0

    try:

        while True:

            try:

                success, frame = cap.read()

                if not success:

                    print("Reconnecting camera...")

                    cap.release()

                    time.sleep(1)

                    cap = cv2.VideoCapture(0)

                    continue

                frame_count += 1

                frame = cv2.flip(frame, 1)

                # ======================================
                # SMALLER FRAME FOR SPEED
                # ======================================
                small_frame = cv2.resize(
                    frame,
                    (640, 480)
                )

                rgb = cv2.cvtColor(
                    small_frame,
                    cv2.COLOR_BGR2RGB
                )

                rgb.flags.writeable = False

                results = pose_detector.process(rgb)

                rgb.flags.writeable = True

                # ======================================
                # PROCESS EVERY 3 FRAMES
                # ======================================
                if (
                    results.pose_landmarks
                    and
                    frame_count % 3 == 0
                ):

                    lms = results.pose_landmarks.landmark

                    # ======================================
                    # DRAW LANDMARKS
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

                        if lms[idx].visibility > 0.3
                    )

                    if visible_points < 6:

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

                        # 14 landmarks × 3 = 42
                        if len(landmarks_raw) == 42:

                            normalized = normalize_landmarks(
                                landmarks_raw,
                                lms
                            )

                            # ======================================
                            # ANGLES
                            # ======================================
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
                                ),

                                # Right shoulder
                                calculate_angle(
                                    [lms[14].x, lms[14].y],
                                    [lms[12].x, lms[12].y],
                                    [lms[24].x, lms[24].y]
                                ),

                                # Left torso
                                calculate_angle(
                                    [lms[11].x, lms[11].y],
                                    [lms[23].x, lms[23].y],
                                    [lms[27].x, lms[27].y]
                                ),

                                # Right torso
                                calculate_angle(
                                    [lms[12].x, lms[12].y],
                                    [lms[24].x, lms[24].y],
                                    [lms[28].x, lms[28].y]
                                ),

                                # Left ankle
                                calculate_angle(
                                    [lms[25].x, lms[25].y],
                                    [lms[27].x, lms[27].y],
                                    [lms[31].x, lms[31].y]
                                ),

                                # Right ankle
                                calculate_angle(
                                    [lms[26].x, lms[26].y],
                                    [lms[28].x, lms[28].y],
                                    [lms[32].x, lms[32].y]
                                ),

                                # Arm spread
                                calculate_angle(
                                    [lms[15].x, lms[15].y],

                                    [
                                        (
                                            lms[11].x +
                                            lms[12].x
                                        ) / 2,

                                        (
                                            lms[11].y +
                                            lms[12].y
                                        ) / 2
                                    ],

                                    [lms[16].x, lms[16].y]
                                )
                            ]

                            # ======================================
                            # FINAL FEATURES
                            # ======================================
                            final_features = np.concatenate([
                                normalized,
                                angles
                            ])

                            # 42 + 14 = 56
                            processed_input = np.array(
                                final_features
                            ).reshape(
                                1,
                                56
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
                                    # SAFE VOICE FEEDBACK
                                    # ======================================
                                    current_time = time.time()

                                    should_speak = (

                                        correction_message != ""

                                        and

                                        correction_message != "Good posture"

                                        and

                                        not is_speaking

                                        and

                                        current_time - last_speak_time
                                        > VOICE_COOLDOWN
                                    )

                                    if should_speak:

                                        last_speak_time = current_time

                                        threading.Thread(

                                            target=speak_correction,

                                            args=(correction_message,),

                                            daemon=True

                                        ).start()

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
                        55
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
