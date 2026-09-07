from dataclasses import dataclass


@dataclass
class TrackingResult:
    conf: list | None = None
    cls: list | None = None
    xyxy: list[list] | None = None
    id_list: list | None = None    # id отслеживаемых объектов
    