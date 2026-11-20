"""영상 좌표 계산. OpenCV/YOLO 없이도 테스트할 수 있습니다."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Detection:
    xyxy: tuple[float, float, float, float]
    confidence: float
    class_id: int
    name: str
    track_id: int | None = None

    def coordinates(self, width: int, height: int) -> dict[str, float]:
        # 원점은 영상 왼쪽 위입니다. x는 오른쪽, y는 아래쪽으로 증가합니다.
        x1, y1, x2, y2 = self.xyxy
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        # 반올림은 그릴 때만 수행하여 출력 좌표의 정밀도를 유지합니다.
        return dict(cx=cx, cy=cy, error_x=cx - width / 2, error_y=cy - height / 2)


def pick_target(detections, locked_id):
    """제어에 쓸 대상 하나를 고릅니다. 추적 중인 ID를 우선하고, 없으면 신뢰도 최대."""
    if not detections:
        return None
    if locked_id is not None:
        for d in detections:
            if d.track_id == locked_id:
                return d
    return max(detections, key=lambda d: d.confidence)


def to_control_values(error_x: float, error_y: float) -> tuple[int, int]:
    """제어부(motor_control)에 보낼 dx, dy. 단위는 픽셀, 정수.

    xy 평면처럼 맞춥니다: dx는 오른쪽 +, 왼쪽 −. dy는 위쪽 +, 아래쪽 −.
    영상 좌표는 아래쪽이 +이므로 세로 부호만 뒤집습니다.
    (팀 펌웨어 조이스틱 모드도 스틱을 위로 밀면 + 라서 같은 방향입니다.)
    """
    return round(error_x), round(-error_y)
