import cv2 as cv
import time
import pathlib as path
import logging
import json
from traffic_control.elements import FrameElement,RawFrame

logger=logging.getLogger(__name__)

class VideoReader:
    def __init__(self,config:dict) -> None:
        self.video_path=config["src"]
        self.stream=cv.VideoCapture(self.video_path)
        self.skip_time=config["skip_time"]
        self.last_frame_time=0
       
    def process(self):
        frame_number=0
        while True:
            succes, frame =self.stream.read()
            if not succes:
                logger.warning("Cant open frame from stream")
                break
            timestamp=self.stream.get(cv.CAP_PROP_POS_MSEC)
            # if (timestamp - self.last_frame_time) < self.skip_time:
            #     continue
            frame_number+=1
            raw=RawFrame(
                source=self.video_path,
                frame=frame,
                timestamp=timestamp,
                frame_num=frame_number)
            yield FrameElement(raw=raw)