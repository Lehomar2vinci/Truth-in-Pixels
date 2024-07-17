from flask import Flask, render_template, Response, request, jsonify
import cv2
import numpy as np
import mediapipe as mp
import warnings
import threading
from video_processing import apply_effects, update_effect_settings

# Ignorer les avertissements spécifiques de protobuf
warnings.filterwarnings("ignore", category=UserWarning,
                        module='google.protobuf')

app = Flask(__name__)

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh()
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

effect_settings = {
    "deformation_intensity": 1,
    "pointillism_size": 2,
    "facemask_point_size": 5,
    "mirror_intensity": 1,
    "color_intensity": 5,
    "blur_intensity": 1,
    "vignette_intensity": 1,
    "selected_effects": []
}

lock = threading.Lock()


def generate_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results_pose = pose.process(rgb_frame)
            results_face = face_mesh.process(rgb_frame)
            results_hands = hands.process(rgb_frame)

            with lock:
                frame = apply_effects(
                    frame, results_pose, results_face, results_hands, effect_settings)

            # Utiliser JPEG pour le flux vidéo
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/update_effects', methods=['POST'])
def update_effects_route():
    data = request.json
    with lock:
        update_effect_settings(effect_settings, data)
    return jsonify(success=True)


if __name__ == '__main__':
    app.run(debug=True)
