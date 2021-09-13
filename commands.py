from PySide2 import QtWidgets


class SelectionChanged(QtWidgets.QUndoCommand):
    def __init__(self, item):
        super().__init__()
        self.item = item
        self.old_selection = item.get_old_selection()
        self.new_selection = item.isSelected()

    def redo(self):
        self.item.setSelected(self.new_selection)
        self.item.set_old_selection(self.old_selection)

    def undo(self):
        self.item.setSelected(self.old_selection)


class ItemMoved(QtWidgets.QUndoCommand):
    def __init__(self, item):
        super().__init__()
        self.item = item
        self.old_posiiton = item.get_old_position()
        self.new_posiiton = item.pos()

    def redo(self):
        self.item.setPos(self.new_posiiton)

    def undo(self):
        self.item.setPos(self.old_posiiton)


class ItemAdded(QtWidgets.QUndoCommand):
    def __init__(self, item):
        super().__init__()
        self.item = item
        self.scene = self.item.scene()

    def redo(self):
        if self.item not in self.scene.get_all_nodes():
            self.scene.addItem(self.item)

    def undo(self):
        if self.item.scene():
            self.scene.removeItem(self.item)


class ItemRemoved(QtWidgets.QUndoCommand):
    def __init__(self, item, scene):
        super().__init__()
        self.item = item
        self.scene = scene

    def redo(self):
        if self.item in self.scene.get_all_nodes():
            self.scene.removeItem(self.item)

    def undo(self):
        self.scene.addItem(self.item)


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
