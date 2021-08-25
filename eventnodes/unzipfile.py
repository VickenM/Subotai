from PySide2 import QtCore
from PySide2.QtCore import Slot

from .base import ComputeNode
from .params import StringParam, IntParam, PARAM, SUBTYPE_FILEPATH, SUBTYPE_DIRPATH
from .signal import Signal, INPUT_PLUG, OUTPUT_PLUG


class UnzipFile(ComputeNode):
    type = 'UnzipFile'
    categories = ['FileSystem']
    description = \
        """The **UnzipFile node** adds the files contained in the *source* directory to the *zipfile* archive file


Parameters:

- *source*: the source directory to add to the archive
- *zipfile*: the zip archive file to create
"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals.append(Signal(node=self, name='event', pluggable=INPUT_PLUG))
        self.signals.append(Signal(node=self, name='event', pluggable=OUTPUT_PLUG))
        self.params.append(
            StringParam(name='zipfile', value='', pluggable=PARAM | INPUT_PLUG, subtype=SUBTYPE_FILEPATH))
        self.params.append(StringParam(name='target', value='', pluggable=PARAM | INPUT_PLUG, subtype=SUBTYPE_DIRPATH))
        self.params.append(StringParam(name='target', value='', pluggable=OUTPUT_PLUG, subtype=SUBTYPE_DIRPATH))

    @ComputeNode.Decorators.show_ui_computation
    def compute(self):
        self.start_spinner_signal.emit()
        zip_file = self.get_first_param('zipfile', pluggable=INPUT_PLUG)
        target = self.get_first_param('target', pluggable=INPUT_PLUG)

        from zipfile import ZipFile
        # import os

        
        with ZipFile(zip_file()) as z:
            z.extractall(path=target.value)

        # fullpaths = []
        # for root, directories, files in os.walk(target()):
        #     for filename in files:
        #         fullpath = os.path.join(root, filename)
        #         fullpaths.append(fullpath)
        #
        # with ZipFile(zip_file(), 'w') as z:
        #     for fullpath in fullpaths:
        #         z.write(fullpath)

        output = self.get_first_param('target', pluggable=OUTPUT_PLUG)
        output.value = target.value

        signal = self.get_first_signal('event', pluggable=OUTPUT_PLUG)
        self.stop_spinner_signal.emit()
        signal.emit_event()
        super().compute()
