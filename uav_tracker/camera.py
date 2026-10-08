"""입력 전용 모듈. 제조사 SDK 카메라로 교체할 때 이 경계를 사용하세요."""
import cv2


class Camera:
    """read()는 OpenCV 표준인 BGR uint8 영상 하나를 반환합니다."""

    def __init__(self, index=0, backend="dshow", width=1280, height=720, fps=30):
        backends = {"auto": cv2.CAP_ANY, "dshow": cv2.CAP_DSHOW, "msmf": cv2.CAP_MSMF}
        self.cap = cv2.VideoCapture(index, backends[backend])
        if not self.cap.isOpened():
            self.close()
            raise RuntimeError("카메라를 열 수 없습니다. --camera 1 또는 --backend msmf/auto를 시도하세요.")
        # 요청값입니다. 지원하지 않는 해상도/FPS는 카메라가 무시할 수 있습니다.
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, fps)

    def read(self):
        ok, frame = self.cap.read()
        if not ok or frame is None or frame.size == 0:
            raise RuntimeError("카메라 프레임을 읽지 못했습니다. 연결과 다른 앱의 카메라 사용을 확인하세요.")
        return frame

    def close(self):
        self.cap.release()
