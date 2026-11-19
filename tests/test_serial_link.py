import unittest
from collections import namedtuple
from uav_tracker.serial_link import find_arduino_port, resolve_port

Port = namedtuple("Port", "device description vid")
BT = Port("COM3", "Standard Serial over Bluetooth link", None)
UNO = Port("COM4", "Arduino Uno (COM4)", 0x2341)
CLONE = Port("COM7", "USB-SERIAL CH340 (COM7)", 0x1A86)


class FindArduinoPortTest(unittest.TestCase):
    def test_finds_official_board_among_others(self):
        self.assertEqual(find_arduino_port([BT, UNO]), "COM4")

    def test_finds_ch340_clone(self):
        self.assertEqual(find_arduino_port([BT, CLONE]), "COM7")

    def test_matches_description_without_vid(self):
        self.assertEqual(find_arduino_port([Port("COM9", "Arduino Mega 2560", None)]), "COM9")

    def test_none_found_lists_ports(self):
        with self.assertRaisesRegex(RuntimeError, "찾지 못했습니다.*COM3"):
            find_arduino_port([BT])

    def test_none_connected(self):
        with self.assertRaisesRegex(RuntimeError, "현재 포트: 없음"):
            find_arduino_port([])

    def test_multiple_candidates_refused(self):
        with self.assertRaisesRegex(RuntimeError, "여러 개.*COM4.*COM7"):
            find_arduino_port([UNO, CLONE])

    def test_explicit_port_passes_through(self):
        self.assertEqual(resolve_port("COM5"), "COM5")


if __name__ == "__main__":
    unittest.main()
