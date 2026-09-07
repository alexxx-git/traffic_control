import cv2 as cv
import time
import pathlib as path
import logging

from elements import FrameElement

logger=logging.getLogger(__name__)

class VideoReader:
 def __init__(self,config:dict) -> None:
  self.videopath=config["src"]
  self.stream=cv.VideoCapture(self.video_path)
  self.skip_time=config["self.skip_time"]
  self.last_frame_time=0
  