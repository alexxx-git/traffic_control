from dataclasses import dataclass, field
import time
import numpy as np

from .raw_frame import RawFrame
from .detection_result import DetectionResult
from .tracking_result import TrackingResult
from .counting_result import CountingResult


@dataclass
class FrameElement:
    raw: RawFrame
    detection: DetectionResult = field(default_factory=DetectionResult)
    # tracking: TrackingResult = field(default_factory=TrackingResult)
    # counting: CountingResult = field(default_factory=CountingResult)
    frame_result: np.ndarray | None = None
    timestamp_date: float = field(default_factory=time.time)
    # send_info_of_frame_to_db: bool = False 
    zones_info: dict |None=None
