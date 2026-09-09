import cv2 as cv
import numpy as np
from traffic_control.utils import count_time
from traffic_control.elements import FrameElement
from collections import Counter
class ZoneCounter():
    def __init__(self) -> None:
        self.last_zone: dict[int,str]={}
        self.counts: dict[str,Counter]={
            "left2right": Counter(),
            "right2left": Counter(),
        }

    def update(self,track_id:int, current_zone:str|None,cls:int)-> None:
        if current_zone is None:
            return
        prev_zone=self.last_zone.get(track_id)
        if prev_zone is not None and prev_zone!=current_zone:
            direction=f"{prev_zone}2{current_zone}"
            if direction in self.counts:
                self.counts[direction][cls]+=1
        self.last_zone[track_id]=current_zone
    def cleanup(self,active_ids:set[int]) -> None:
        inactive=set(self.last_zone)-active_ids
        for tid in inactive:
            del self.last_zone[tid]

