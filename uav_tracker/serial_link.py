"""아두이노(motor_control)로 목표 정보를 보내는 시리얼 송신기.

메시지 (글자 한 줄, 115200 baud, 매 프레임):  A,dx,dy,flag + 줄바꿈
  dx: 화면 중앙 기준 가로 픽셀 오차, 정수. 오른쪽 +, 왼쪽 −   (1280×720 기준 약 −640 ~ +640)
  dy: 화면 중앙 기준 세로 픽셀 오차, 정수. 위쪽 +, 아래쪽 −   (약 −360 ~ +360)
  flag: 1 = 드론 탐지, 0 = 못 찾음 (못 찾아도 매 프레임 보내서 하트비트 역할)

정수 값을 2바이트 바이너리가 아니라 글자(ASCII)로 보냅니다. 조이스틱 메시지(M,x,y)와 같은 방식입니다.
"""
import time

# 아두이노 정품과 흔한 호환보드 USB-시리얼 칩의 USB 제조사 ID(VID)
ARDUINO_VIDS = {
    0x2341: "Arduino",
    0x2A03: "Arduino (arduino.org)",
    0x1A86: "CH340 호환보드",
    0x0403: "FTDI",
    0x10C4: "CP210x",
}


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


def _values(dx, dy, flag):
    flag = 1 if flag else 0
    return (int(dx), int(dy), flag) if flag else (0, 0, 0)


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
