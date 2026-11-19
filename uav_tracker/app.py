"""실행 옵션과 전체 처리 흐름. --help는 패키지 설치 전에도 볼 수 있습니다."""
import argparse
import json
import sys
import time


def positive(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("0보다 큰 정수를 입력하세요.")
    return number


def parse_args():
    parser = argparse.ArgumentParser(description="웹캠 YOLO 검출/추적 및 중심 좌표 출력")
    parser.add_argument("--camera", type=int, default=0, help="카메라 번호 (기본 0)")
    parser.add_argument("--backend", choices=["dshow", "msmf", "auto"], default="dshow")
    parser.add_argument("--width", type=positive, default=1280)
    parser.add_argument("--height", type=positive, default=720)
    parser.add_argument("--fps", type=positive, default=30, help="카메라 요청 FPS")
    parser.add_argument("--model", default="models/best.pt", help="모델 경로 (기본: UAV 전용 models/best.pt)")
    parser.add_argument("--mode", choices=["detect", "track"], default="track")
    parser.add_argument("--tracker", choices=["bytetrack.yaml", "botsort.yaml"], default="bytetrack.yaml")
    parser.add_argument("--conf", type=float, default=0.50, help="탐지 신뢰도 임계값 (기본 0.50)")
    parser.add_argument("--imgsz", type=positive, default=640)
    parser.add_argument("--device", default="cpu", help="cpu 또는 CUDA GPU 번호 0")
    parser.add_argument("--classes", type=int, nargs="+", help="클래스 번호. 기본 UAV 모델: 쿼드콥터 0, 고정익 1")
    parser.add_argument("--print-every", type=positive, default=10, help="N 프레임마다 콘솔 출력; 1은 매 프레임")
    parser.add_argument("--udp", nargs="?", const="127.0.0.1:5005", metavar="HOST:PORT",
                        help="control.py로 매 프레임 dx,dy,flag 전송 (권장). 값 생략 시 127.0.0.1:5005")
    parser.add_argument("--serial", metavar="PORT",
                        help="아두이노로 A,dx,dy,flag 직접 전송 (control.py 없이 시험할 때). COM5 또는 auto")
    parser.add_argument("--baud", type=positive, default=115200)
    parser.add_argument("--dfov", type=float, default=95.8, help="카메라 대각선 화각(도), 기본 95.8")
    args = parser.parse_args()
    if args.udp and args.serial:
        parser.error("--udp와 --serial은 함께 쓸 수 없습니다. 보통은 --udp만 쓰세요.")
    if args.udp:
        from .serial_link import parse_udp_target  # 표준 라이브러리만 쓰므로 --help 전에도 가볍습니다.
        try:
            parse_udp_target(args.udp)
        except ValueError as exc:
            parser.error(str(exc))
    if not 0 < args.dfov < 180:
        parser.error("--dfov는 0~180 사이여야 합니다.")
    if not 0 <= args.conf <= 1:
        parser.error("--conf는 0~1 사이여야 합니다.")
    if args.camera < 0 or (args.classes and min(args.classes) < 0):
        parser.error("카메라/클래스 번호는 0 이상이어야 합니다.")
    return args


def main():
    args = parse_args()
    # 지연 import: --help는 OpenCV나 torch를 불러오지 않습니다.
    try:
        import cv2
        from .camera import Camera
        from .detector import Detector
        from .display import draw
        from .geometry import pick_target, to_control_values
        from .serial_link import SerialLink, UdpLink, resolve_port
    except ImportError as exc:
        print(f"필수 패키지 로드 실패: {exc}\npython -m pip install -r requirements.txt", file=sys.stderr)
        return 1

    camera = None
    link = None
    try:
        # 모델·카메라를 열기 전에 포트부터 찾아서, 못 찾으면 바로 알려줍니다.
        port = resolve_port(args.serial) if args.serial else None
        detector = Detector(args.model, args.mode, args.tracker, args.conf,
                            args.imgsz, args.device, args.classes)
        camera = Camera(args.camera, args.backend, args.width, args.height, args.fps)
        if port:
            link = SerialLink(port, args.baud)
            print(f"시리얼 연결: {port} @ {args.baud} (아두이노로 직접 전송)", flush=True)
        elif args.udp:
            link = UdpLink(args.udp)
            print(f"UDP 전송: {link.address[0]}:{link.address[1]} (control.py 수신)", flush=True)
        locked_id = None
        message = None
        frame_number = 0
        window = "UAV Tracker"
        cv2.namedWindow(window, cv2.WINDOW_NORMAL)
        while True:
            started = time.perf_counter()
            frame = camera.read()
            height, width = frame.shape[:2]  # 요청 해상도가 아닌 실제 영상 기준
            detections = detector.process(frame)
            frame_number += 1
            if link is not None:
                # 출력 주기와 무관하게 매 프레임 전송합니다. 놓쳐도 valid=0을 보내 하트비트로 씁니다.
                target = pick_target(detections, locked_id)
                if target is None:
                    message = link.send(0, 0, 0)
                else:
                    locked_id = target.track_id
                    point = target.coordinates(width, height)
                    dx, dy = to_control_values(point["error_x"], point["error_y"],
                                               width, height, args.dfov)
                    message = link.send(dx, dy, 1)
            if frame_number == 1 or frame_number % args.print_every == 0:
                objects = [dict(class_id=d.class_id, name=d.name, confidence=d.confidence,
                                track_id=d.track_id, **d.coordinates(width, height)) for d in detections]
                # 빈 목록은 현재 검출 없음입니다. 이전 좌표를 재사용하지 않습니다.
                print(json.dumps(dict(frame=frame_number, width=width, height=height,
                                      objects=objects, sent=message),
                                 ensure_ascii=False), flush=True)
            fps = 1 / max(time.perf_counter() - started, 1e-9)
            cv2.imshow(window, draw(frame, detections, fps, args.mode))
            if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                break
            if cv2.getWindowProperty(window, cv2.WND_PROP_VISIBLE) < 1:
                break
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        print(f"실행 실패: {exc}", file=sys.stderr)
        return 1
    finally:
        # 오류나 Ctrl+C로 종료해도 다른 앱에서 카메라를 다시 사용할 수 있게 반환합니다.
        if camera is not None:
            camera.close()
        if link is not None:
            link.send(0, 0, 0)  # 종료 직전 '놓침'을 알려 모터가 멈추게 합니다.
            link.close()
        cv2.destroyAllWindows()
    return 0
