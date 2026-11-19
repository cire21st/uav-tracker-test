import unittest
from collections import namedtuple
import socket
from uav_tracker.serial_link import (SerialLink, UdpLink, find_arduino_port,
                                     parse_udp_target, resolve_port)

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
        self.assertEqual(link.send(250, 17, 1), "A,250,17,1")
        self.assertEqual(link.ser.sent, [b"A,250,17,1\n"])

    def test_lost_target_sends_zeros(self):
        link = self.make_serial()
        self.assertEqual(link.send(123, 45, 0), "A,0,0,0")

    def test_udp_round_trip(self):
        receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        receiver.bind(("127.0.0.1", 0))
        receiver.settimeout(2)
        link = UdpLink(f"127.0.0.1:{receiver.getsockname()[1]}")
        try:
            self.assertEqual(link.send(-440, 285, 1), "-440,285,1")
            self.assertEqual(receiver.recvfrom(64)[0], b"-440,285,1")
        finally:
            link.close()
            receiver.close()

    def test_udp_without_receiver_does_not_raise(self):
        link = UdpLink("127.0.0.1:9")
        try:
            link.send(1, 2, 1)
        finally:
            link.close()

    def test_parse_udp_target(self):
        self.assertEqual(parse_udp_target("127.0.0.1:5005"), ("127.0.0.1", 5005))
        self.assertEqual(parse_udp_target("6000"), ("127.0.0.1", 6000))
        with self.assertRaises(ValueError):
            parse_udp_target("localhost:abc")


if __name__ == "__main__":
    unittest.main()
