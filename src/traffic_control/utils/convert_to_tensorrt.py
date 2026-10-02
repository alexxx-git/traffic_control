from ultralytics import YOLO

model = YOLO("/home/alex/Projects/traffic_control/weights/yolo26x.pt")
model.export(
    format="engine",
    imgsz=640,         
    quantize=16,        
    device=0,
    workspace=10,        # Gb or None
)