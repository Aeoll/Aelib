import sys
import unittest
from pathlib import Path

# Load the Python 3.9 library variant this test protects.
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from svg.path.parser import parse_path


class SmoothCommandsAfterCloseTest(unittest.TestCase):
    def test_smooth_cubic_after_close_starts_at_current_point(self):
        segments = parse_path("M 0,0 C 1,1 2,2 3,3 Z S 1,1 2,2")
        curve = segments[-1]
        self.assertEqual(type(curve).__name__, "CubicBezier")
        self.assertEqual(curve.control1, curve.start)
        self.assertEqual(curve.start, 0j)

    def test_smooth_quadratic_after_close_starts_at_current_point(self):
        segments = parse_path("M 0,0 Q 1,1 2,2 Z T 3,3")
        curve = segments[-1]
        self.assertEqual(type(curve).__name__, "QuadraticBezier")
        self.assertEqual(curve.control, curve.start)
        self.assertEqual(curve.start, 0j)


if __name__ == "__main__":
    unittest.main()
