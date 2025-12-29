import cv2
import mediapipe as mp
import numpy as np
import logging
import os
from typing import Dict, Any, Optional, Tuple, List
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FaceEdemaAnalyzer:
    """
    Analyzes facial geometry to estimate edema (swelling) metrics using MediaPipe Tasks (FaceLandmarker).
    """

    def __init__(self, model_path: str = "backend/models/face_landmarker.task"):
        """
        Initialize MediaPipe FaceLandmarker.
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}. Please download it.")

        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
            num_faces=1
        )
        self.detector = vision.FaceLandmarker.create_from_options(options)

        # Landmark Indices (Standard 468 topology)
        self.IDX_ZYGOMA_LEFT = 234
        self.IDX_ZYGOMA_RIGHT = 454
        self.IDX_GLABELLA = 10
        self.IDX_CHIN = 152
        self.IDX_JAW_CORNER_L = 172
        self.IDX_JAW_CORNER_R = 397
        self.IDX_JAW_UPPER_L = 234
        self.IDX_JAW_UPPER_R = 454

    def analyze(self, image_array: np.ndarray) -> Dict[str, Any]:
        """
        Process the image and return geometric metrics.
        """
        if image_array is None or image_array.size == 0:
            return self._create_error_response("Invalid or empty image provided.")

        try:
            # MediaPipe Tasks expects mp.Image
            image_rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
            
            detection_result = self.detector.detect(mp_image)

            if not detection_result.face_landmarks:
                return self._create_error_response("No face detected in the image.")

            # Get the first face
            face_landmarks = detection_result.face_landmarks[0]
            
            # Convert to numpy for easier math
            # Note: tasks API returns NormalizedLandmark (x, y, z).
            h, w, _ = image_array.shape
            landmarks_np = np.array([
                [lm.x * w, lm.y * h, lm.z * w] 
                for lm in face_landmarks
            ])

            # 1. Calculate Face Width / Height Ratio
            face_width = self._calculate_distance(
                landmarks_np[self.IDX_ZYGOMA_LEFT], 
                landmarks_np[self.IDX_ZYGOMA_RIGHT]
            )
            face_height = self._calculate_distance(
                landmarks_np[self.IDX_GLABELLA], 
                landmarks_np[self.IDX_CHIN]
            )
            
            wh_ratio = face_width / face_height if face_height > 0 else 0.0

            # 2. Calculate Jawline Sharpness
            angle_left = self._calculate_angle(
                landmarks_np[self.IDX_JAW_UPPER_L],
                landmarks_np[self.IDX_JAW_CORNER_L],
                landmarks_np[self.IDX_CHIN]
            )
            angle_right = self._calculate_angle(
                landmarks_np[self.IDX_JAW_UPPER_R],
                landmarks_np[self.IDX_JAW_CORNER_R],
                landmarks_np[self.IDX_CHIN]
            )
            avg_jaw_angle = (angle_left + angle_right) / 2.0

            # 3. Chin Angle
            chin_angle = self._calculate_angle(
                landmarks_np[self.IDX_JAW_CORNER_L],
                landmarks_np[self.IDX_CHIN],
                landmarks_np[self.IDX_JAW_CORNER_R]
            )

            metrics = {
                "face_width_height_ratio": round(float(wh_ratio), 4),
                "jawline_sharpness_deg": round(float(avg_jaw_angle), 2),
                "chin_angle_deg": round(float(chin_angle), 2),
                "details": {
                    "face_width_px": round(float(face_width), 1),
                    "face_height_px": round(float(face_height), 1),
                    "jaw_angle_left": round(float(angle_left), 2),
                    "jaw_angle_right": round(float(angle_right), 2)
                }
            }

            return {
                "status": "success",
                "data": metrics
            }

        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            return self._create_error_response(f"Internal analysis error: {str(e)}")

    def _calculate_distance(self, p1: np.ndarray, p2: np.ndarray) -> float:
        return np.linalg.norm(p1 - p2)

    def _calculate_angle(self, p_a: np.ndarray, p_vertex: np.ndarray, p_b: np.ndarray) -> float:
        vec_a = p_a - p_vertex
        vec_b = p_b - p_vertex
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        dot_product = np.dot(vec_a, vec_b)
        cosine_angle = np.clip(dot_product / (norm_a * norm_b), -1.0, 1.0)
        return np.degrees(np.arccos(cosine_angle))

    def _create_error_response(self, message: str) -> Dict[str, Any]:
        return {"status": "error", "message": message, "data": None}

    def close(self):
        self.detector.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

