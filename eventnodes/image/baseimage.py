from PySide6 import QtCore
from PySide6.QtCore import Slot, Signal

from eventnodes.params import INPUT_PLUG, OUTPUT_PLUG, PARAM
from eventnodes import base
from abc import abstractmethod


class BaseImageNode(base.ComputeNode):
    categories = ['Image']
    description = """BaseImageNode description"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
