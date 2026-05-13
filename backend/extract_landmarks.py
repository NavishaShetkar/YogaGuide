import cv2
import mediapipe as mp
import os
import csv
import numpy as np

# ==========================================
# ANGLE CALCULATION
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
# MEDIAPIPE
# ==========================================
mp_pose = mp.solutions.pose

pose = mp_pose.Pose(

    static_image_mode=True,

    model_complexity=1,

    min_detection_confidence=0.5
)

# ==========================================
# PATHS
# ==========================================
BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

dataset_path = os.path.join(

    BASE_DIR,

    "cnn_model",

    "dataset"
)

output_file = os.path.join(

    BASE_DIR,

    "pose_dataset.csv"
)

data = []

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
# PROCESS DATASET
# ==========================================
for pose_name in os.listdir(dataset_path):

    pose_folder = os.path.join(

        dataset_path,

        pose_name
    )

    if not os.path.isdir(pose_folder):

        continue

    print(f"Processing pose: {pose_name}")

    for img_name in os.listdir(pose_folder):

        img_path = os.path.join(

            pose_folder,

            img_name
        )

        image = cv2.imread(img_path)

        if image is None:

            continue

        rgb = cv2.cvtColor(

            image,

            cv2.COLOR_BGR2RGB
        )

        results = pose.process(rgb)

        if results.pose_landmarks:

            lms = results.pose_landmarks.landmark

            # ======================================
            # VISIBILITY CHECK
            # ======================================
            visible = sum(

                1 for idx in selected_points

                if lms[idx].visibility > 0.5
            )

            if visible < 10:

                continue

            # ======================================
            # EXTRACT 3D LANDMARKS
            # ======================================
            landmarks = []

            for idx in selected_points:

                lm = lms[idx]

                landmarks.append(lm.x)

                landmarks.append(lm.y)

                landmarks.append(lm.z)

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
            # NORMALIZATION
            # ======================================
            landmarks_np = np.array(
                landmarks
            ).reshape(-1, 3)

            # HIP CENTER
            mid_hip_x = (
                lms[23].x + lms[24].x
            ) / 2

            mid_hip_y = (
                lms[23].y + lms[24].y
            ) / 2

            mid_hip_z = (
                lms[23].z + lms[24].z
            ) / 2

            # CENTER BODY
            landmarks_np[:, 0] -= mid_hip_x

            landmarks_np[:, 1] -= mid_hip_y

            landmarks_np[:, 2] -= mid_hip_z

            # SCALE BODY
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

                landmarks_np /= hip_width

            normalized = landmarks_np.flatten()

            # ======================================
            # FINAL FEATURES
            # ======================================
            # 14 landmarks × 3 = 42
            # 42 + 14 angles = 56

            row = (

                normalized.tolist()

                +

                angles

                +

                [pose_name]
            )

            data.append(row)

# ==========================================
# SAVE CSV
# ==========================================
with open(output_file, "w", newline="") as f:

    writer = csv.writer(f)

    header = []

    landmark_names = [

        "L_Shoulder",
        "R_Shoulder",

        "L_Elbow",
        "R_Elbow",

        "L_Wrist",
        "R_Wrist",

        "L_Hip",
        "R_Hip",

        "L_Knee",
        "R_Knee",

        "L_Ankle",
        "R_Ankle",

        "L_Foot",
        "R_Foot"
    ]

    # ======================================
    # 3D COORDINATE HEADERS
    # ======================================
    for name in landmark_names:

        header.append(f"{name}_x")

        header.append(f"{name}_y")

        header.append(f"{name}_z")

    # ======================================
    # ANGLE HEADERS
    # ======================================
    angle_labels = [

        "L_Elbow_Angle",
        "R_Elbow_Angle",

        "L_Knee_Angle",
        "R_Knee_Angle",

        "L_Hip_Angle",
        "R_Hip_Angle",

        "L_Shoulder_Angle",
        "Leg_Spread_Angle",

        "R_Shoulder_Angle",

        "L_Torso_Angle",
        "R_Torso_Angle",

        "L_Ankle_Angle",
        "R_Ankle_Angle",

        "Arm_Spread_Angle"
    ]

    header.extend(angle_labels)

    # ======================================
    # LABEL
    # ======================================
    header.append("pose")

    writer.writerow(header)

    writer.writerows(data)

print(

    f"Dataset saved with {len(data)} samples "

    f"and 56 features: {output_file}"
)
