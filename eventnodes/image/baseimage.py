from PySide2 import QtCore
from PySide2.QtCore import Slot, Signal

from eventnodes.params import INPUT_PLUG, OUTPUT_PLUG, PARAM
from eventnodes import base
from abc import abstractmethod


class BaseImageNode(base.ComputeNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.color = (35, 140, 105, 200)
