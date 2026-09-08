from ultralytics import YOLO
import cv2 as cv
import torch
import numpy as np
from utils.utils import count_time
from collections import deque
from elements.frame_element import FrameElement


class DetectionTrackingNodes:
    def __init__(self, config)-> None:
        device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Compute will be on device: {device}")

        config_yolo=config["detection_node"]
        self.model = YOLO(config_yolo["weight_path"])
        self.model.fuse()
        self.classes = self.model.names
        self.conf = config_yolo["confidence"]
        self.iou = config_yolo["iou"]
        self.imgsz = config_yolo["imgsz"]
        self.classes_to_detect = config_yolo["classes_to_detect"]
    @count_time
    def process(self, frame_element:FrameElement):
        frame=frame_element.raw.frame.copy()
        out=self.model.track(
            frame,
            persist=True, 
            # tracker="bytetrack.yaml", 
            classes=self.classes_to_detect,
            iou =self.iou,
            verbose=False, 
            conf=self.conf)[0]
        if out.boxes and out.boxes.is_track:
            frame_element.tracking.xyxy = out.boxes.xyxy.cpu().numpy().astype(int)
            frame_element.tracking.conf= out.boxes.conf.cpu().numpy()
            frame_element.tracking.id_list= out.boxes.id.int().cpu().numpy()
            frame_element.tracking.cls=out.boxes.cls.int().cpu().numpy()
    
