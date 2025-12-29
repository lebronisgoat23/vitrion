import cv2
import numpy as np
import sys
import os

# Ensure we can import the backend modules
sys.path.append(os.getcwd())

from backend.core.face_analyzer import FaceEdemaAnalyzer

def create_dummy_face_image():
    """
    Creates a simple image. 
    Note: MediaPipe might not detect a face in a purely drawn geometric face, 
    so this script primarily tests the *workflow* and error handling if no face is found.
    To see real metrics, you need to provide a path to a real photo.
    """
    # Create black image
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    # Draw a circle (face)
    cv2.circle(img, (320, 240), 100, (255, 255, 255), -1)
    return img

def main():
    print("--- Vitrion Face Edema Analyzer Demo ---")
    
    # Initialize Analyzer
    try:
        analyzer = FaceEdemaAnalyzer()
        print("✅ Model loaded successfully.")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return

    # 1. Test with a dummy (synthetic) image -> Expect "No face detected"
    print("\n[Test 1] Analyzing synthetic generated image...")
    dummy_img = create_dummy_face_image()
    result = analyzer.analyze(dummy_img)
    print(f"Result: {result}")
    
    # 2. Instructions for real image
    print("\n[Test 2] To see real data, run this script with an image path:")
    print("      python3 demo_run.py path/to/your/photo.jpg")
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        print(f"\n[Test 3] Analyzing provided image: {image_path}")
        if os.path.exists(image_path):
            real_img = cv2.imread(image_path)
            if real_img is not None:
                real_result = analyzer.analyze(real_img)
                import json
                print(json.dumps(real_result, indent=2))
            else:
                print("❌ Could not read image file.")
        else:
            print("❌ File does not exist.")

    analyzer.close()

if __name__ == "__main__":
    main()
