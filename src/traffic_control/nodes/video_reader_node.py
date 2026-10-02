import cv2 as cv
import time
import logging
from traffic_control.elements import FrameElement,RawFrame
import os
logger=logging.getLogger(__name__)

class VideoReader:
    def __init__(self, config: dict) -> None:
        if config["src"] == "rtsp":
            self.video_path = (
                f"rtsp://{config['user']}:{config['password']}"
                f"@{config['host']}:{config['port']}{config['path']}"
            )
        else:
            self.video_path = config["src"]
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
        self.is_live = config["src"] == "rtsp"
        self.stream = self._open()
        self.skip_time = config["skip_time"]
        self._start_time = time.monotonic()
        self.last_frame_time = 0
        self.target_dt = 1.0 / (self.stream.get(cv.CAP_PROP_FPS) or 30)

    def _open(self):
        return cv.VideoCapture(
            self.video_path,
            cv.CAP_FFMPEG,
            [cv.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000,
             cv.CAP_PROP_READ_TIMEOUT_MSEC, 5000],
        )

    def process(self):
        frame_number = 0
        failures = 0
        backoff = 1.0
        MAX_FAILURES = 10
        MAX_BACKOFF = 30.0

        while True:
            ok, frame = self.stream.read()
            if not ok:
                if not self.is_live:
                    logger.info("End video file")
                    return
                failures += 1
                logger.warning(f"Can't read frame ({failures}/{MAX_FAILURES})")
                if failures >= MAX_FAILURES:
                    logger.warning(f"Reconnecting in {backoff:.0f}s...")
                    self.stream.release()
                    time.sleep(backoff)
                    self.stream = self._open()
                    backoff = min(backoff * 2, MAX_BACKOFF)
                    failures = 0
                else:
                    time.sleep(0.05)
                continue

            failures = 0
            backoff = 1.0

            if not self.is_live:
                elapsed = time.monotonic() - self.last_frame_time
                if elapsed < self.target_dt:
                    time.sleep(self.target_dt - elapsed)
            self.last_frame_time = time.monotonic()

            if self.is_live:
                timestamp = (time.monotonic() - self._start_time) * 1000
            else:
                timestamp = self.stream.get(cv.CAP_PROP_POS_MSEC)
            frame_number += 1
            raw = RawFrame(source=self.video_path, frame=frame,
                           timestamp=timestamp, frame_num=frame_number)
            yield FrameElement(raw=raw)
