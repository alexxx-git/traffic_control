import hydra
from traffic_control.nodes import VideoReader,DetectionTrackingNodes, ShowNode, CalcStaticNode, VideoServerNode
# from src.traffic_control.utils import check_and_set_env_var
@hydra.main(version_base=None, config_path="configs", config_name="app_config")
def main(config) -> None:
    print("Hello from traffic-control!")
    video_reader=VideoReader(config["video_reader"])
    detection_node = DetectionTrackingNodes(config)
    show_node = ShowNode(config)
    calc_static_node=CalcStaticNode(config)
    video_server_node=VideoServerNode(config)
    
    for frame_element in video_reader.process():
        frame_element = detection_node.process(frame_element)
        frame_element= calc_static_node.process(frame_element)
        frame_element = show_node.process(frame_element)
        video_server_node.update_image(frame_element.raw.frame) 
if __name__ == "__main__":
    main()
