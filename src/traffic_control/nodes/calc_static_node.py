import cv2 as cv
import numpy as np
from traffic_control.utils import count_time
from traffic_control.elements import FrameElement
from collections import Counter
import json
import time
class ZoneCounter:
    def __init__(self, max_age:float=30) -> None:
        self.last_zone: dict[int,int]={}
        self.last_seen_time: dict[int,float]={}
        self.counts: dict[str,Counter]={
            "in": Counter(),
            "out": Counter(),
        }
        self.max_age=max_age

    def update(self,track_id:int, current_zone:int|None,cls:int, timestep:float)-> None:
        self.last_seen_time[track_id]=timestep
        if current_zone is None:
            return
        prev_zone=self.last_zone.get(track_id)
        if prev_zone is not None and prev_zone!=current_zone:
            direction="in" if prev_zone=='0' else "out"
            if direction in self.counts:
                self.counts[direction][cls]+=1
        self.last_zone[track_id]=current_zone
    def cleanup(self,current_timestamp:float) -> None:
        inactive=[tid for tid, t in self.last_seen_time.items() if current_timestamp-t>self.max_age]
        for tid in inactive:
            del self.last_zone[tid]
            del self.last_seen_time[tid]


class CalcStaticNode:
    def __init__(self,config)->None:
        self.config=config["calculate_node"]
        self.max_age_seconds=self.config["max_age_seconds"]
        self.zone_counter=ZoneCounter(self.max_age_seconds)
        with open(config["general"]["zones"], "r") as file:
            raw_zones = json.load(file)
        self.zones = {
            name: {"points": np.array(data["points"], dtype=np.int32)}
            for name, data in raw_zones.items()
        }
    @count_time
    def process(self,frame_element:FrameElement)->FrameElement:
        now = time.monotonic()
        for box,track_id, cls in zip(
            frame_element.tracking.xyxy,
            frame_element.tracking.id_list,
            frame_element.tracking.cls):
            x1,y1,x2,y2=box
            bottom_center_bb=(float((x2+x1)/2),float(((y1+y2)/2+y2)/2)) #some above then bottom center
            current_zone=self.get_current_zone(bottom_center_bb,self.zones)
            self.zone_counter.update(track_id,current_zone,cls,now)
        frame_element.counting.info=self.zone_counter.counts
        return frame_element

    @staticmethod
    def get_current_zone(point,zones:dict[str,dict])->str|None:
        for zone_name,zone_data in zones.items():
            if cv.pointPolygonTest(zone_data["points"],point,measureDist=False)>=0:
                return zone_name
        return None


