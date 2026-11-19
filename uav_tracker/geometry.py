"""영상 좌표 계산. OpenCV/YOLO 없이도 테스트할 수 있습니다."""
import math
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


def to_angle10(error_x: float, error_y: float, width: int, height: int,
               dfov_deg: float) -> tuple[int, int]:
    """픽셀 오차를 0.1° 단위 정수 각도 오차로 바꿉니다.

    dfov_deg는 카메라 대각선 화각입니다. 광각 렌즈는 비례식 오차가 커서 atan을 씁니다.
    카메라 기본 비율과 다른 해상도(예: 16:9 카메라를 4:3으로)는 화면이 잘려 화각이 달라질 수 있습니다.
    """
    half_diag = math.hypot(width, height) / 2
    focal = half_diag / math.tan(math.radians(dfov_deg / 2))  # 픽셀 단위 초점거리
    return (round(math.degrees(math.atan(error_x / focal)) * 10),
            round(math.degrees(math.atan(error_y / focal)) * 10))


def pick_target(detections, locked_id):
    """제어에 쓸 대상 하나를 고릅니다. 추적 중인 ID를 우선하고, 없으면 신뢰도 최대."""
    if not detections:
        return None
    if locked_id is not None:
        for d in detections:
            if d.track_id == locked_id:
                return d
    return max(detections, key=lambda d: d.confidence)
