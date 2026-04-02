import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"

import sys
import json
import cv2
import torch
import mediapipe as mp

from torch import nn
from torchvision import transforms, models
from PIL import Image
from collections import deque, Counter

from PyQt5 import QtWidgets, QtGui, QtCore, uic
from PyQt5.QtWidgets import QMessageBox
from deepface import DeepFace


# =========================
# CONFIG
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UI_PATH = os.path.join(BASE_DIR, "face_app.ui")
MODEL_PATH = os.path.join(BASE_DIR, "identity_model.pth")
CLASS_NAMES_PATH = os.path.join(BASE_DIR, "class_names.json")

IMG_SIZE = 224
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

# Confidence threshold for access approval
ACCESS_THRESHOLD = 60.0


class FaceApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Load UI directly from .ui file
        if not os.path.isfile(UI_PATH):
            raise FileNotFoundError(f"UI file not found: {UI_PATH}")
        uic.loadUi(UI_PATH, self)

        self.setWindowTitle("Face Identity, Emotion and Finger Recognition")

        # Check important widgets exist
        required_widgets = ["camera_label", "start_button", "stop_button", "resultBanner", "finger_label", "name_label", "left_blink_label", "right_blink_label"]
        for widget_name in required_widgets:
            if not hasattr(self, widget_name):
                raise AttributeError(
                    f"Widget '{widget_name}' not found in face_app.ui.\n"
                    f"Please check the objectName in Qt Designer."
                )

        # Camera label setup
        self.camera_label.setAlignment(QtCore.Qt.AlignCenter)
        if not self.camera_label.text():
            self.camera_label.setText("Camera Feed")

        # State
        self.cap = None
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        self.identity_history = deque(maxlen=10)
        self.emotion_history = deque(maxlen=10)
        #self.finger_history = deque(maxlen=8)

        self.left_blink_count = 0
        self.right_blink_count = 0

        self.left_closed_frames = 0
        self.right_closed_frames = 0

        self.left_eye_closed = False
        self.right_eye_closed = False

        self.frame_count = 0

        self.class_names = []
        self.identity_model = None

        # Pre-create transform once
        self.transform = transforms.Compose([
            transforms.Resize((IMG_SIZE, IMG_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(
                [0.485, 0.456, 0.406],
                [0.229, 0.224, 0.225]
            ),
        ])

        # Load face detector
        self.face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
        if self.face_cascade.empty():
            self.show_error("OpenCV Error", f"Could not load Haar cascade:\n{CASCADE_PATH}")

        # Hand detection (MediaPipe)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils

        # Face Mesh for blink detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # Load model and classes
        self.load_resources()

        # Connect buttons
        self.start_button.clicked.connect(self.start_camera)
        self.stop_button.clicked.connect(self.stop_camera)

        # Initial button state
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        # Set initial banner state
        self.set_result_neutral()

        # Style labels
        self.finger_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: yellow;")
        self.name_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: cyan;")
        self.left_blink_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: lightgreen;")
        self.right_blink_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: lightgreen;")

        # Eye landmarks constants for blink detection
        self.LEFT_EYE = {
            "top1": 159,
            "top2": 160,
            "bottom1": 145,
            "bottom2": 144,
            "left_corner": 33,
            "right_corner": 133
        }

        self.RIGHT_EYE = {
            "top1": 386,
            "top2": 385,
            "bottom1": 374,
            "bottom2": 380,
            "left_corner": 362,
            "right_corner": 263
        }

        self.EAR_THRESHOLD = 0.20
        self.CONSEC_FRAMES = 2

    # =========================
    # MODEL / FILE LOADING
    # =========================
    def load_resources(self):
        """Load class names and identity model safely."""
        try:
            if not os.path.isfile(CLASS_NAMES_PATH):
                raise FileNotFoundError(f"class_names.json not found:\n{CLASS_NAMES_PATH}")

            with open(CLASS_NAMES_PATH, "r") as f:
                self.class_names = json.load(f)

            if not isinstance(self.class_names, list) or len(self.class_names) == 0:
                raise ValueError("class_names.json is empty or invalid.")

            if not os.path.isfile(MODEL_PATH):
                raise FileNotFoundError(f"identity_model.pth not found:\n{MODEL_PATH}")

            self.identity_model = self.build_model(len(self.class_names))
            self.statusBar().showMessage("Model loaded successfully. System ready.")

        except Exception as e:
            self.identity_model = None
            self.show_error("Model Loading Error", str(e))
            self.statusBar().showMessage("Model not loaded.")

    def build_model(self, num_classes):
        model = models.resnet18(weights=None)
        model.fc = nn.Linear(model.fc.in_features, num_classes)

        state_dict = torch.load(MODEL_PATH, map_location=DEVICE)
        model.load_state_dict(state_dict)

        model.to(DEVICE)
        model.eval()
        return model

    # =========================
    # CAMERA CONTROL
    # =========================
    def start_camera(self):
        if self.cap is not None and self.cap.isOpened():
            return

        self.cap = cv2.VideoCapture(0)

        if not self.cap.isOpened():
            self.cap = None
            self.show_error("Camera Error", "Could not open webcam.")
            return

        self.identity_history.clear()
        self.emotion_history.clear()
        #self.finger_history.clear()

        self.left_blink_count = 0
        self.right_blink_count = 0
        self.left_closed_frames = 0
        self.right_closed_frames = 0
        self.left_eye_closed = False
        self.right_eye_closed = False

        self.left_blink_label.setText("Left Blink: 0")
        self.right_blink_label.setText("Right Blink: 0")

        self.finger_label.setText("Fingers: -")
        self.name_label.setText("Name: - | Emotion: -")

        self.timer.start(30)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        self.set_result_neutral()
        self.statusBar().showMessage("Camera started. Waiting for face and hand scan...")

    def stop_camera(self):
        self.timer.stop()

        if self.cap is not None:
            self.cap.release()
            self.cap = None

        self.camera_label.setPixmap(QtGui.QPixmap())
        self.camera_label.setText("Camera Stopped")

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        self.identity_history.clear()
        self.emotion_history.clear()
        #self.finger_history.clear()

        self.finger_label.setText("Fingers: -")
        self.name_label.setText("Name: - | Emotion: -")

        self.left_blink_label.setText("Left Blink: 0")
        self.right_blink_label.setText("Right Blink: 0")

        self.set_result_neutral()
        self.statusBar().showMessage("Camera stopped.")

    # =========================
    # RESULT BANNER
    # =========================
    def set_result_neutral(self):
        self.resultBanner.setText("SYSTEM READY")
        self.resultBanner.setStyleSheet("""
            QLabel#resultBanner {
                background-color: #111a2b;
                border: 2px solid #22324a;
                border-radius: 12px;
                color: #f1f5f9;
                font-size: 16pt;
                font-weight: bold;
                padding: 12px;
            }
        """)

    def show_granted(self, name):
        self.resultBanner.setText(f"ACCESS GRANTED\n{name} VERIFIED — GATE OPEN")
        self.resultBanner.setStyleSheet("""
            QLabel#resultBanner {
                background-color: #0f2d1f;
                border: 2px solid #18b76a;
                border-radius: 12px;
                color: #d1fadf;
                font-size: 16pt;
                font-weight: bold;
                padding: 12px;
            }
        """)

    def show_denied(self):
        self.resultBanner.setText("ACCESS DENIED\nWARNING — UNRECOGNISED FACE")
        self.resultBanner.setStyleSheet("""
            QLabel#resultBanner {
                background-color: #341212;
                border: 2px solid #ef4444;
                border-radius: 12px;
                color: #ffe2e2;
                font-size: 16pt;
                font-weight: bold;
                padding: 12px;
            }
        """)

    # =========================
    # PREDICTION
    # =========================
    def predict_identity(self, face):
        """Predict identity from cropped face image."""
        if self.identity_model is None or not self.class_names:
            return "Unknown", 0.0

        try:
            face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            face_pil = Image.fromarray(face_rgb)
            tensor = self.transform(face_pil).unsqueeze(0).to(DEVICE)

            with torch.no_grad():
                outputs = self.identity_model(tensor)
                probs = torch.softmax(outputs, dim=1)
                conf, idx = torch.max(probs, dim=1)

            predicted_name = self.class_names[idx.item()]
            confidence = conf.item() * 100
            return predicted_name, confidence

        except Exception:
            return "Unknown", 0.0

    def predict_emotion(self, face):
        """Predict emotion using DeepFace."""
        try:
            result = DeepFace.analyze(
                img_path=face,
                actions=["emotion"],
                enforce_detection=False,
                detector_backend="opencv",
                silent=True
            )

            if isinstance(result, list):
                result = result[0]

            return result.get("dominant_emotion", "Unknown")

        except Exception:
            return "Unknown"

    def euclidean(self, p1, p2):
        return ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** 0.5
    def eye_aspect_ratio(self, landmarks, top1, top2, bottom1, bottom2, left_corner, right_corner):
        vertical_1 = self.euclidean(landmarks[top1], landmarks[bottom1])
        vertical_2 = self.euclidean(landmarks[top2], landmarks[bottom2])
        horizontal = self.euclidean(landmarks[left_corner], landmarks[right_corner])
        if horizontal == 0:
            return 0.0
        return (vertical_1 + vertical_2) / (2.0 * horizontal)

    def count_fingers(self, hand_landmarks, handedness_label):
        """
        Count extended fingers using MediaPipe landmarks.
        Uses handedness to improve thumb counting reliability.
        """
        landmarks = hand_landmarks.landmark
        finger_count = 0

        # For index, middle, ring, pinky:
        tip_ids = [8, 12, 16, 20]
        pip_ids = [6, 10, 14, 18]

        for tip_id, pip_id in zip(tip_ids, pip_ids):
            if landmarks[tip_id].y < landmarks[pip_id].y:
                finger_count += 1

        # Thumb logic depends on left/right hand
        # For a mirrored webcam, this may still vary slightly across setups,
        # but this is more reliable than the old fixed rule.
        if handedness_label == "Right":
            if landmarks[4].x < landmarks[3].x:
                finger_count += 1
        else:  # Left hand
            if landmarks[4].x > landmarks[3].x:
                finger_count += 1

        return finger_count

    # =========================
    # FRAME UPDATE
    # =========================
    def update_frame(self):
        if self.cap is None:
            return

        ret, frame = self.cap.read()
        if not ret:
            return
        
        frame = cv2.flip(frame, 1)  # Mirror view for more natural webcam display
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # ---------------------------
        # Eye Blink Detection Logic
        # ---------------------------
    
        face_mesh_results = self.face_mesh.process(rgb_frame)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if face_mesh_results.multi_face_landmarks:
            face_landmarks = face_mesh_results.multi_face_landmarks[0]
            lm = face_landmarks.landmark

            left_ear = self.eye_aspect_ratio(
                lm,
                self.LEFT_EYE["top1"], self.LEFT_EYE["top2"],
                self.LEFT_EYE["bottom1"], self.LEFT_EYE["bottom2"],
                self.LEFT_EYE["left_corner"], self.LEFT_EYE["right_corner"]
            )

            right_ear = self.eye_aspect_ratio(
                lm,
                self.RIGHT_EYE["top1"], self.RIGHT_EYE["top2"],
                self.RIGHT_EYE["bottom1"], self.RIGHT_EYE["bottom2"],
                self.RIGHT_EYE["left_corner"], self.RIGHT_EYE["right_corner"]
            )

            # Left blink logic
            if left_ear < self.EAR_THRESHOLD:
                self.left_closed_frames += 1
                if self.left_closed_frames >= self.CONSEC_FRAMES and not self.left_eye_closed:
                    self.left_blink_count += 1
                    self.left_eye_closed = True
            else:
                self.left_closed_frames = 0
                self.left_eye_closed = False

            # Right blink logic
            if right_ear < self.EAR_THRESHOLD:
                self.right_closed_frames += 1
                if self.right_closed_frames >= self.CONSEC_FRAMES and not self.right_eye_closed:
                    self.right_blink_count += 1
                    self.right_eye_closed = True
            else:
                self.right_closed_frames = 0
                self.right_eye_closed = False

            self.left_blink_label.setText(f"Left Blink: {self.left_blink_count}")
            self.right_blink_label.setText(f"Right Blink: {self.right_blink_count}")
        else:
            self.left_blink_label.setText(f"Left Blink: {self.left_blink_count}")
            self.right_blink_label.setText(f"Right Blink: {self.right_blink_count}")

        # -------------------------
        # HAND DETECTION
        # -------------------------
        #rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        hand_results = self.hands.process(rgb_frame)

        left_hand = None
        right_hand = None

        if hand_results.multi_hand_landmarks and hand_results.multi_handedness:
            for hand_landmarks, handedness in zip(
                hand_results.multi_hand_landmarks,
                hand_results.multi_handedness
            ):
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )

                handedness_label = handedness.classification[0].label
                finger_count = self.count_fingers(hand_landmarks, handedness_label)

                if handedness_label == "Left":
                    left_hand = f"Left: {finger_count}"
                else:
                    right_hand = f"Right: {finger_count}"

            gesture_lines = []

            if left_hand:
                gesture_lines.append(left_hand)
            if right_hand:
                gesture_lines.append(right_hand)

            status_gesture = " | ".join(gesture_lines)
            self.finger_label.setText(f"Fingers: {status_gesture}")

        else:
            status_gesture = "No hand detected"
            self.finger_label.setText("Fingers: -")

        # -------------------------
        # FACE DETECTION
        # -------------------------
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.05,
            minNeighbors=4,
            minSize=(80, 80)
        )

        # No face detected
        if len(faces) == 0:
            self.set_result_neutral()
            self.name_label.setText("Name: - | Emotion: -")
            self.statusBar().showMessage(f"No face detected. {status_gesture} ")
            self.show_frame(frame)
            return

        # Only process the first detected face for cleaner UI behavior
        x, y, w, h = faces[0]
        face = frame[y:y + h, x:x + w]

        if face.size == 0:
            self.show_frame(frame)
            return

        name, conf = self.predict_identity(face)
        
        self.frame_count += 1

        if self.frame_count % 10 == 0:
            emotion = self.predict_emotion(face)
        else:
            emotion = self.emotion_history[-1] if self.emotion_history else "Detecting..."

        self.identity_history.append(name)
        self.emotion_history.append(emotion)

        smooth_name = Counter(self.identity_history).most_common(1)[0][0]
        smooth_emotion = Counter(self.emotion_history).most_common(1)[0][0]
        self.name_label.setText(f"Name: {smooth_name} | Emotion: {smooth_emotion}")

        allowed = (smooth_name != "Unknown") and (conf >= ACCESS_THRESHOLD)

        if allowed:
            box_color = (0, 200, 0)
            #label = f"{smooth_name} | {smooth_emotion} | {conf:.1f}% | ALLOWED"
            self.show_granted(smooth_name)
            self.statusBar().showMessage(
                f"{smooth_name} verified. Entry allowed. {status_gesture} "
            )
        else:
            box_color = (0, 0, 255)
            #label = f"{smooth_name} | {smooth_emotion} | {conf:.1f}% | DENIED"
            self.show_denied()
            self.statusBar().showMessage(
                f"Face not recognised. Warning triggered. {status_gesture} "
            )

        cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)
        
        self.show_frame(frame)


    # =========================
    # DISPLAY
    # =========================
    def show_frame(self, frame):
        """Display OpenCV frame inside QLabel."""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w

        qt_img = QtGui.QImage(
            rgb.data,
            w,
            h,
            bytes_per_line,
            QtGui.QImage.Format_RGB888
        )

        pixmap = QtGui.QPixmap.fromImage(qt_img)

        scaled_pixmap = pixmap.scaled(
            self.camera_label.width(),
            self.camera_label.height(),
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        )

        self.camera_label.setPixmap(scaled_pixmap)

    def closeEvent(self, event):
        """Make sure camera and hand resources are released when app closes."""
        self.stop_camera()
        try:
            self.hands.close()
        except Exception:
            pass
        try:
            self.face_mesh.close()
        except Exception:
            pass
        event.accept()

    def show_error(self, title, message):
        QMessageBox.critical(self, title, message)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = FaceApp()
    window.show()
    sys.exit(app.exec_())
