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
        if self.item not in self.scene.items():
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
        if self.item in self.scene.items():
            self.scene.removeItem(self.item)

    def undo(self):
        self.scene.addItem(self.item)


class Connect(QtWidgets.QUndoCommand):
    def __init__(self, source_plug, target_plug, edge, scene):
        super().__init__()
        self.source_plug = source_plug
        self.target_plug = target_plug
        self.edge = edge
        self.scene = scene

    def redo(self):
        if self.edge not in self.scene.items():
            self.scene.addItem(self.edge)

        plug1 = self.source_plug
        plug2 = self.target_plug

        source = plug1.parentItem().node_obj
        target = plug2.parentItem().node_obj

        from eventnodes import signal
        source_signal = isinstance(plug1.plug_obj, signal.Signal)
        target_signal = isinstance(plug2.plug_obj, signal.Signal)

        if all([source_signal, target_signal]):
            signal_obj = plug1.plug_obj
            target.connect_from(signal_obj.computed, trigger=plug2.type_)
        else:
            input = plug1.plug_obj
            output = plug2.plug_obj

            output.connect_(input)

        plug1.add_edge(self.edge)
        plug2.add_edge(self.edge)

    def undo(self):
        if self.edge in self.scene.items():
            self.scene.removeItem(self.edge)

        plug1 = self.source_plug
        plug2 = self.target_plug

        source = plug1.parentItem().node_obj
        target = plug2.parentItem().node_obj

        from eventnodes import signal
        source_signal = isinstance(plug1.plug_obj, signal.Signal)
        target_signal = isinstance(plug2.plug_obj, signal.Signal)

        if all([source_signal, target_signal]):
            signal_obj = plug1.plug_obj
            target.disconnect_from(signal_obj.computed, trigger=plug2.type_)
        else:
            input = plug1.plug_obj
            output = plug2.plug_obj

            output.disconnect_()

        plug1.remove_edge(self.edge)
        plug2.remove_edge(self.edge)


class Disconnect(QtWidgets.QUndoCommand):
    def __init__(self, source_plug, target_plug, edge, scene):
        super().__init__()
        self.source_plug = source_plug
        self.target_plug = target_plug
        self.edge = edge
        self.scene = scene

    def redo(self):
        if self.edge in self.scene.items():
            self.scene.removeItem(self.edge)

        plug1 = self.source_plug
        plug2 = self.target_plug

        source = plug1.parentItem().node_obj
        target = plug2.parentItem().node_obj

        from eventnodes import signal
        source_signal = isinstance(plug1.plug_obj, signal.Signal)
        target_signal = isinstance(plug2.plug_obj, signal.Signal)

        if all([source_signal, target_signal]):
            signal_obj = plug1.plug_obj
            target.disconnect_from(signal_obj.computed, trigger=plug2.type_)
        else:
            input = plug1.plug_obj
            output = plug2.plug_obj

            output.disconnect_()

        plug1.remove_edge(self.edge)
        plug2.remove_edge(self.edge)

    def undo(self):
        if self.edge not in self.scene.items():
            self.scene.addItem(self.edge)

        plug1 = self.source_plug
        plug2 = self.target_plug

        source = plug1.parentItem().node_obj
        target = plug2.parentItem().node_obj

        from eventnodes import signal
        source_signal = isinstance(plug1.plug_obj, signal.Signal)
        target_signal = isinstance(plug2.plug_obj, signal.Signal)

        if all([source_signal, target_signal]):
            signal_obj = plug1.plug_obj
            target.connect_from(signal_obj.computed, trigger=plug2.type_)
        else:
            input = plug1.plug_obj
            output = plug2.plug_obj

            output.connect_(input)

        self.edge.connect_plugs(plug1, plug2)

        plug1.add_edge(self.edge)
        plug2.add_edge(self.edge)


class ParamChanged(QtWidgets.QUndoCommand):
    def __init__(self, param):
        super().__init__()
        self.param = param
        self.value = self.param.value
        self.old_value = self.param._old_value

    def redo(self):
        self.param.value = self.value

    def undo(self):
        self.param.value = self.old_value
