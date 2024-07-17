from setuptools import setup
import py2exe
import sys

sys.setrecursionlimit(5000)


setup(
    name="TrackingApp",
    version="1.0",
    description="Application de suivi",
    author="Nathan Chambrette",
    # Changez 'console' en 'windows' pour une application GUI sans console
    windows=['main.py'],
    options={
        "py2exe": {
            "packages": ["os", "sys", "cv2", "numpy", "mediapipe", "PyQt5"],
            "includes": ["os", "sys", "cv2", "numpy", "mediapipe", "PyQt5"],
            # Exclure des modules non nécessaires
            "excludes": ["tkinter", "unittest", "email"],
        }
    },
    data_files=[
        ('mediapipe/modules/pose_landmark',
         ['mediapipe/modules/pose_landmark/pose_landmark_cpu.binarypb'])
    ],
    py_modules=['main', 'interface', 'video_processing', 'controls']
)
