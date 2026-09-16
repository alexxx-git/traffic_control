import cv2 as cv
import time
import logging
from traffic_control.elements import FrameElement,RawFrame

logger=logging.getLogger(__name__)

class VideoReader:
    def __init__(self,config:dict) -> None:
        self.video_path = config["src"]
        self.stream = cv.VideoCapture(self.video_path)
        self.skip_time = config["skip_time"]
        self.is_live = self.stream.get(cv.CAP_PROP_FRAME_COUNT) <= 0
        self._start_time = time.monotonic()
        self.last_frame_time = 0
        self.target_dt = 1.0 / (self.stream.get(cv.CAP_PROP_FPS) or 30)
       
    def process(self):
        frame_number = 0
        while True:
            succes, frame = self.stream.read()
            if not succes:
                logger.warning("Cant open frame from stream")
                break

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
            yield FrameElement(raw=raw)