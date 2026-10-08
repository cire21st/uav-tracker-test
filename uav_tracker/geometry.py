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
