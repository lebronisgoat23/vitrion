import cv2
import numpy as np
import logging
import os
import warnings

# Suppress warnings from libraries
warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import cv2
import numpy as np
import logging
import os
from scipy import signal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VitalSignsAnalyzer:
    """
    Analyzes video to estimate vital signs (Heart Rate / BPM) using rPPG.
    Implements the 'Green Channel' method (POS/CHROM simplified).
    """

    def __init__(self):
        """
        Initialize rPPG engine using OpenCV Haar Cascade for ROI.
        """
        # Load standard Haar Cascade
        # We use the one included in cv2 data if possible, or expect it in system
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        if self.face_cascade.empty():
            logger.warning("VitalSignsAnalyzer: Haar Cascade xml not found via cv2.data. Trying default path.")
            # Fallback path if cv2.data is weird
        
        self.enabled = True
        logger.info("VitalSignsAnalyzer: Custom rPPG Engine (OpenCV Haar) ready.")

    def analyze_video(self, video_path: str):
        """
        Process a video file to extract heart rate.
        """
        if not os.path.exists(video_path):
            return {"status": "error", "message": "Video file not found."}

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps == 0: fps = 30.0

        green_signal = []
        frame_count = 0
        
        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
                
                if len(faces) > 0:
                    # Get first face
                    (x, y, w, h) = faces[0]
                    
                    # ROI: Center 40%
                    roi_x = int(x + w * 0.3)
                    roi_y = int(y + h * 0.2)
                    roi_w = int(w * 0.4)
                    roi_h = int(h * 0.4)
                    
                    roi = frame[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]
                    
                    if roi.size > 0:
                        g_mean = np.mean(roi[:, :, 1])
                        green_signal.append(g_mean)
                
                frame_count += 1
                if frame_count > 300: 
                    break

            cap.release()

            if len(green_signal) < 30: 
                return {"status": "error", "message": "Video too short or no face detected."}

            # Signal Processing
            signal_detrended = signal.detrend(np.array(green_signal))
            b, a = signal.butter(2, [0.7 / (fps / 2), 4.0 / (fps / 2)], btype='bandpass')
            signal_filtered = signal.filtfilt(b, a, signal_detrended)
            
            freqs, power = signal.periodogram(signal_filtered, fs=fps)
            max_power_idx = np.argmax(power)
            peak_freq = freqs[max_power_idx]
            bpm = peak_freq * 60.0

            return {
                "status": "success",
                "data": {
                    "bpm": round(float(bpm), 1),
                    "confidence": float(np.max(power))
                }
            }

        except Exception as e:
            logger.error(f"Custom rPPG Analysis failed: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}

    def close(self):
        pass



if __name__ == "__main__":
    # Quick Test
    analyzer = VitalSignsAnalyzer()
    if analyzer.enabled:
        print("rPPG Engine Ready.")
    else:
        print("rPPG Engine Disabled.")
