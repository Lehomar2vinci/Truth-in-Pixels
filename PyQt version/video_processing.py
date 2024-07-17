from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
import mediapipe as mp
import cv2


# Initialiser la détection des membres avec Mediapipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh()
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic()


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    recording_status_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._run_flag = True
        self.is_recording = False
        self.selected_effects = []
        self.deformation_intensity = 1.0
        self.pointillism_size = 2
        self.facemask_point_size = 5
        self.mirror_intensity = 1
        self.brightness = 0
        self.contrast = 0
        self.out = None
        self.cap = cv2.VideoCapture(0)
        self.drawing = False
        self.draw_color = (0, 255, 0)  # Green color for drawing
        self.draw_thickness = 5
        self.previous_point = None

    def run(self):
        while self._run_flag:
            ret, frame = self.cap.read()
            if not ret:
                continue

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = holistic.process(rgb_frame)
            frame = self.apply_effects(frame, results)

            if self.drawing:
                self.draw_with_hand(frame, results)

            if self.is_recording and self.out:
                self.out.write(frame)

            self.change_pixmap_signal.emit(frame)

    def stop(self):
        self._run_flag = False
        self.cap.release()
        if self.out:
            self.out.release()
        self.quit()
        self.wait()

    def start_recording(self, filename):
        self.is_recording = True
        self.out = cv2.VideoWriter(
            filename, cv2.VideoWriter_fourcc(*'XVID'), 20.0, (640, 480))
        self.recording_status_signal.emit(True)

    def stop_recording(self):
        self.is_recording = False
        if self.out:
            self.out.release()
            self.out = None
        self.recording_status_signal.emit(False)

    def apply_effects(self, frame, results):
        for effect in self.selected_effects:
            if effect == "Deformation":
                frame = self.apply_deformation(frame, results.pose_landmarks)
            elif effect == "Mirror":
                frame = self.apply_mirror_effect(frame, results.pose_landmarks)
            elif effect == "Color Change":
                frame = self.change_color(frame, results.pose_landmarks)
            elif effect == "Fun Filters":
                frame = self.add_fun_filters(frame, results.pose_landmarks)
            elif effect == "Bubble":
                frame = self.add_bubble_effect(frame, results.pose_landmarks)
            elif effect == "Wave":
                frame = self.add_wave_effect(frame, results.pose_landmarks)
            elif effect == "Pointillism":
                frame = self.apply_pointillism_effect(
                    frame, results.pose_landmarks)
            elif effect == "Face Morphing" and results.face_landmarks:
                frame = self.apply_face_morphing(frame, results.face_landmarks)
            elif effect == "Rainbow":
                frame = self.apply_rainbow_effect(frame)
            elif effect == "Glitch":
                frame = self.apply_glitch_effect(frame)
            elif effect == "Hand Tracking" and (results.left_hand_landmarks or results.right_hand_landmarks):
                frame = self.apply_hand_tracking_effect(frame, results)
            elif effect == "Background Distortion":
                frame = self.apply_background_distortion(
                    frame, results.pose_landmarks)
            elif effect == "Face Mask" and results.face_landmarks:
                frame = self.apply_face_mask(frame, results.face_landmarks)
        frame = self.adjust_brightness_contrast(frame)
        return frame

    def apply_deformation(self, frame, landmarks):
        if landmarks:
            for idx in [mp_pose.PoseLandmark.LEFT_EYE.value, mp_pose.PoseLandmark.RIGHT_EYE.value, mp_pose.PoseLandmark.LEFT_WRIST.value, mp_pose.PoseLandmark.RIGHT_WRIST.value]:
                point = landmarks.landmark[idx]
                x = int(point.x * frame.shape[1])
                y = int(point.y * frame.shape[0])
                size = int(30 * self.deformation_intensity)

                src_points = np.float32(
                    [[x - size, y - size], [x + size, y - size], [x + size, y + size], [x - size, y + size]])
                dst_points = np.float32([[x - size, y - int(size * 1.5)], [x + size, y - int(
                    size * 1.5)], [x + size, y + int(size * 1.5)], [x - size, y + int(size * 1.5)]])
                warped = self.warp_image(frame, src_points, dst_points)
                mask = np.zeros_like(frame)
                cv2.fillConvexPoly(
                    mask, src_points.astype(int), (255, 255, 255))
                frame = cv2.bitwise_and(frame, cv2.bitwise_not(mask))
                frame = cv2.add(frame, cv2.bitwise_and(warped, mask))
        return frame

    def warp_image(self, frame, src_points, dst_points):
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        warped = cv2.warpPerspective(
            frame, matrix, (frame.shape[1], frame.shape[0]))
        return warped

    def apply_mirror_effect(self, frame, landmarks):
        if landmarks:
            for idx in [mp_pose.PoseLandmark.NOSE.value, mp_pose.PoseLandmark.MOUTH_LEFT.value, mp_pose.PoseLandmark.MOUTH_RIGHT.value]:
                point = landmarks.landmark[idx]
                x = int(point.x * frame.shape[1])
                y = int(point.y * frame.shape[0])
                size = 100 * self.mirror_intensity  # Augmenter l'intensité de l'effet miroir

                left = max(x - size, 0)
                right = min(x + size, frame.shape[1])
                top = max(y - size, 0)
                bottom = min(y + size, frame.shape[0])

                if left < right and top < bottom:
                    frame[top:bottom, left:right] = cv2.flip(
                        frame[top:bottom, left:right], 1)

        return frame

    def change_color(self, frame, landmarks):
        if landmarks:
            for idx in [mp_pose.PoseLandmark.LEFT_WRIST.value, mp_pose.PoseLandmark.RIGHT_WRIST.value]:
                point = landmarks.landmark[idx]
                x = int(point.x * frame.shape[1])
                y = int(point.y * frame.shape[0])
                size = 30

                left = max(x - size, 0)
                right = min(x + size, frame.shape[1])
                top = max(y - size, 0)
                bottom = min(y + size, frame.shape[0])

                if left < right and top < bottom:
                    frame[top:bottom, left:right] = cv2.applyColorMap(
                        frame[top:bottom, left:right], cv2.COLORMAP_JET)

        return frame

    def add_fun_filters(self, frame, landmarks):
        if landmarks:
            nose = landmarks.landmark[mp_pose.PoseLandmark.NOSE.value]
            left_eye = landmarks.landmark[mp_pose.PoseLandmark.LEFT_EYE.value]
            right_eye = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_EYE.value]
            mouth_left = landmarks.landmark[mp_pose.PoseLandmark.MOUTH_LEFT.value]
            mouth_right = landmarks.landmark[mp_pose.PoseLandmark.MOUTH_RIGHT.value]

            _ = int(nose.x * frame.shape[1])
            _ = int(nose.y * frame.shape[0])
            left_eye_x = int(left_eye.x * frame.shape[1])
            left_eye_y = int(left_eye.y * frame.shape[0])
            right_eye_x = int(right_eye.x * frame.shape[1])
            right_eye_y = int(right_eye.y * frame.shape[0])
            mouth_left_x = int(mouth_left.x * frame.shape[1])
            mouth_left_y = int(mouth_left.y * frame.shape[0])
            mouth_right_x = int(mouth_right.x * frame.shape[1])
            mouth_right_y = int(mouth_right.y * frame.shape[0])

            cv2.line(frame, (left_eye_x - 20, left_eye_y),
                    (right_eye_x + 20, right_eye_y), (0, 0, 0), 5)
            cv2.circle(frame, (left_eye_x, left_eye_y), 30, (0, 0, 0), 5)
            cv2.circle(frame, (right_eye_x, right_eye_y), 30, (0, 0, 0), 5)

            cv2.line(frame, (mouth_left_x, mouth_left_y + 10),
                    (mouth_right_x, mouth_right_y + 10), (0, 0, 0), 10)
            cv2.line(frame, (mouth_left_x - 10, mouth_left_y + 20),
                    (mouth_right_x + 10, mouth_right_y + 20), (0, 0, 0), 10)

        return frame

    def add_bubble_effect(self, frame, landmarks):
        if landmarks:
            for idx in [mp_pose.PoseLandmark.LEFT_EYE.value, mp_pose.PoseLandmark.RIGHT_EYE.value, mp_pose.PoseLandmark.NOSE.value, mp_pose.PoseLandmark.MOUTH_LEFT.value, mp_pose.PoseLandmark.MOUTH_RIGHT.value]:
                point = landmarks.landmark[idx]
                x = int(point.x * frame.shape[1])
                y = int(point.y * frame.shape[0])
                radius = 30

                cv2.circle(frame, (x, y), radius, (255, 255, 255), 3)

        return frame

    def add_wave_effect(self, frame, landmarks):
        if landmarks:
            for idx in [mp_pose.PoseLandmark.LEFT_WRIST.value, mp_pose.PoseLandmark.RIGHT_WRIST.value, mp_pose.PoseLandmark.LEFT_KNEE.value, mp_pose.PoseLandmark.RIGHT_KNEE.value]:
                point = landmarks.landmark[idx]
                x = int(point.x * frame.shape[1])
                y = int(point.y * frame.shape[0])
                size = 30

                rng = np.random.default_rng(seed=42)
                for i in rng.integers(1, 6, size=5):
                    cv2.circle(frame, (x, y), size + i * 5, (0, 255, 255), 2)

        return frame

    def apply_pointillism_effect(self, frame, landmarks):
        if landmarks:
            output = np.zeros_like(frame)
            height, width, _ = frame.shape
            for idx in range(len(landmarks.landmark)):
                point = landmarks.landmark[idx]
                x = int(point.x * width)
                y = int(point.y * height)
                if 0 <= x < width and 0 <= y < height:
                    color = frame[y, x]
                    cv2.circle(output, (x, y), self.pointillism_size,
                            color.tolist(), -1)
            return output
        return frame

    def apply_face_morphing(self, frame, face_landmarks):
        if face_landmarks:
            for point in face_landmarks.landmark:
                x = int(point.x * frame.shape[1])
                y = int(point.y * frame.shape[0])
                frame[y:y+3, x:x+3] = (0, 255, 0)
        return frame

    def apply_rainbow_effect(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hsv[..., 0] = (hsv[..., 0] + 10) % 180
        frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        return frame

    def apply_glitch_effect(self, frame):
        height, width, _ = frame.shape
        glitch_frame = np.copy(frame)
        for i in range(0, height, 4):
            glitch_frame[i:i+4, :] = np.roll(frame[i:i+4, :],
                                            np.random.randint(-10, 10), axis=1)
        return glitch_frame

    def apply_hand_tracking_effect(self, frame, results):
        if results.left_hand_landmarks:
            frame = self.draw_hand_landmarks(
                frame, results.left_hand_landmarks)
        if results.right_hand_landmarks:
            frame = self.draw_hand_landmarks(
                frame, results.right_hand_landmarks)
        return frame

    def draw_hand_landmarks(self, frame, hand_landmarks):
        for point in hand_landmarks.landmark:
            x = int(point.x * frame.shape[1])
            y = int(point.y * frame.shape[0])
            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
        return frame

    def apply_background_distortion(self, frame, landmarks):
        if landmarks:
            mask = np.zeros(frame.shape[:2], dtype=np.uint8)
            for idx in range(len(landmarks.landmark)):
                point = landmarks.landmark[idx]
                x = int(point.x * frame.shape[1])
                y = int(point.y * frame.shape[0])
                cv2.circle(mask, (x, y), 15, 255, -1)
            dist_frame = cv2.GaussianBlur(frame, (99, 99), 30)
            frame = np.where(mask[..., None] == 255, frame, dist_frame)
        return frame

    def apply_face_mask(self, frame, face_landmarks):
        if face_landmarks:
            for point in face_landmarks.landmark:
                x = int(point.x * frame.shape[1])
                y = int(point.y * frame.shape[0])
                cv2.circle(frame, (x, y), self.facemask_point_size,
                           (255, 0, 0), -1)
        return frame

    def adjust_brightness_contrast(self, frame):
        brightness = self.brightness
        contrast = self.contrast
        if brightness != 0:
            shadow = brightness if brightness > 0 else 0
            highlight = 255 if brightness > 0 else 255 + brightness
            alpha_b = (highlight - shadow) / 255
            gamma_b = shadow
            frame = cv2.addWeighted(frame, alpha_b, frame, 0, gamma_b)

        if contrast != 0:
            f = 131 * (contrast + 127) / (127 * (131 - contrast))
            alpha_c = f
            gamma_c = 127 * (1 - f)
            frame = cv2.addWeighted(frame, alpha_c, frame, 0, gamma_c)

        return frame
