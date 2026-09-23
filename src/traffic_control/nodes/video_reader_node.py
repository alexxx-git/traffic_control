import cv2 as cv
import time
import logging
from traffic_control.elements import FrameElement,RawFrame
import os
logger=logging.getLogger(__name__)

class VideoReader:
    def __init__(self,config:dict) -> None:
        if config["src"] == "rtsp":
            self.video_path = (
                f"rtsp://{config['user']}:{config['password']}"
                f"@{config['host']}:{config['port']}{config['path']}"
            )
        else:
            self.video_path = config["src"]
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
        self.stream = cv.VideoCapture(self.video_path, cv.CAP_FFMPEG)
        self.skip_time = config["skip_time"]
        self.is_live = self.stream.get(cv.CAP_PROP_FRAME_COUNT) <= 0
        self._start_time = time.monotonic()
        self.last_frame_time = 0
        self.target_dt = 1.0 / (self.stream.get(cv.CAP_PROP_FPS) or 30)
       
    def process(self):
        frame_number = 0
        consecutive_failures = 0
        MAX_FAILURES = 1
        while True:
            succes, frame = self.stream.read()
            if not succes:
                consecutive_failures += 1
                logger.warning(f"Cant open frame from stream ({consecutive_failures}/{MAX_FAILURES})")
                if consecutive_failures >= MAX_FAILURES:
                    logger.warning("Reconnecting to stream...")
                    self.stream.release()
                    self.stream = cv.VideoCapture(self.video_path, cv.CAP_FFMPEG)
                    consecutive_failures = 0
                continue

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
            raw = RawFrame(source=self.video_path, frame=frame, timestamp=timestamp, frame_num=frame_number)
            consecutive_failures = 0
            yield FrameElement(raw=raw)
