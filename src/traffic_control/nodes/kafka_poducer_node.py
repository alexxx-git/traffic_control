from kafka import KafkaProducer
from json import dumps
import time

from traffic_control.utils import count_time
from traffic_control.elements import FrameElement

class KafkaProducerNode:
    
    def __init__(self, config: dict) -> None:
        self.bootstrap_servers = config["kafka_producer_node"]["bootstrap_servers"]
        self.topic_name = f"statistics_{config['video_reader']['id']}"
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda x: dumps(x).encode('utf-8')
        )
        self.camera_id = config["video_reader"]["id"]

    @count_time
    def process(self, frame_element: FrameElement):
        events = frame_element.counting.info
        for ev in events:
            payload = {
                "camera_id": self.camera_id,
                "class": ev["class"],
                "direction": ev["direction"],
                "timestamp": int(time.time()),
            }
            self.producer.send(self.topic_name, value=payload)

        return frame_element

    def close(self):
        self.producer.flush() 