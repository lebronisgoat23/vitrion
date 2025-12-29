import unittest
import numpy as np
import sys
import os

# Ensure backend can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.core.face_analyzer import FaceEdemaAnalyzer

class TestFaceEdemaAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = FaceEdemaAnalyzer()

    def tearDown(self):
        self.analyzer.close()

    def test_empty_image(self):
        """Test reaction to None or empty numpy array."""
        result = self.analyzer.analyze(None)
        self.assertEqual(result['status'], 'error')
        self.assertIn('Invalid', result['message'])

        result_empty = self.analyzer.analyze(np.array([]))
        self.assertEqual(result_empty['status'], 'error')

    def test_no_face_image(self):
        """Test reaction to an image with random noise (no face)."""
        # Create a blank black image 640x480
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        
        result = self.analyzer.analyze(img)
        self.assertEqual(result['status'], 'error')
        self.assertIn('No face detected', result['message'])

    def test_structure_success_mock(self):
        """
        Since we don't have a real face image in CI/headless easily without downloading one,
        we verify the class structure and methods exist.
        Actual logic validation requires a real image test which we can add later.
        """
        self.assertTrue(hasattr(self.analyzer, 'analyze'))
        self.assertTrue(hasattr(self.analyzer, '_calculate_distance'))
        self.assertTrue(hasattr(self.analyzer, '_calculate_angle'))

if __name__ == '__main__':
    unittest.main()
