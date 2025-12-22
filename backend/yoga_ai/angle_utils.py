import numpy as np
import mediapipe as mp

mp_pose = mp.solutions.pose


def calculate_angle(a, b, c):
    """
    Calculates angle between three points (a, b, c)
    Angle is at point 'b'
    """
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)

    angle = np.degrees(np.arccos(cosine_angle))
    return round(angle, 2)


def get_all_angles(landmarks):
    """
    Takes MediaPipe pose_landmarks and returns key joint angles.
    """

    lm = landmarks.landmark

    def p(id):
        return [lm[id].x, lm[id].y]

    angles = {
        # Arms
        "left_elbow": calculate_angle(p(mp_pose.PoseLandmark.LEFT_WRIST.value),
                                      p(mp_pose.PoseLandmark.LEFT_ELBOW.value),
                                      p(mp_pose.PoseLandmark.LEFT_SHOULDER.value)),

        "right_elbow": calculate_angle(p(mp_pose.PoseLandmark.RIGHT_WRIST.value),
                                       p(mp_pose.PoseLandmark.RIGHT_ELBOW.value),
                                       p(mp_pose.PoseLandmark.RIGHT_SHOULDER.value)),

        # Legs
        "left_knee": calculate_angle(p(mp_pose.PoseLandmark.LEFT_HIP.value),
                                     p(mp_pose.PoseLandmark.LEFT_KNEE.value),
                                     p(mp_pose.PoseLandmark.LEFT_ANKLE.value)),

        "right_knee": calculate_angle(p(mp_pose.PoseLandmark.RIGHT_HIP.value),
                                      p(mp_pose.PoseLandmark.RIGHT_KNEE.value),
                                      p(mp_pose.PoseLandmark.RIGHT_ANKLE.value)),

        # Shoulders
        "left_shoulder": calculate_angle(p(mp_pose.PoseLandmark.LEFT_ELBOW.value),
                                         p(mp_pose.PoseLandmark.LEFT_SHOULDER.value),
                                         p(mp_pose.PoseLandmark.LEFT_HIP.value)),

        "right_shoulder": calculate_angle(p(mp_pose.PoseLandmark.RIGHT_ELBOW.value),
                                          p(mp_pose.PoseLandmark.RIGHT_SHOULDER.value),
                                          p(mp_pose.PoseLandmark.RIGHT_HIP.value)),
    }

    return angles
