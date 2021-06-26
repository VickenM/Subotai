import os
import sys
import json
import argparse

import pywerlines.pywerview

from PySide2.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QDockWidget,
    QWidget,
    QHBoxLayout,
    QGraphicsScene,
    QSplitter,
    QFileDialog
)
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2.QtGui import QIcon
from PySide2.QtCore import Slot

from toolbox import ToolBox, ToolItem
from parameters import Parameters
from pywerlines import pyweritems, pywerscene

import nodes

import eventnodes.base
import eventnodes.parameter
import eventnodes.inttostr
import eventnodes.math
import eventnodes.timer
import eventnodes.zipfile
import eventnodes.copyfile
import eventnodes.listdir
import eventnodes.dirchange
import eventnodes.fileschanged
import eventnodes.email
import eventnodes.consolewriter
import eventnodes.counter
import eventnodes.foreach
import eventnodes.for_
import eventnodes.splitstring
import eventnodes.joinstrings
import eventnodes.slicelist
import eventnodes.condition
import eventnodes.collector
import eventnodes.image.open
import eventnodes.image.save
import eventnodes.image.crop
import eventnodes.image.resize
import eventnodes.image.thumbnail
import eventnodes.camera
import eventnodes.facedetect
import eventnodes.viewer
import eventnodes.systemnotification
import appnode


@Slot(list)
def selected_nodes(data):
    pass


@Slot(list)
def added_nodes(data):
    pass


@Slot(list)
def deleted_nodes(data):
    pass


@Slot()
def start_thread():
    eventnodes.base.thread = eventnodes.base.Worker()


@Slot()
def stop_thread():
    eventnodes.base.thread.exit()
    eventnodes.base.thread.wait(QtCore.QDeadlineTimer(10000))  # wait 10sec if the thread is still running


@Slot(pyweritems.PywerPlug, pyweritems.PywerPlug)
def connected_plugs(plug1, plug2):
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

        output.connect(input)


@Slot(pyweritems.PywerPlug, pyweritems.PywerPlug)
def disconnected_plugs(plug1, plug2):
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

        output.disconnect()


class EventFlow(pywerscene.PywerScene):
    def list_node_types(self):
        return nodes.list_nodes()

    def new_node(self, type_):
        if type_ == 'StringParameter':
            node = appnode.ParamNode.from_event_node(eventnodes.parameter.StringParameter())
        elif type_ == 'IntegerParameter':
            node = appnode.ParamNode.from_event_node(eventnodes.parameter.IntegerParameter())
        elif type_ == 'FloatParameter':
            node = appnode.ParamNode.from_event_node(eventnodes.parameter.FloatParameter())
        elif type_ == 'BooleanParameter':
            node = appnode.ParamNode.from_event_node(eventnodes.parameter.BooleanParameter())
        elif type_ == 'IntToStr':
            node = appnode.ParamNode.from_event_node(eventnodes.inttostr.IntToStr())
        elif type_ == 'Math':
            node = appnode.ParamNode.from_event_node(eventnodes.math.Math())
        elif type_ == 'Timer':
            node = appnode.EventNode.from_event_node(eventnodes.timer.TimerNode())
        elif type_ == 'DirChanged':
            node = appnode.EventNode.from_event_node(eventnodes.dirchange.DirChanged())
        elif type_ == 'FilesChanged':
            node = appnode.EventNode.from_event_node(eventnodes.fileschanged.FilesChanged())
        elif type_ == 'ConsoleWriter':
            node = appnode.EventNode.from_event_node(eventnodes.consolewriter.ConsoleWriter())
        elif type_ == 'ZipFile':
            node = appnode.EventNode.from_event_node(eventnodes.zipfile.ZipFile())
        elif type_ == 'CopyFile':
            node = appnode.EventNode.from_event_node(eventnodes.copyfile.CopyFile())
        elif type_ == 'ListDir':
            node = appnode.EventNode.from_event_node(eventnodes.listdir.ListDir())
        elif type_ == 'Email':
            node = appnode.EventNode.from_event_node(eventnodes.email.Email())
        elif type_ == 'Collector':
            node = appnode.EventNode.from_event_node(eventnodes.collector.Collector())
        elif type_ == 'Counter':
            node = appnode.EventNode.from_event_node(eventnodes.counter.Counter())
        elif type_ == 'ForEach':
            node = appnode.EventNode.from_event_node(eventnodes.foreach.ForEach())
        elif type_ == 'For':
            node = appnode.EventNode.from_event_node(eventnodes.for_.For())
        elif type_ == 'SplitString':
            node = appnode.EventNode.from_event_node(eventnodes.splitstring.SplitString())
        elif type_ == 'JoinStrings':
            node = appnode.ParamNode.from_event_node(eventnodes.joinstrings.JoinStrings())
        elif type_ == 'SliceList':
            node = appnode.ParamNode.from_event_node(eventnodes.slicelist.SliceList())
        elif type_ == 'Condition':
            node = appnode.EventNode.from_event_node(eventnodes.condition.Condition())
        elif type_ == 'OpenImage':
            node = appnode.EventNode.from_event_node(eventnodes.image.open.Open())
        elif type_ == 'SaveImage':
            node = appnode.EventNode.from_event_node(eventnodes.image.save.Save())
        elif type_ == 'CropImage':
            node = appnode.EventNode.from_event_node(eventnodes.image.crop.Crop())
        elif type_ == 'ResizeImage':
            node = appnode.EventNode.from_event_node(eventnodes.image.resize.Resize())
        elif type_ == 'ThumbnailImage':
            node = appnode.EventNode.from_event_node(eventnodes.image.thumbnail.Thumbnail())
        elif type_ == 'Camera':
            node = appnode.EventNode.from_event_node(eventnodes.camera.Camera())
        elif type_ == 'FaceDetect':
            node = appnode.EventNode.from_event_node(eventnodes.facedetect.FaceDetect())
        elif type_ == 'Viewer':
            node = appnode.EventNode.from_event_node(eventnodes.viewer.Viewer())
        elif type_ == 'SystemNotification':
            node = appnode.EventNode.from_event_node(eventnodes.systemnotification.SystemNotification())

        else:
            return None
        return node

    def can_connect(self, source_plug, target_plug):
        if not super().can_connect(source_plug, target_plug):
            return False

        import eventnodes.signal
        source_signal = isinstance(source_plug.plug_obj, eventnodes.signal.Signal)
        target_signal = isinstance(target_plug.plug_obj, eventnodes.signal.Signal)
        if source_signal and target_signal:
            return True

        # if any is a signal but all are not, then only one of them is
        if any([source_signal, target_signal]) and not all([source_signal, target_signal]):
            return False

        return source_plug.plug_obj.type == target_plug.plug_obj.type

    def create_node_of_type(self, type_):
        node = self.new_node(type_)
        self.add_node(node)
        return node

    def create_edge(self, source_plug, target_plug):
        super(EventFlow, self).create_edge(source_plug, target_plug)

    def get_node_by_id(self, obj_id):
        nodes = self.get_all_nodes()
        for node in nodes:
            if node.node_obj.obj_id == obj_id:
                return node

    def get_all_edges(self):
        return [item for item in self.items() if isinstance(item, pyweritems.PywerEdge)]

    def get_all_nodes(self):
        return [item for item in self.items() if isinstance(item, pyweritems.PywerNode)]

    def get_all_groups(self):
        return [item for item in self.items() if isinstance(item, pyweritems.PywerGroup)]

    def eval(self):
        selected_nodes = self.get_selected_nodes()
        if not selected_nodes:
            print('No nodes selected')
            return

        selected_node = selected_nodes[0]

        mnode = selected_node.node_obj
        # mnode.compute()
        if mnode.computable:
            mnode.calculate.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        view = pywerlines.pywerview.PywerView()
        scene = EventFlow()
        scene.setSceneRect(0, 0, 5000, 5000)
        scene.setItemIndexMethod(scene.NoIndex)
        view.setScene(scene)

        self.filename = None
        self.unsaved = True

        p = os.path.dirname(os.path.abspath(__file__))

        toolbox = ToolBox()
        toolbox.addItem(ToolItem(icon=QIcon(p + '/icons/flow.png'), label="DirChanged", sections=['Events']))
        toolbox.addItem(ToolItem(icon=QIcon(p + '/icons/flow.png'), label="FilesChanged", sections=['Events']))
        toolbox.addItem(ToolItem(icon=QIcon(p + '/icons/flow.png'), label="Timer", sections=['Events']))
        toolbox.addItem(ToolItem(icon=QIcon(p + '/icons/flow.png'), label="CopyFile", sections=['FileSystem']))
        toolbox.addItem(ToolItem(icon=QIcon(p + '/icons/flow.png'), label="ListDir", sections=['FileSystem']))
        toolbox.addItem(ToolItem(icon=QIcon(p + '/icons/flow.png'), label="ZipFile", sections=['FileSystem']))
        toolbox.addItem(ToolItem(icon=QIcon(p + '/icons/flow.png'), label="Email", sections=['FileSystem']))
        toolbox.addItem(ToolItem(icon=QIcon(p + '/icons/flow.png'), label="StringParameter", sections=['Data']))
        toolbox.addItem(ToolItem(icon=QIcon(p + '/icons/flow.png'), label="IntegerParameter", sections=['Data']))
        toolbox.addItem(ToolItem(icon=QIcon(p + '/icons/flow.png'), label="FloatParameter", sections=['Data']))
        toolbox.addItem(ToolItem(icon=QIcon(p + '/icons/flow.png'), label="BooleanParameter", sections=['Data']))
        toolbox.addItem(ToolItem(icon=QIcon(p + '/icons/flow.png'), label="IntToStr", sections=['Data']))
        toolbox.addItem(ToolItem(icon=QIcon(p + '/icons/flow.png'), label="Math", sections=['Math']))
        toolbox.addItem(ToolItem(icon=QIcon(p + '/icons/flow.png'), label="SliceList", sections=['Data']))
        toolbox.addItem(ToolItem(icon=QIcon(p + '/icons/flow.png'), label="SplitString", sections=['String']))
        toolbox.addItem(ToolItem(icon=QIcon(p + '/icons/flow.png'), label="JoinStrings", sections=['String']))
        toolbox.addItem(ToolItem(icon=QIcon(p + '/icons/flow.png'), label="For", sections=['Flow Control']))
        toolbox.addItem(ToolItem(icon=QIcon(p + '/icons/flow.png'), label="ForEach", sections=['Flow Control']))
        toolbox.addItem(ToolItem(icon=QIcon(p + '/icons/flow.png'), label="Counter", sections=['Flow Control']))
        toolbox.addItem(ToolItem(icon=QIcon(p + '/icons/flow.png'), label="Condition", sections=['Flow Control']))
        toolbox.addItem(ToolItem(icon=QIcon(p + '/icons/flow.png'), label="Collector", sections=['Flow Control']))
        toolbox.addItem(ToolItem(icon=QIcon(p + '/icons/flow.png'), label="ConsoleWriter", sections=['I/O']))
        toolbox.addItem(ToolItem(icon=QIcon(p + '/icons/flow.png'), label="OpenImage", sections=['Image']))
        toolbox.addItem(ToolItem(icon=QIcon(p + '/icons/flow.png'), label="SaveImage", sections=['Image']))
        toolbox.addItem(ToolItem(icon=QIcon(p + '/icons/flow.png'), label="CropImage", sections=['Image']))
        toolbox.addItem(ToolItem(icon=QIcon(p + '/icons/flow.png'), label="ResizeImage", sections=['Image']))
        toolbox.addItem(ToolItem(icon=QIcon(p + '/icons/flow.png'), label="ThumbnailImage", sections=['Image']))
        toolbox.addItem(ToolItem(icon=QIcon(p + '/icons/flow.png'), label="Camera", sections=['I/O']))
        toolbox.addItem(ToolItem(icon=QIcon(p + '/icons/flow.png'), label="FaceDetect", sections=['I/O']))
        toolbox.addItem(ToolItem(icon=QIcon(p + '/icons/flow.png'), label="Viewer", sections=['I/O']))
        toolbox.addItem(ToolItem(icon=QIcon(p + '/icons/flow.png'), label="SystemNotification", sections=['I/O']))
        toolbox.itemClicked.connect(self.toolbox_item_selected)

        scene.nodes_selected.connect(selected_nodes)
        scene.nodes_deleted.connect(deleted_nodes)
        scene.nodes_added.connect(added_nodes)
        scene.plugs_connected.connect(connected_plugs)
        scene.plugs_disconnected.connect(disconnected_plugs)
        scene.nodes_selected.connect(self.selected_nodes)

        self.scene = scene
        self.view = view

        self.parameters = Parameters()

        splitter = QSplitter()
        splitter.addWidget(toolbox)
        splitter.addWidget(view)
        splitter.addWidget(self.parameters)
        splitter.setSizes([100, 400, 100])

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(splitter)

        central_widget = QWidget(parent=self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        toolbar = self.addToolBar('Run')
        action = toolbar.addAction('&Run')
        action.setIcon(QIcon(p + '/icons/run.jpg'))
        action.setShortcut(QtGui.QKeySequence('Space'))
        action.triggered.connect(lambda x: self.scene.eval())

        file_menu = self.menuBar().addMenu('&File')
        action = file_menu.addAction('&New Scene')
        action.setShortcut(QtGui.QKeySequence('Ctrl+n'))
        action.triggered.connect(self.new_scene)

        action = file_menu.addAction('&Open Scene')
        action.setShortcut(QtGui.QKeySequence('Ctrl+o'))
        action.triggered.connect(self.open_scene)

        file_menu.addSeparator()
        action = file_menu.addAction('&Save Scene')
        action.setShortcut(QtGui.QKeySequence('Ctrl+s'))
        action.triggered.connect(self.save_scene)

        action = file_menu.addAction('&Save Scene As')
        action.setShortcut(QtGui.QKeySequence('Ctrl+Shift+s'))
        action.triggered.connect(self.save_scene_as)

        file_menu.addSeparator()
        file_menu.addAction('&Exit').triggered.connect(self.exit_app)

        edit_menu = self.menuBar().addMenu('&Edit')
        action = edit_menu.addAction('&Group Selected')
        action.setShortcut(QtGui.QKeySequence('Ctrl+G'))
        action.triggered.connect(self.group_selected)
        action = edit_menu.addAction('&New Group')
        action.setShortcut(QtGui.QKeySequence('Ctrl+Alt+G'))
        action.triggered.connect(self.new_group)

        edit_menu.addSeparator()
        action = edit_menu.addAction('&Delete Selected')
        action.setShortcut(QtGui.QKeySequence('Delete'))
        action.triggered.connect(self.delete_selected)

        self.menuBar().addSeparator()
        run_menu = self.menuBar().addMenu('Process')

        action = run_menu.addAction('&Create new process')
        action.setShortcut(QtGui.QKeySequence('Ctrl+r'))
        action.triggered.connect(lambda x: self.spawn(background=False))

        action = run_menu.addAction('&Create new background process')
        action.setShortcut(QtGui.QKeySequence('Ctrl+Shift+r'))
        action.triggered.connect(lambda x: self.spawn(background=True))

    def spawn(self, background=True):
        import subprocess

        py_path = sys.executable
        app_path = os.path.abspath(__file__)
        json_string = self.dump_json()

        args = [py_path, app_path, '--load-json', json_string]
        if background:
            args = [py_path, app_path, '--background', '--load-json', json_string]

        p = subprocess.Popen(args,
                             creationflags=subprocess.CREATE_NEW_CONSOLE,
                             close_fds=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             shell=False)

    def load_data(self, data):
        for node in data['nodes']:
            type_ = node['node_obj'].split('.')[-1]
            n = self.scene.create_node_of_type(type_)
            n.node_obj.obj_id = node['id']
            n.node_obj.set_active(node.get('active', True))
            n.setPos(*node['position'])
            n.setSize(*node.get('size', (100, 100)))

            for pluggable, params in node.get('params', {}).items():
                pluggable = int(pluggable)
                for param, value in params.items():
                    if type(value) == list:
                        p = n.node_obj.get_first_param(param, pluggable=pluggable)
                        from eventnodes.params import StringParam
                        s = []
                        for item in value:
                            s.append(StringParam(value=item))

                        # print(p.value)
                        p.value.clear()
                        p.value.extend(s)
                        continue

                    p = n.node_obj.get_first_param(param, pluggable=pluggable)
                    from enum import Enum
                    if issubclass(p.value.__class__, Enum):
                        p._value = p.enum(value)
                    else:
                        p._value = value
            n.node_obj.update()

        for edge in data['edges']:
            source, target = edge
            s_obj_id, s_plug = source.split('.')
            t_obj_id, t_plug = target.split('.')

            s_node = self.scene.get_node_by_id(s_obj_id)
            for o in s_node.outputs:
                if o.type_ == s_plug:
                    source_plug = o
                    break

            t_node = self.scene.get_node_by_id(t_obj_id)
            for o in t_node.inputs:
                if o.type_ == t_plug:
                    target_plug = o
                    break

            self.scene.create_edge(source_plug, target_plug)

        for group in data['groups']:
            g = self.scene.create_group()
            g.setPos(*group['position'])
            g.setSize(*group['size'])

        print(data)

    def save_data(self):
        data = {'nodes': [], 'edges': [], 'groups': []}
        for node in self.scene.get_all_nodes():
            data['nodes'].append(node.to_dict())

        # TODO: should do edges and groups like nodes with to_dict()

        for edge in self.scene.get_all_edges():
            edge_info = (str(edge.source_plug.parentItem().node_obj.obj_id) + '.' + edge.source_plug.type_,
                         str(edge.target_plug.parentItem().node_obj.obj_id) + '.' + edge.target_plug.type_)
            data['edges'].append(edge_info)

        for group in self.scene.get_all_groups():
            data['groups'].append(
                {'position': (group.pos().x(), group.pos().y()),
                 'size': (group.width, group.height)
                 }
            )

        return data

    def load_json(self, json_string):
        data = json.loads(json_string)
        self.load_data(data)

    def dump_json(self):
        return json.dumps(self.save_data())

    def load_file(self, file_name):
        with open(file_name, 'r') as fp:
            data = json.load(fp)
        self.load_data(data)

    def save_file(self, file_name):
        data = self.save_data()
        with open(file_name, 'w') as fp:
            json.dump(data, fp, indent=4)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Period:
            self.scene.toggle_labels()

            # elif event.key() == QtCore.Qt.Key_Space:
            #     self.scene.eval()

    def stop_timers(self):
        scene_nodes = self.scene.list_nodes()
        for node in scene_nodes:
            node.stop_spinner()
            if node.node_obj.is_computable():
                node.node_obj.unset_ui_node()

        timers = [item for item in scene_nodes if isinstance(item.node_obj, eventnodes.timer.TimerNode)]
        for timer in timers:
            timer.node_obj.deactivate()

    @Slot()
    def new_group(self):
        group = self.scene.create_group()
        position = QtCore.QPointF(self.view.mapToScene(self.view.mouse_position))
        group.setPos(position)

    @Slot()
    def group_selected(self):
        self.scene.group_selected_nodes()

    @Slot()
    def delete_selected(self):
        self.scene.remove_selected_nodes()
        self.scene.remove_selected_groups()

    @Slot(str)
    def toolbox_item_selected(self, item):
        node = self.scene.create_node_of_type(item)
        position = QtCore.QPointF(self.view.mapToScene(100, 100))
        node.setPos(position)

    @Slot(list)
    def selected_nodes(self, nodes):
        if nodes:
            self.parameters.set_node_obj(nodes[0].node_obj)
        else:
            self.parameters.set_node_obj(None)

    @Slot()
    def new_scene(self):
        stop_thread()
        self.stop_timers()
        start_thread()
        self.scene.clear()

    @Slot()
    def open_scene(self):
        filename, filter_ = QFileDialog.getOpenFileName(self, 'Open Scene', os.getcwd(), 'Scene Files (*.json)')
        if filename:
            stop_thread()
            self.stop_timers()
            self.scene.clear()
            start_thread()
            self.load_file(filename)

    @Slot()
    def save_scene_as(self):
        filename, filter_ = QFileDialog.getSaveFileName(self, 'Save Scene', os.getcwd(), 'Scene Files (*.json)')
        if filename:
            self.save_file(filename)

    @Slot()
    def save_scene(self):
        if self.filename:
            self.save_file(self.filename)
        else:
            self.save_scene_as()

    @Slot()
    def exit_app(self):
        qapp = QApplication.instance()
        qapp.exit()


def main(background=False, scene_file=None, json_string=None):
    import signal as signal_

    app = QApplication(sys.argv)
    QtCore.QTimer(app).singleShot(0, start_thread)
    app.startingUp()
    main_window = MainWindow()

    if scene_file:
        main_window.load_file(scene_file)
    else:
        if json_string:
            main_window.load_json(json_string)

    if background:
        signal_.signal(signal_.SIGINT, signal_.SIG_DFL)  # accept ctrl-c signal when in background mode to quit
    else:
        main_window.show()

    app.aboutToQuit.connect(stop_thread)
    return app, main_window


if __name__ == "__main__":
    background = False
    scene_file = None
    json_string = None

    parser = argparse.ArgumentParser()
    parser.add_argument("--background", action='store_true', help="run in a background process (no GUI)")
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--load-file", type=str, metavar='<FILENAME>',
                       help="loads the given scene .json file in")
    group.add_argument("--load-json", type=str, metavar='<JSON STRING>',
                       help="loads the given json string in")
    args = parser.parse_args()

    if args.background:
        background = True

    if args.load_file:
        scene_file = os.path.abspath(args.load_file)

    if args.load_json:
        json_string = args.load_json

    app, main_window = main(background=background, scene_file=scene_file, json_string=json_string)
    sys.exit(app.exec_())
