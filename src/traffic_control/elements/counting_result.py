from dataclasses import dataclass, field


@dataclass
class CountingResult:
    info: dict = field(default_factory=dict)
    debug_count:dict =    field(default_factory=dict)  
    buffer_tracks: dict | None = None               
    