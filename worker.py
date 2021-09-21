from PySide2 import QtCore


class Worker(QtCore.QThread):
    def __init__(self, parent):
        super().__init__(parent=parent)
