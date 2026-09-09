from dataclasses import dataclass, field
from collections import deque, Counter,defaultdict
from time import monotonic
import os
import functools
import time
import logging

logger_profile=logging.getLogger("profile")
@dataclass
class FPSCounter:
    max_frames: int = 30
    current_frames: deque = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.max_frames <= 1:
            raise ValueError("max_frames must be greater than 1")
        self.current_frames = deque(maxlen=self.max_frames)

    def calc_fps(self) -> float:
        """Record a time frame and return the FPS."""
        self.current_frames.append(monotonic())

        if len(self.current_frames) < 2:
            return 0.0

        elapsed = self.current_frames[-1] - self.current_frames[0]
        return (len(self.current_frames) - 1) / elapsed if elapsed > 0 else 0.0       

    
def check_and_set_env_var(var_name,value_new):
    value=os.getenv(var_name)
    if value is None:
        os.environ[var_name]=str(value_new)
        print(f"{var_name} was empty. Now value is {value_new}")
    else:
        print(f"Variable {var_name} was set to {value}already!")

def count_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        t_start=time.monotonic()
        out=func(*args, **kwargs)
        t_end=time.monotonic()
        delta_time_ms=(t_end-t_start)*1000
        owner=args[0].__class__.__name__ if args else func.__module__
        logger_profile.debug(f"{owner}.{func.__name__}, time spent {delta_time_ms:.2f} msecs")
        return out
    return wrapper
class ClassSmoother:
    def __init__(self) -> None:
        self._class_votes:dict[int,Counter] = defaultdict(Counter)
    def update(self,track_id:int,cls:int,conf)->int:
        track_id=int(track_id)
        cls=int(cls)
        self._class_votes[track_id][cls]+=conf
        return self._class_votes[track_id].most_common(1)[0][0]
    def cleanup(self, active_ids: set[int]) -> None:
        inactiv_ids = set(self._class_votes) - active_ids
        for tid in inactiv_ids:
            del self._class_votes[tid]