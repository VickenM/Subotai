from PySide2 import QtWidgets


class SplashScreen(QtWidgets.QSplashScreen):
    def __init__(self, pixmap, flags):
        super().__init__(pixmap, flags)

        # TODO I dont get it, implementing the mousePressEvent(...) function doesn't work. this lambda assignment is hack
        self.mousePressEvent = lambda x: self.close()
