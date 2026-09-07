from src.traffic_control.utils import check_and_set_env_var
import os
import hydra
from src.traffic_control.nodes import VideoReader


@hydra.main(version_base=None, config_path="config", config_name="app_config")
def main(config) -> None:
    print("Hello from traffic-control!")
    video_reader=VideoReader(config["video_reader"])
    

    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    check_and_set_env_var("TC_LOG_FILE_PATH", os.path.join(log_dir, "app.log"))

if __name__ == "__main__":
    main()
