import unittest
from uav_tracker.geometry import Detection, pick_target, to_angle10


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


class AngleTest(unittest.TestCase):
    def test_center_is_zero(self):
        self.assertEqual(to_angle10(0, 0, 1280, 720, 95.8), (0, 0))

    def test_frame_edges_match_fov(self):
        # 대각선 95.8°, 16:9 → 가로 약 ±44.0°, 세로 약 ±28.5°
        ax, ay = to_angle10(640, 360, 1280, 720, 95.8)
        self.assertAlmostEqual(ax / 10, 44.0, delta=0.2)
        self.assertAlmostEqual(ay / 10, 28.5, delta=0.2)
        self.assertEqual(to_angle10(-640, -360, 1280, 720, 95.8), (-ax, -ay))

    def test_same_angle_across_resolution(self):
        self.assertEqual(to_angle10(320, 180, 1280, 720, 95.8),
                         to_angle10(160, 90, 640, 360, 95.8))


class PickTargetTest(unittest.TestCase):
    def test_empty(self):
        self.assertIsNone(pick_target([], 3))

    def test_keeps_locked_id_over_confidence(self):
        a = Detection((0, 0, 1, 1), 0.9, 0, "q", 1)
        b = Detection((0, 0, 1, 1), 0.5, 0, "q", 2)
        self.assertIs(pick_target([a, b], 2), b)

    def test_falls_back_to_confidence(self):
        a = Detection((0, 0, 1, 1), 0.4, 0, "q", 1)
        b = Detection((0, 0, 1, 1), 0.8, 0, "q", 2)
        self.assertIs(pick_target([a, b], 9), b)
        self.assertIs(pick_target([a, b], None), b)


if __name__ == "__main__":
    unittest.main()
