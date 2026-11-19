"""제어부로 목표 정보를 보내는 연결부.

보내는 값은 dx, dy, flag 세 정수입니다 (팀 펌웨어 motor_control 의 AUTO 규칙).
  dx: 화면 중앙 기준 가로 각도 오차 × 10. 오른쪽이 +   (예: 250 = 오른쪽 25.0°)
  dy: 화면 중앙 기준 세로 각도 오차 × 10. 위쪽이 +
  flag: 1 = 드론 탐지, 0 = 못 찾음 (못 찾아도 매 프레임 보내서 하트비트 역할)

연결 방법은 두 가지입니다.
  UdpLink    → control.py 로 "dx,dy,flag" 전송 (권장. control.py 가 COM 포트를 맡고
               키보드/조이스틱/자동 모드를 F1~F3 으로 전환)
  SerialLink → 아두이노로 "A,dx,dy,flag\n" 직접 전송 (control.py 없이 자동 모드만 시험할 때)
"""
import socket
import time

# 아두이노 정품과 흔한 호환보드 USB-시리얼 칩의 USB 제조사 ID(VID)
ARDUINO_VIDS = {
    0x2341: "Arduino",
    0x2A03: "Arduino (arduino.org)",
    0x1A86: "CH340 호환보드",
    0x0403: "FTDI",
    0x10C4: "CP210x",
}

DEFAULT_UDP = "127.0.0.1:5005"


def _describe(port):
    return f"{port.device} ({port.description})"


def find_arduino_port(ports=None):
    """연결된 아두이노의 COM 포트를 찾습니다. 정확히 하나일 때만 반환합니다.

    블루투스 등 다른 COM 포트가 섞여 있을 수 있어 아무 포트나 고르지 않습니다.
    ports는 테스트용이며, 생략하면 실제 연결된 포트 목록을 읽습니다.
    """
    if ports is None:
        from serial.tools import list_ports
        ports = list_ports.comports()
    ports = list(ports)
    matches = [p for p in ports
               if p.vid in ARDUINO_VIDS or "arduino" in (p.description or "").lower()]
    if len(matches) == 1:
        return matches[0].device
    all_ports = ", ".join(_describe(p) for p in ports) or "없음"
    if not matches:
        raise RuntimeError("아두이노를 찾지 못했습니다. USB 연결과 드라이버(CH340 등)를 확인하거나 "
                           f"--serial COM번호로 직접 지정하세요. 현재 포트: {all_ports}")
    raise RuntimeError("아두이노로 보이는 포트가 여러 개입니다. --serial COM번호로 직접 지정하세요. "
                       f"후보: {', '.join(_describe(p) for p in matches)}")


def resolve_port(name):
    """'auto'면 자동 탐색, 아니면 입력한 포트 이름을 그대로 씁니다."""
    return find_arduino_port() if name.lower() == "auto" else name


def parse_udp_target(text):
    """'HOST:PORT' 또는 'PORT' → (host, port)."""
    host, _, port = text.rpartition(":")
    try:
        number = int(port)
    except ValueError:
        raise ValueError(f"UDP 주소 형식이 잘못되었습니다: {text} (예: 127.0.0.1:5005)") from None
    if not 0 < number < 65536:
        raise ValueError(f"UDP 포트 번호는 1~65535 사이여야 합니다: {number}")
    return host or "127.0.0.1", number


def _values(dx, dy, flag):
    flag = 1 if flag else 0
    return (int(dx), int(dy), flag) if flag else (0, 0, 0)


class UdpLink:
    """control.py 로 'dx,dy,flag' 를 보냅니다. 받는 쪽이 없어도 에러 없이 계속 동작합니다."""

    def __init__(self, target=DEFAULT_UDP):
        self.address = parse_udp_target(target)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, dx=0, dy=0, flag=0):
        message = "{},{},{}".format(*_values(dx, dy, flag))
        try:
            self.sock.sendto(message.encode("ascii"), self.address)
        except OSError:
            pass  # control.py 가 아직 안 켜져 있어도 비전은 멈추지 않습니다.
        return message

    def close(self):
        self.sock.close()


class SerialLink:
    """아두이노(motor_control)로 'A,dx,dy,flag\n' 을 직접 보냅니다."""

    def __init__(self, port, baud=115200, boot_wait=2.0):
        import serial  # pyserial. --serial 옵션을 쓸 때만 필요합니다.
        self._timeout_error = serial.SerialTimeoutException
        self.port = port
        self.ser = serial.Serial(port, baud, timeout=0, write_timeout=0.05)
        time.sleep(boot_wait)  # Uno R3는 포트를 열면 리셋되므로 부팅을 기다립니다.
        self.ser.reset_input_buffer()

    def send(self, dx=0, dy=0, flag=0):
        message = "A,{},{},{}".format(*_values(dx, dy, flag))
        try:
            self.ser.write((message + "\n").encode("ascii"))
        except self._timeout_error:
            pass  # 밀린 데이터는 버립니다. 오래된 좌표보다 다음 프레임이 낫습니다.
        return message

    def close(self):
        self.ser.close()
