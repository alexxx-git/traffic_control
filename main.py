from logging import config

import hydra
from traffic_control.nodes import VideoReader,DetectionTrackingNodes, ShowNode, CalcStaticNode, VideoServerNode, KafkaProducerNode
from traffic_control.utils import metrics_buffer
from dotenv import load_dotenv
load_dotenv()  

@hydra.main(version_base=None, config_path="configs", config_name="app_config")
def main(config) -> None:
    print("Hello from traffic-control!")
    video_reader=VideoReader(config["video_reader"])
    detection_node = DetectionTrackingNodes(config)
    show_node = ShowNode(config)
    calc_static_node=CalcStaticNode(config)
    video_server_node=VideoServerNode(config)
    kafka_node = KafkaProducerNode(config)
    try:
            for frame_element in video_reader.process():
                frame_element = detection_node.process(frame_element)
                frame_element = calc_static_node.process(frame_element)
                frame_element = kafka_node.process(frame_element)
                frame_element = show_node.process(frame_element)
                frame_element = video_server_node.process(frame_element)

    finally:
        kafka_node.close()
if __name__ == "__main__":
    main()
