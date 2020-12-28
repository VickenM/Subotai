import sys
import pywerlines.pywerview

from PySide2.QtWidgets import QApplication, QLabel, QMainWindow, QDockWidget, QWidget, QVBoxLayout, QGraphicsScene
from PySide2 import QtCore
from PySide2.QtCore import Slot, Signal

from pywerlines import pyweritems, pywerscene

from PySide2.QtMultimedia import QAudioFormat, QAudioOutput, QAudio

from PySide2.QtCore import QByteArray, QDataStream, QIODevice, QBuffer, QObject
from PySide2 import QtGui, QtWidgets
import time


@Slot(QAudio)
def handleStateChanged(state):
    print(state)
    # if state == QAudio.IdleState:
    #     audio.stop()
    # if state == QAudio.StoppedState:
    #     sys.exit()


class Worker(QObject):
    finished = QtCore.Signal()

    def __init__(self, audio, buffer):
        super().__init__()
        self.audio = audio
        self.buffer = buffer

    def run(self):
        while True:
            time.sleep(0.005)
            if self.audio.state() in [QAudio.IdleState, QAudio.StoppedState]:
                if not buffer.atEnd():
                    self.audio.start(self.buffer)

                    # self.finished.emit()


class Feeder(QObject):
    def __init__(self, audio, buffer, freq=220):
        super().__init__()
        self.audio = audio
        self.buffer = buffer
        self.freq = freq

    def setFreq(self, freq):
        self.freq = freq

    def run(self):
        import math

        while True:
            time.sleep(0.051)
            if self.buffer.size() - self.buffer.pos() > 10000:
                continue
            freq = self.freq
            samples = [int(volume * math.sin(2.0 * math.pi * freq * x / sampleRate)) for x in
                       range(0, int(sampleRate * duration))]

            for s in samples:
                try:
                    data_stream.writeInt16(s)
                except:
                    print(s)


class Main(QtWidgets.QWidget):
    def __init__(self, data_stream):
        super().__init__()
        self.data_stream = data_stream

        self.slider = QtWidgets.QSlider()
        self.slider.setMinimum(0)
        self.slider.setMaximum(33)
        # self.slider.setTickInterval(10)
        self.slider.valueChanged.connect(self.sliderChanged)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.slider)
        self.setLayout(layout)

    @Slot(int)
    def sliderChanged(self, value):
        freq = (value * 10) + 220
        print(freq)
        feeder.setFreq(freq)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    fmt = QAudioFormat()
    fmt.setSampleRate(441000)
    fmt.setChannelCount(1)
    fmt.setSampleSize(16)
    fmt.setCodec('audio/pcm')
    fmt.setByteOrder(QAudioFormat.LittleEndian)
    fmt.setSampleType(QAudioFormat.SignedInt)

    audio = QAudioOutput(fmt)
    bytearray_ = QByteArray()
    buffer = QBuffer(bytearray_)
    buffer.open(QBuffer.ReadWrite)
    buffer.seek(0)
    data_stream = QDataStream(bytearray_, QBuffer.ReadWrite)
    data_stream.setVersion(QDataStream.Qt_5_15)
    data_stream.setByteOrder(QDataStream.LittleEndian)

    duration = 0.1
    freq = 261.63 * 2
    sampleRate = 441000
    volume = 10000

    buffer.seek(0)
    audio.stateChanged.connect(handleStateChanged)
    # audio.start(buffer)

    worker = Worker(audio, buffer)
    thread = QtCore.QThread()
    worker.moveToThread(thread)
    thread.started.connect(worker.run)
    thread.start()

    feeder = Feeder(audio, buffer)
    fthread = QtCore.QThread()
    feeder.moveToThread(fthread)
    fthread.started.connect(feeder.run)
    fthread.start()

    main = Main(data_stream)
    main.show()

    sys.exit(app.exec_())
