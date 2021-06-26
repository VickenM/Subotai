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


class Camera(ComputeNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'Camera'

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(ImageParam(name='image', value=None, pluggable=OUTPUT_PLUG))

        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)

    def compute(self):
        self.start_spinner_signal.emit()
        ret, frame = self.cap.read()

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img)

        image_ = self.get_first_param('image')
        image_.value = img_pil

        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        self.stop_spinner_signal.emit()
        signal.emit_event()
        super().compute()
