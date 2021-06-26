from PySide2 import QtCore
from PySide2.QtCore import Slot

from .base import ComputeNode
from .params import StringParam, IntParam, FloatParam, PARAM, SUBTYPE_FILEPATH
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG

from .image.imageparam import ImageParam

import sys

sys.path.append('D:\\projects\\python\\node2\\opencv')

from PIL import Image

import os
import cv2
import numpy as np


class FaceDetect(ComputeNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'FaceDetect'

        p = os.path.dirname(os.path.abspath(__file__))

        scaleFactor = 1.1,
        minNeighbors = 5,

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(StringParam(name='classifier', value='', pluggable=PARAM, subtype=SUBTYPE_FILEPATH))
        self.params.append(FloatParam(name='scale factor', value=1.1, pluggable=PARAM))
        self.params.append(IntParam(name='min neighbors', value=5, pluggable=PARAM))
        self.params.append(IntParam(name='width', value=30, pluggable=PARAM))
        self.params.append(IntParam(name='height', value=30, pluggable=PARAM))
        self.params.append(ImageParam(name='image', value=None, pluggable=INPUT_PLUG))
        self.params.append(ImageParam(name='image', value=None, pluggable=OUTPUT_PLUG))

        self.cascade = cv2.CascadeClassifier()
        self.classifier_file = None

        self.description = \
            """The **FaceDetect node** can detect faces from the source *image* input.

Parameters:

- *classifier*:


Inputs:

- *image*: source image


Outputs:

- *image*: output image
"""

    def update(self):
        super().update()
        classifier = self.get_first_param('classifier', pluggable=PARAM)
        classifier_file = classifier.value

        if os.path.isfile(classifier_file) and classifier_file != self.classifier_file:
            self.cascade = cv2.CascadeClassifier()
            self.cascade.load(classifier_file)
            self.classifier_file = classifier_file

    def compute(self):
        self.start_spinner_signal.emit()

        img_pil = self.get_first_param('image', pluggable=INPUT_PLUG).value
        width = self.get_first_param('width').value
        height = self.get_first_param('height').value
        num_neighbors = self.get_first_param('min neighbors').value
        scale_facor = self.get_first_param('scale factor').value

        # img_pil = image_.value

        image = np.asarray(img_pil)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        if not self.cascade.empty():
            faces = self.cascade.detectMultiScale(
                gray,
                scaleFactor=scale_facor,
                minNeighbors=num_neighbors,
                minSize=(width, height)
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
