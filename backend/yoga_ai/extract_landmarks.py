import cv2
import mediapipe as mp
import os
import json

# Paths
DATASET_DIR = "dataset"
LANDMARK_DIR = "landmarks"

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True, model_complexity=2)

def extract_landmarks_from_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return None
    
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    result = pose.process(image_rgb)
    if not result.pose_landmarks:
        return None

    landmarks = []
    for lm in result.pose_landmarks.landmark:
        landmarks.append({
            "x": lm.x,
            "y": lm.y,
            "z": lm.z,
            "visibility": lm.visibility
        })

    return landmarks


def process_all_images():
    # Loop through each pose folder inside dataset/
    for pose_name in os.listdir(DATASET_DIR):
        pose_folder = os.path.join(DATASET_DIR, pose_name)

        if not os.path.isdir(pose_folder):
            continue

        # Make output folder
        output_folder = os.path.join(LANDMARK_DIR, pose_name)
        os.makedirs(output_folder, exist_ok=True)

        print(f"Processing pose: {pose_name}")

        # Loop through each image
        for img_name in os.listdir(pose_folder):
            img_path = os.path.join(pose_folder, img_name)
            
            landmarks = extract_landmarks_from_image(img_path)
            if landmarks is None:
                print("  ❌ No landmarks:", img_name)
                continue

            # Save JSON
            json_path = os.path.join(output_folder, img_name.replace(".jpg", ".json"))
            with open(json_path, "w") as f:
                json.dump(landmarks, f)

            print("  ✔ Saved:", json_path)


if __name__ == "__main__":
    process_all_images()