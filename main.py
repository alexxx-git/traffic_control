import hydra
from traffic_control.nodes import VideoReader,DetectionTrackingNodes, ShowNode, CalcStaticNode
# from src.traffic_control.utils import check_and_set_env_var
@hydra.main(version_base=None, config_path="configs", config_name="app_config")
def main(config) -> None:
    print("Hello from traffic-control!")
    video_reader=VideoReader(config["video_reader"])
    detection_node = DetectionTrackingNodes(config)
    show_node = ShowNode(config)
    calc_static_node=CalcStaticNode(config)
    
    for frame_element in video_reader.process():
        frame_element = detection_node.process(frame_element)
        frame_element= calc_static_node.process(frame_element)
        frame_element = show_node.process(frame_element)
if __name__ == "__main__":
    main()
