import time
import threading
import cv2 as cv
from flask import Flask, Response, render_template
from traffic_control.utils import count_time
from traffic_control.elements import FrameElement


class VideoServerNode:
    def __init__(self, config) -> None:
        config_server = config["video_server_node"]
        self.host_ip = config_server["host_ip"]
        self.port = config_server["port"]
        self.index_page = config_server["index_page"]
        self.stream_fps = config_server.get("stream_fps", 8)

        self._jpeg: bytes | None = None
        self._frame_id = 0
        self._last_encode = 0.0
        self._cond = threading.Condition()

        self.app = Flask(__name__, template_folder=config_server["template_folder"])
        self.app.add_url_rule("/", "index", lambda: render_template(self.index_page))
        self.app.add_url_rule("/video", "video", self._video)

        self._thread = threading.Thread(
            target=self.app.run,
            kwargs=dict(host=self.host_ip, port=self.port, threaded=True, use_reloader=False),
            daemon=True,
        )
        self._thread.start()

    def _gen(self):
        last_id = -1
        while True:
            with self._cond:
                self._cond.wait_for(lambda: self._frame_id != last_id, timeout=5)
                if self._frame_id == last_id:
                    continue
                jpeg, last_id = self._jpeg, self._frame_id
            yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpeg + b"\r\n")

    def _video(self):
        return Response(self._gen(), mimetype="multipart/x-mixed-replace; boundary=frame")

    @count_time
    def process(self, frame_element: FrameElement) -> FrameElement:
        now = time.monotonic()
        if now - self._last_encode >= 1 / self.stream_fps:
            self._last_encode = now
            small = cv.resize(frame_element.frame_result, None, fx=0.5, fy=0.5)
            ok, jpeg = cv.imencode(".jpg", small, [cv.IMWRITE_JPEG_QUALITY, 60])
            if ok:
                with self._cond:
                    self._jpeg = jpeg.tobytes()
                    self._frame_id += 1
                    self._cond.notify_all()
        return frame_element