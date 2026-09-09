from ultralytics import YOLO
import cv2 as cv
import torch
import numpy as np
from traffic_control.utils import count_time
from traffic_control.utils import ClassSmoother
from traffic_control.elements import FrameElement
import json

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
        self.only_roi_area_detect=config_yolo["only_roi_area_detect"]
        self.classes_to_detect = config_yolo["classes_to_detect"]
        with open(config["general"]["roi"], "r") as file:
            raw_roi = json.load(file)
        self.detection_roi_box = tuple(raw_roi["detection"]["box"])
        self.class_smoother=ClassSmoother()

    @count_time
    def process(self, frame_element:FrameElement):
        frame=frame_element.raw.frame.copy()
        x1, y1, x2, y2 = self.detection_roi_box 
        out=self.model.track(
            frame[y1:y2, x1:x2],
            persist=True, 
            tracker="bytetrack.yaml", 
            classes=self.classes_to_detect,
            iou =self.iou,
            verbose=False, 
            conf=self.conf)[0]
        if out.boxes and out.boxes.is_track:
            xyxy = out.boxes.xyxy.cpu().numpy().astype(int)
            xyxy[:, [0, 2]] += x1
            xyxy[:, [1, 3]] += y1
            frame_element.tracking.xyxy = xyxy
            frame_element.tracking.conf= out.boxes.conf.cpu().numpy()
            smoothed_cls=np.array([
                self.class_smoother.update(tid,cls, conf)
                for tid, cls, conf in zip
                (out.boxes.id.int().cpu().numpy(),
                 out.boxes.cls.int().cpu().numpy(),
                 out.boxes.conf.cpu().numpy())
                ])
            frame_element.tracking.id_list= out.boxes.id.int().cpu().numpy()
            frame_element.tracking.cls=smoothed_cls
            self.class_smoother.cleanup(set(frame_element.tracking.id_list.tolist()))
        return frame_element
