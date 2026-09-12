import time
import threading
import cv2 as cv
import numpy as np
from flask import Flask, Response, render_template


class VideoServerNode:
    def __init__(self,config)->None:
        self.app=Flask(__name__,template_folder=config["template_folder"])
        
        self.app.add_url_rule("/", "index", lambda: render_template(config["index_page"]))