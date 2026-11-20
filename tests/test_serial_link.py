import unittest
from collections import namedtuple
from uav_tracker.serial_link import SerialLink, find_arduino_port, resolve_port

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


class FakeSerial:
    def __init__(self):
        self.sent = []

    def write(self, data):
        self.sent.append(data)


class MessageFormatTest(unittest.TestCase):
    def make_serial(self):
        link = SerialLink.__new__(SerialLink)
        link.ser = FakeSerial()
        link._timeout_error = TimeoutError
        return link

    def test_serial_uses_team_auto_format(self):
        link = self.make_serial()
        self.assertEqual(link.send(310, 20, 1), "A,310,20,1")
        self.assertEqual(link.ser.sent, [b"A,310,20,1\n"])

    def test_negative_values_are_plain_text(self):
        link = self.make_serial()
        self.assertEqual(link.send(-640, -360, 1), "A,-640,-360,1")

    def test_lost_target_sends_zeros(self):
        link = self.make_serial()
        self.assertEqual(link.send(123, 45, 0), "A,0,0,0")


if __name__ == "__main__":
    unittest.main()
