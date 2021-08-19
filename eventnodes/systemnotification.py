from .base import ComputeNode  # , ThreadedComputeNode
from .params import StringParam, IntParam, PARAM, SUBTYPE_FILEPATH
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG

from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore

from .image.imageparam import ImageParam
from PIL import ImageQt


class SystemNotification(ComputeNode):
    type = 'SystemNotification'
    categories = ['I/O']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.params.append(StringParam(name='title', value='', pluggable=PARAM))
        self.params.append(StringParam(name='message', value='', pluggable=PARAM | INPUT_PLUG))
        # self.params.append(StringParam(name='icon', value='', pluggable=PARAM | INPUT_PLUG, subtype=SUBTYPE_FILEPATH))
        self.params.append(ImageParam(name='icon', value=None, pluggable=INPUT_PLUG))

        # self.params.append(IntParam(name='length of time', value=5000, pluggable=PARAM))

    @ComputeNode.Decorators.show_ui_computation
    def compute(self):
        title = self.get_first_param('title').value
        message = self.get_first_param('message').value
        icon_img = self.get_first_param('icon').value

        # TODO: setting the millisecond timeout value doesnt seem to have an affect. So disabling param until I figure it out
        # milliseconds = self.get_first_param('length of time').value
        milliseconds = 5000
        self.start_spinner_signal.emit()

        qApp = QtWidgets.QApplication.instance()

        if icon_img:
            qim = ImageQt.ImageQt(icon_img)
            pixmap = QtGui.QPixmap.fromImage(qim).scaled(qim.width(), qim.height(), QtCore.Qt.KeepAspectRatio)
            icon = QtGui.QIcon(pixmap)
        else:
            icon = qApp.windowIcon()

        # TODO: hacky stuff just so that Qt doesnt give warning about non 32x32 icon sizes
        pixmap = icon.pixmap(QtCore.QSize(32, 32)).scaled(32, 32)

        qApp.trayIcon.showMessage(
            title,
            message,
            QtGui.QIcon(pixmap),
            milliseconds,
        )

        self.stop_spinner_signal.emit()
        super().compute()
