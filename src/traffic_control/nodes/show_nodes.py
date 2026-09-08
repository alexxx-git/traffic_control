import cv2 as cv
from utils.utils import FPSCounter
from elements import FrameElement


class ShowNode:
    def __init__(self,config)->None:
        zones_colors=config["general"]["colors_of_zones"]