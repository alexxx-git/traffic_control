
from dataclasses import dataclass, field
import numpy as np


@dataclass
class DetectionResult:
    xyxy: np.ndarray = field(default_factory=lambda: np.empty((0, 4)))
    cls: np.ndarray = field(default_factory=lambda: np.empty((0,), dtype=int))
    conf: np.ndarray = field(default_factory=lambda: np.empty((0,)))