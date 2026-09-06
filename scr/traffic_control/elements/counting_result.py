from dataclasses import dataclass, field


@dataclass
class CountingResult:
    info: dict = field(default_factory=dict)         # итоговая статистика по кадру
    buffer_tracks: dict | None = None                  # буфер треков за окно анализа
    