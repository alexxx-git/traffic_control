import cv2 as cv
import time
import pathlib as path
import logging
import json
from elements import FrameElement

logger=logging.getLogger(__name__)

class VideoReader:
    def __init__(self,config:dict) -> None:
        self.videopath=config["src"]
        self.stream=cv.VideoCapture(self.video_path)
        self.skip_time=config["self.skip_time"]
        self.last_frame_time=0
        with open(config["zones"], "r") as file:
            raw_data_zones=json.load(file)
        self.zones_info={key: [int(value) for value in values] for key, values in raw_data_zones["main_road"].items()} #read main_road zones

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
            yield FrameElement(self.videopath,frame,timestamp,frame_number,self.zones_info)