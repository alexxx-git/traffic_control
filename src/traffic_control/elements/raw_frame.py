from dataclasses import dataclass
import numpy as np


@dataclass
class RawFrame:
    source: str     # Путь к видео или номер камеры с которой берём поток
    frame: np.ndarray     # Кадр в BGR формате
    timestamp: float     # Время с начала потока (в секундах)
    frame_num: int     # Номер кадра в потоке
    back_layer_frame: np.ndarray
