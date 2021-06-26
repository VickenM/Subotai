from PySide2 import QtCore
from PySide2.QtCore import Slot

from .base import ComputeNode
from .params import StringParam, IntParam, PARAM
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG

from .image.imageparam import ImageParam

import sys

from PIL import Image
from PySide2.QtGui import QPainter, QPixmap

from PySide2 import QtWidgets
from PIL import ImageQt


class View(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(QtCore.Qt.WA_QuitOnClose, False)  # close this widget when main app window is closed
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)

        self.pixmap = None
        self.label = QtWidgets.QLabel(self)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.label)
        layout.setSizeConstraint(layout.SetNoConstraint)
        self.setLayout(layout)

        self.resize(1920 / 4, 1080 / 4)

    def setPixmap(self, image):
        width = self.label.width()
        height = self.label.height()

        pixmap = QPixmap.fromImage(image).scaled(width, height, QtCore.Qt.KeepAspectRatio)
        self.label.setPixmap(pixmap)


class Viewer(ComputeNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'Viewer'

        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.params.append(ImageParam(name='image', value=None, pluggable=INPUT_PLUG))

        self.widget = View()
        self.widget.show()

        self.show_viewer_button = QtWidgets.QPushButton('Toggle Viewer')

        self.controls.append((self.show_viewer_button, self.toggle_viewer, self.show_viewer_button.clicked))
        self.description = \
            """The **Viewer node** provides a Viewer UI window, for viewing an *image*


Parameters:

- *image*: a source image to view
            """


    def toggle_viewer(self):
        self.widget.setVisible(not self.widget.isVisible())

    def compute(self):
        self.start_spinner_signal.emit()
        image = self.get_first_param('image')

        qim = ImageQt.ImageQt(image.value)

        self.widget.setPixmap(qim)
        self.stop_spinner_signal.emit()
        super().compute()
