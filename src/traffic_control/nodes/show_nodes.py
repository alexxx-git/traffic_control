import cv2 as cv
from traffic_control.utils import FPSCounter, count_time
from traffic_control.elements import FrameElement
import json
import numpy as np
from collections import Counter
COCO_CLASSES: dict[int, str] =  {
        2: "car",
        3: "motorcycle",
        5: "bus",
        7: "truck",
    }
class ShowNode:

    def __init__(self,config)->None:
        config_show_node=config["show_node"]
        self.scale=config_show_node["scale"]
        self.imshow=config_show_node["imshow"]
        self.show_counting = config_show_node["show_counting"]

        self.fps_window_N_frames=config_show_node["fps_window_N_frames"]
        self.fps_counter=FPSCounter(self.fps_window_N_frames)

        self.back_layer_frame =None

        self.show_fps=config_show_node["show_fps"]
        self.show_roi_border=config_show_node["show_roi_border"]
        self.show_roi_detector_border=config_show_node["show_roi_detector_border"]

        self.show_zones=config_show_node["show_zones"]
        self.show_only_yolo_detection=config_show_node["show_only_yolo_detection"]
        
        with open(config["general"]["zones"], "r") as file:
            raw_zones = json.load(file)
        self.zones = {
            name: {"points": np.array(data["points"], dtype=np.int32), "color": tuple(data["color"])}
            for name, data in raw_zones.items()
        }

        with open(config["general"]["roi"], "r") as file:
            raw_roi = json.load(file)
        self.roi_show_box = tuple(raw_roi["show"]["box"])
        self.roi_show_color = tuple(raw_roi["show"]["color"])
        self.roi_detection_box = tuple(raw_roi["detection"]["box"])
        self.roi_detection_color = tuple(raw_roi["detection"]["color"])        
            
        self.fontFace = 1
        self.fontScale = 2.0
        self.thickness = 2


    @count_time
    def process(self,frame_element:FrameElement, fps_counter=None):
        frame_result=frame_element.raw.frame.copy()
        if self.show_only_yolo_detection :
            #yolo detection
            for box, class_name in zip(frame_element.detection.xyxy, frame_element.detection.cls):
                x1,y1,x2,y2=box
                cv.rectangle(frame_result,(x1,y1),(x2,y2),(0,0,0),2)
                cv.putText(frame_result, class_name,(x1,y1-10),
                            fontFace=self.fontFace,
                            fontScale=self.fontScale,
                            thickness=self.thickness,
                            color=(0, 0, 255),
                           )
        else :
            # tracking
            for box,class_id, id in zip(frame_element.tracking.xyxy,
                                          frame_element.tracking.cls,
                                          frame_element.tracking.id_list):
                if not self._is_center_inside_roi(box,self.roi_show_box): #work with edges
                    continue
                x1,y1,x2,y2=box
                cv.rectangle(frame_result,(x1,y1),(x2,y2),(50,25,50),2)

                class_name = COCO_CLASSES.get(class_id, "unknown")
                cv.putText(frame_result,f"{class_name}, {id}",(x1,y1-10),
                                                       fontFace=self.fontFace,
                            fontScale=self.fontScale,
                            thickness=self.thickness,
                            color=(0, 0, 255),
                           )
                #code below may be insert to init..
        if self.show_roi_border:
            x1, y1, x2, y2 = self.roi_show_box
            cv.rectangle(frame_result, (x1, y1), (x2, y2), self.roi_show_color, 2)# cian color for border roi

        if self.show_roi_detector_border:
            x1, y1, x2, y2 = self.roi_detection_box
            cv.rectangle(frame_result, (x1, y1), (x2, y2), self.roi_detection_color, 2) # yellow color for border detection
        
        if self.show_zones: # show in_out zones
            if self.back_layer_frame is None:
                self.back_layer_frame=self.add_layer(np.zeros((frame_result.shape), dtype=np.uint8),self.zones["0"]["points"],mask_color=(self.zones["0"]["color"]))
                self.back_layer_frame=self.add_layer(self.back_layer_frame,self.zones["1"]["points"],mask_color=self.zones["1"]["color"])
            frame_result=cv.addWeighted(self.back_layer_frame,1, frame_result, 1, 0)
            #*****
        if self.show_fps:
            if fps_counter is None:
                fps_counter = self.fps_counter
            fps_real = fps_counter.calc_fps()
            text_fps=f"FPS: {fps_real:.1f}"
            cv.putText(
                frame_result,
                text_fps,
                (10,40),
                fontFace=self.fontFace,
                fontScale=self.fontScale,
                thickness=self.thickness,
                color=(255, 255, 255),
            )
        if self.show_counting:
            self._draw_counting_info(frame_result, frame_element.counting.info)
            frame_element.frame_result=frame_result
        frame_show=cv.resize(frame_result.copy(), (-1, -1), fx=self.scale, fy=self.scale)
        if self.imshow:
            cv.imshow(frame_element.raw.source,frame_show)
            if cv.waitKey(1) & 0xFF == ord("q"):
                exit

        return frame_element
    
    def add_layer(self,img, points, mask_color=(0, 255, 255), alpha=0.3):
            bin_mask = np.zeros((img.shape[:2]), dtype=np.uint8)
            bin_mask = cv.fillPoly(bin_mask, pts=[points], color=1)
            colored_mask = (bin_mask[:, :, np.newaxis] * mask_color).astype(np.uint8)
            return cv.addWeighted(img, 1, colored_mask, alpha, 0)
    @staticmethod
    def _is_center_inside_roi(box, roi_box):
        x1, y1, x2, y2 = box
        rx1, ry1, rx2, ry2 = roi_box
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        return rx1 <= cx <= rx2 and ry1 <= cy <= ry2

    def _draw_counting_info(self, frame, counting_info: dict[str, Counter]) -> None:
        y = 80 if self.show_fps else 40
        line_height = 30
        for direction in ("in", "out"):
            label = "IN:" if direction == "in" else "OUT:"
            cv.putText(
                frame, label, (10, y),
                fontFace=self.fontFace, fontScale=self.fontScale,
                thickness=self.thickness, color=(255, 255, 255),
            )
            y += line_height

            for cls_id, count in sorted(counting_info[direction].items()):
                class_name = COCO_CLASSES.get(cls_id, "unknown")
                text = f"{count} {class_name}"
                cv.putText(
                    frame, text, (10, y),
                    fontFace=self.fontFace, fontScale=self.fontScale,
                    thickness=self.thickness, color=(255, 255, 255),
                )
                y += line_height
    