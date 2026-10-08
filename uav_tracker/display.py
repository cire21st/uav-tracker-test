"""검출 결과를 화면에 표시합니다. 원본 프레임 크기를 그대로 사용합니다."""
import cv2


def draw(frame, detections, fps, mode):
    height, width = frame.shape[:2]
    cv2.drawMarker(frame, (width // 2, height // 2), (255, 200, 0),
                   cv2.MARKER_CROSS, 20, 2)
    for detection in detections:
        x1, y1, x2, y2 = map(round, detection.xyxy)
        point = detection.coordinates(width, height)
        cx, cy = round(point["cx"]), round(point["cy"])
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
        # OpenCV 기본 글꼴은 한글을 지원하지 않아 화면 표시는 영어를 사용합니다.
        label = f"{detection.name} {detection.confidence:.2f} ID={detection.track_id}"
        lines = [label, f"center=({cx},{cy})",
                 f"error=({point['error_x']:+.1f},{point['error_y']:+.1f})"]
        for i, text in enumerate(lines):
            y = min(height - 8, max(20, y1) + i * 20)
            cv2.putText(frame, text, (max(0, x1), y), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 0), 1, cv2.LINE_AA)
    cv2.putText(frame, f"{mode} | FPS {fps:.1f} | objects {len(detections)} | Q / Esc: quit",
                (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    return frame
