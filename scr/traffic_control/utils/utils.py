from dataclasses import dataclass, field
from collections import deque
from time import monotonic


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
    