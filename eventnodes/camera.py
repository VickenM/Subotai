from PySide2 import QtCore
from PySide2.QtCore import Slot

from .base import ComputeNode
from .params import StringParam, IntParam, PARAM, EnumParam
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG

from .image.imageparam import ImageParam

import sys

sys.path.append('D:\\projects\\python\\node2\\opencv')

from PIL import Image

import cv2

from enum import Enum, auto


class Camera(ComputeNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'Camera'

        self.current_index = 1

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(ImageParam(name='image', value=None, pluggable=OUTPUT_PLUG))
        self.params.append(IntParam(name='camera index', value=self.current_index, pluggable=PARAM))
        self.params.append(IntParam(name='width', value=960, pluggable=PARAM))
        self.params.append(IntParam(name='height', value=540, pluggable=PARAM))

        self.cap = cv2.VideoCapture(self.current_index, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)

        self.description = \
            """The **Camera node** can read images from your camera and output the *image*.

Parameters:

- *camera index*: the index of the camera device available on the system to read from
- *image*: image read from the camera

"""

    def update(self):
        index = self.get_first_param('camera index').value
        width = self.get_first_param('width').value
        height = self.get_first_param('width').value

        if index != self.current_index:
            if self.cap and self.cap.isOpened():
                self.cap.release()

            self.cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            self.current_index = index

        if self.cap and self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

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

    def terminate(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
