import time
import threading
import cv2 as cv
import numpy as np
from flask import Flask, Response, render_template


class VideoServerNode:
    def __init__(self,config)->None:
        config_server=config["video_server_node"]
        self.app=Flask(__name__,template_folder=config_server["template_folder"])
        self.app.add_url_rule("/", "index", lambda: render_template(config_server["index_page"]))
        self.app.add_url_rule("/video", "video",self._video)
        self.host_ip=config_server["host_ip"]
        self.port=config_server["port"]
        self.index_page = config_server["index_page"]
        self._frame=np.zeros(shape=(640, 480), dtype=np.uint8)
        self._lock=threading.Lock()
        self._thread=threading.Thread(
            target=self.app.run,
            kwargs=dict(host=self.host_ip, port=self.port, threaded=True, use_reloader=False),
            daemon=True,
        )
        self._thread.start()
    def _gen(self):
        while True:
            with self._lock:
                frame=self._frame
            ok,jpeg =cv.imencode(".jpg",frame)
            if ok:
                yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
                       + jpeg.tobytes() + b"\r\n")
            time.sleep(1 / 25)
    def _video(self):
       return Response(self._gen(), mimetype="multipart/x-mixed-replace; boundary=frame")

    def update_image(self, image: np.ndarray):
        with self._lock:
            self._frame = image