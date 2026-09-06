
from dataclasses import dataclass


@dataclass
class DetectionResult:
    conf: list | None = None
    cls: list | None = None
    xyxy: list[list] | None = None
