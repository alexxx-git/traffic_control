import cv2 as cv
import time
import pathlib as path
import logging

from elements import FrameElement

logger=logging.getLogger(__name__)

class VideoReader:
 def __init__(self,config:dict) -> None:
  self.stream=cv.VideoCapture(self.video_pth)
  