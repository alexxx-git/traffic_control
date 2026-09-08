import cv2 as cv
from utils.utils import FPSCounter, count_time
from elements import FrameElement
import json
import numpy as np

COCO_CLASSES: dict[int, str] =  {
        2: "car",
        3: "motorcycle",
        5: "bus",
        7: "truck",
    }
class ShowNode:

    def __init__(self,config)->None:
        data_zones_colors=config["general"]["colors_of_zones"]
        self.zones_colors={key: tuple(value) for key, value in data_zones_colors.items()}
        config_show_node=config["show_node"]
        self.scale=config_show_node["scale"]
        self.imshow=config_show_node["imshow"]

        self.fps_window_N_frames=config_show_node["fps_window_N_frames"]
        self.fps_counter=FPSCounter(self.fps_window_N_frames)

        self.show_fps=config_show_node["show_fps"]
        self.show_roi_border=config_show_node["show_roi_border"]
        self.show_roi_detector_border=config_show_node["show_roi_detector_border"]

        self.show_zones=config_show_node["show_zones"]
        self.show_only_yolo_detection=config["show_only_yolo_detection"]
        
        with open(config["zones"], "r") as file:
            raw_data_zones=json.load(file)
        self.roi_road={key: [int(value) for value in values] for key, values in raw_data_zones["roi_count_road"].items()} #read main_road zones
        
        self.fontFace = 1
        self.fontScale = 2.0
        self.thickness = 2

 
    @count_time
    def process(self,frame_element:FrameElement, fps_counter=None):


        frame_result=frame_element.raw.frame.copy()
        back_layer_frame=frame_element.raw.back_layer_frame
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
                x1,y1,x2,y2=box
                color=(50,25,50)
                cv.rectangle(frame_result,(x1,y1),(x2,y2),color,2)

                class_name = COCO_CLASSES.get(class_id, "unknown")
                cv.putText(frame_result,f"{class_name}, {id}",(x1,y1-10),
                                                       fontFace=self.fontFace,
                            fontScale=self.fontScale,
                            thickness=self.thickness,
                            color=(0, 0, 255),
                           )
        if self.show_roi_border:
            cv.rectangle(frame_result,self.roi_road["show"],(255,221,0),2) # cian color for border roi
        if self.show_roi_detector_border:
            cv.rectangle(frame_result,self.roi_road["detection"],(0,225,255),2) # yellow color for border detection
        
        if self.show_zones: # show in_out zones
            if back_layer_frame is None:
                back_layer_frame=self.add_layer(np.zeros((frame_result.shape), dtype=np.uint8),frame_element.zones_info[1],mask_color=(0, 255, 0))
                back_layer_frame=self.add_layer(back_layer_frame,frame_element.zones_info[2],mask_color=(0, 0, 255))
                frame_element.raw.back_layer_frame=back_layer_frame
            frame_result=cv.addWeighted(back_layer_frame,1, frame_result, 1, 0)
        if self.show_fps:
            if fps_counter is None:
                fps_counter = self.fps_counter
            fps_real = fps_counter.calc_FPS()
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
        frame_element.frame_result=frame_result
        frame_show=cv.resize(frame_result.copy(), (-1, -1), fx=self.scale, fy=self.scale)
        if self.imshow:
            cv.imshow(frame_element.raw.source,frame_show)
            cv.waitKey(1)
        return frame_element
    
    def add_layer(self,img, points, mask_color=(0, 255, 255), alpha=0.3):
            bin_mask = np.zeros((img.shape[:2]), dtype=np.uint8)
            bin_mask = cv.fillPoly(bin_mask, pts=[points], color=1)
            colored_mask = (bin_mask[:, :, np.newaxis] * mask_color).astype(np.uint8)
            return cv.addWeighted(img, 1, colored_mask, alpha, 0)


    