from PySide2 import QtWidgets


class SelectionChanged(QtWidgets.QUndoCommand):
    def __init__(self, item):
        super().__init__()
        self.item = item
        self.selection = item.isSelected()

    def redo(self):
        self.item.setSelected(self.selection)

    def undo(self):
        self.item.setSelected(not self.selection)


class ItemMoved(QtWidgets.QUndoCommand):
    def __init__(self, item):
        super().__init__()
        self.item = item
        self.old_posiiton = item.old_position
        self.new_posiiton = item.pos()

    def redo(self):
        self.item.setPos(self.new_posiiton)

    def undo(self):
        self.item.setPos(self.old_posiiton)


class ItemAdded(QtWidgets.QUndoCommand):
    def __init__(self, item):
        super().__init__()
        self.item = item

    def redo(self):
        pass

    def undo(self):
        pass


class ItemRemoved(QtWidgets.QUndoCommand):
    def __init__(self, item):
        super().__init__()
        self.item = item

    def redo(self):
        pass

    def undo(self):
        pass


class Connect(QtWidgets.QUndoCommand):
    def __init__(self, source_plug, target_plug):
        super().__init__()
        self.source_plug = source_plug
        self.target_plug = target_plug

    def redo(self):
        pass

    def undo(self):
        pass


class Disonnect(QtWidgets.QUndoCommand):
    def __init__(self, source_plug, target_plug):
        super().__init__()
        self.source_plug = source_plug
        self.target_plug = target_plug

    def redo(self):
        pass

    def undo(self):
        pass


class ParamChanged(QtWidgets.QUndoCommand):
    def __init__(self, item, param, value):
        super().__init__()
        self.item = item
        self.param = param
        self.value = value

    def redo(self):
        pass

    def undo(self):
        pass
