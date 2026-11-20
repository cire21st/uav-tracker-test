import unittest
from uav_tracker.geometry import Detection, pick_target, to_control_values


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


class ControlValuesTest(unittest.TestCase):
    def test_xy_plane_signs(self):
        # 오른쪽 위 → dx +, dy +  /  왼쪽 아래 → dx −, dy −
        self.assertEqual(to_control_values(310, -20), (310, 20))
        self.assertEqual(to_control_values(-310, 20), (-310, -20))

    def test_rounds_to_integers(self):
        dx, dy = to_control_values(-309.5 + 0.2, -224.5 - 0.2)
        self.assertEqual((dx, dy), (-309, 225))
        self.assertIsInstance(dx, int)
        self.assertIsInstance(dy, int)

    def test_center_is_zero(self):
        self.assertEqual(to_control_values(0.0, 0.0), (0, 0))


if __name__ == "__main__":
    unittest.main()
