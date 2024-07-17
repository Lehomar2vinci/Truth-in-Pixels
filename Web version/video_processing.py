import cv2
import numpy as np
import mediapipe as mp

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh()
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()


def apply_effects(frame, results_pose, results_face, results_hands, effect_settings):
    if results_pose and results_pose.pose_landmarks:
        frame = apply_pose_effects(
            frame, results_pose.pose_landmarks, effect_settings)

    if results_face and results_face.multi_face_landmarks:
        frame = apply_face_effects(
            frame, results_face.multi_face_landmarks, effect_settings)

    if results_hands and (results_hands.multi_hand_landmarks):
        frame = apply_hand_effects(
            frame, results_hands.multi_hand_landmarks, effect_settings)

    return frame


def apply_pose_effects(frame, landmarks, effect_settings):
    if "Deformation" in effect_settings["selected_effects"]:
        frame = apply_deformation(frame, landmarks, effect_settings)

    if "Mirror" in effect_settings["selected_effects"]:
        frame = apply_mirror_effect(frame, landmarks, effect_settings)

    if "Pointillism" in effect_settings["selected_effects"]:
        frame = apply_pointillism_effect(frame, landmarks, effect_settings)

    if "Sepia" in effect_settings["selected_effects"]:
        frame = apply_sepia_effect(frame)

    if "Cartoon" in effect_settings["selected_effects"]:
        frame = apply_cartoon_effect(frame)

    return frame


def apply_face_effects(frame, face_landmarks_list, effect_settings):
    if "Face Mask" in effect_settings["selected_effects"]:
        frame = apply_face_mask(frame, face_landmarks_list, effect_settings)

    return frame


def apply_hand_effects(frame, hand_landmarks_list, effect_settings):
    # Ajouter des effets spécifiques aux main
    for hand_landmarks in hand_landmarks_list:
        for point in hand_landmarks.landmark:
            x = int(point.x * frame.shape[1])
            y = int(point.y * frame.shape[0])
            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
    return frame


def apply_deformation(frame, landmarks, effect_settings):
    for idx in [mp_pose.PoseLandmark.LEFT_EYE.value, mp_pose.PoseLandmark.RIGHT_EYE.value, mp_pose.PoseLandmark.LEFT_WRIST.value, mp_pose.PoseLandmark.RIGHT_WRIST.value]:
        point = landmarks.landmark[idx]
        x = int(point.x * frame.shape[1])
        y = int(point.y * frame.shape[0])
        size = int(30 * effect_settings["deformation_intensity"])

        src_points = np.float32(
            [[x - size, y - size], [x + size, y - size], [x + size, y + size], [x - size, y + size]])
        dst_points = np.float32([[x - size, y - int(size * 1.5)], [x + size, y - int(
            size * 1.5)], [x + size, y + int(size * 1.5)], [x - size, y + int(size * 1.5)]])
        warped = warp_image(frame, src_points, dst_points)
        mask = np.zeros_like(frame)
        cv2.fillConvexPoly(mask, src_points.astype(int), (255, 255, 255))
        frame = cv2.bitwise_and(frame, cv2.bitwise_not(mask))
        frame = cv2.add(frame, cv2.bitwise_and(warped, mask))
    return frame


def warp_image(frame, src_points, dst_points):
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    warped = cv2.warpPerspective(
        frame, matrix, (frame.shape[1], frame.shape[0]))
    return warped


def apply_mirror_effect(frame, landmarks, effect_settings):
    for idx in [mp_pose.PoseLandmark.NOSE.value, mp_pose.PoseLandmark.MOUTH_LEFT.value, mp_pose.PoseLandmark.MOUTH_RIGHT.value]:
        point = landmarks.landmark[idx]
        x = int(point.x * frame.shape[1])
        y = int(point.y * frame.shape[0])
        size = 50

        left = max(x - size, 0)
        right = min(x + size, frame.shape[1])
        top = max(y - size, 0)
        bottom = min(y + size, frame.shape[0])

        if left < right and top < bottom:
            frame[top:bottom, left:right] = cv2.flip(
                frame[top:bottom, left:right], 1)
    return frame


def apply_pointillism_effect(frame, landmarks, effect_settings):
    output = np.zeros_like(frame)
    height, width, _ = frame.shape
    for idx in range(len(landmarks.landmark)):
        point = landmarks.landmark[idx]
        x = int(point.x * width)
        y = int(point.y * height)
        if 0 <= x < width and 0 <= y < height:
            color = frame[y, x]
            cv2.circle(output, (x, y),
                       effect_settings["pointillism_size"], color.tolist(), -1)
    return output


def apply_face_mask(frame, face_landmarks_list, effect_settings):
    for face_landmarks in face_landmarks_list:
        for point in face_landmarks.landmark:
            x = int(point.x * frame.shape[1])
            y = int(point.y * frame.shape[0])
            cv2.circle(frame, (x, y),
                       effect_settings["facemask_point_size"], (255, 0, 0), -1)
    return frame


def apply_color_filter(frame, intensity):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hsv[..., 1] = hsv[..., 1] * (intensity / 10.0)
    frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return frame


def apply_blur(frame, intensity):
    return cv2.GaussianBlur(frame, (intensity * 2 + 1, intensity * 2 + 1), 0)


def apply_vignette(frame, intensity):
    rows, cols = frame.shape[:2]
    kernel_x = cv2.getGaussianKernel(cols, cols / (intensity + 1))
    kernel_y = cv2.getGaussianKernel(rows, rows / (intensity + 1))
    kernel = kernel_y * kernel_x.T
    mask = 255 * kernel / np.linalg.norm(kernel)
    vignette = np.copy(frame)
    for i in range(3):
        vignette[:, :, i] = vignette[:, :, i] * mask
    return vignette


def apply_sepia_effect(frame):
    sepia_filter = np.array([[0.272, 0.534, 0.131],
                             [0.349, 0.686, 0.168],
                             [0.393, 0.769, 0.189]])
    sepia_frame = cv2.transform(frame, sepia_filter)
    sepia_frame = np.clip(sepia_frame, 0, 255)
    return sepia_frame


def apply_cartoon_effect(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 7)
    edges = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 10)
    color = cv2.bilateralFilter(frame, 9, 250, 250)
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    return cartoon


def update_effect_settings(effect_settings, data):
    for key, value in data.items():
        if key in effect_settings:
            effect_settings[key] = value
