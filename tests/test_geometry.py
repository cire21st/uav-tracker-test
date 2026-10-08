import unittest
from uav_tracker.geometry import Detection


class CoordinatesTest(unittest.TestCase):
    def test_centered_object(self):
        d = Detection((300, 220, 340, 260), 0.9, 0, "person")
        self.assertEqual(d.coordinates(640, 480), dict(cx=320, cy=240, error_x=0, error_y=0))

    def test_top_left_and_subpixel(self):
        d = Detection((0, 0, 21, 31), 0.9, 0, "person")
        self.assertEqual(d.coordinates(640, 480),
                         dict(cx=10.5, cy=15.5, error_x=-309.5, error_y=-224.5))

    def test_bottom_right_actual_resolution(self):
        d = Detection((1000, 600, 1200, 700), 0.9, 0, "person", 7)
        self.assertEqual(d.coordinates(1280, 720),
                         dict(cx=1100, cy=650, error_x=460, error_y=290))


if __name__ == "__main__":
    unittest.main()
