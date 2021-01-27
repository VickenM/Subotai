from eventnodes.params import Param
from PIL import Image


class ImageParam(Param):
    def __init__(self, name='', value=None, pluggable=None):
        super().__init__(name=name, pluggable=pluggable)
        self.name = name
        self._type = Image
        self._value = value
