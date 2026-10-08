"""Ultralytics 결과를 앱에서 쓰기 쉬운 Detection 목록으로 변환합니다."""
from ultralytics import YOLO
from .geometry import Detection


class Detector:
    def __init__(self, model, mode, tracker, confidence, image_size, device, classes):
        self.model = YOLO(model)
        if self.model.task != "detect":
            raise ValueError("일반 bounding box detection 모델을 지정하세요 (분류/OBB 모델 제외).")
        self.mode, self.tracker = mode, tracker
        self.options = dict(conf=confidence, imgsz=image_size, device=device,
                            classes=classes, verbose=False)

    def process(self, frame):
        if self.mode == "track":
            # 같은 카메라의 연속 프레임이므로 이전 프레임의 추적 상태를 유지합니다.
            result = self.model.track(frame, persist=True, tracker=self.tracker,
                                      **self.options)[0]
        else:
            result = self.model.predict(frame, **self.options)[0]
        boxes = result.boxes
        if boxes is None:
            return []
        # GPU 텐서를 CPU로 옮긴 뒤 Python 숫자로 변환합니다.
        ids = boxes.id.int().cpu().tolist() if boxes.id is not None else [None] * len(boxes)
        return [Detection(tuple(xyxy), float(conf), int(cls), result.names[int(cls)], tid)
                for xyxy, conf, cls, tid in zip(boxes.xyxy.cpu().tolist(),
                    boxes.conf.cpu().tolist(), boxes.cls.cpu().tolist(), ids)]
