from PySide2 import QtCore
from PySide2.QtCore import Slot

from .base import ComputeNode
from .params import StringParam, IntParam, PARAM
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG

from .image.imageparam import ImageParam

import sys

sys.path.append('D:\\projects\\python\\node2\\opencv')

from PIL import Image

import cv2
import numpy as np


class FaceDetect(ComputeNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'FaceDetect'

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(ImageParam(name='image', value=None, pluggable=INPUT_PLUG))
        self.params.append(ImageParam(name='image', value=None, pluggable=OUTPUT_PLUG))

        self.cascade = cv2.CascadeClassifier("D:/projects/python/node2/tmp/haarcascade_frontalface_default.xml")

    def compute(self):
        self.start_spinner_signal.emit()

        image_ = self.get_first_param('image', pluggable=INPUT_PLUG)
        img_pil = image_.value

        image = np.asarray(img_pil)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        faces = self.cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
            # flags = cv2.CV_HAAR_SCALE_IMAGE
        )

        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        out_image = self.get_first_param('image', pluggable=OUTPUT_PLUG)
        out_image.value = Image.fromarray(image)

        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        self.stop_spinner_signal.emit()
        signal.emit_event()
        super().compute()
