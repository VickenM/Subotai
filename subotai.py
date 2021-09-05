import argparse
import json
import os
import sys

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2.QtCore import Slot
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QSplitter,
    QFileDialog,
    QSystemTrayIcon,
    QMenu,
    QSplashScreen,
    QMessageBox,
    QAction
)
from pywerlines import (
    pyweritems,
    pywerscene,
    pywerview
)

from config import (
    path,
    node_categories
)

from ui.parameters import Parameters
from ui.toolbox import ToolBox, ToolItem

import register
import appnode
import eventnodes

@Slot(list)
def selected_nodes(data):
    pass


@Slot(list)
def added_nodes(data):
    pass


@Slot(list)
def deleted_nodes(data):
    pass


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

        output.connect_(input)


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

        output.disconnect_()


class SplashScreen(QSplashScreen):
    def __init__(self, pixmap, flags):
        super().__init__(pixmap, flags)

        # TODO I dont get it, implementing the mousePressEvent(...) function doesn't work. this lambda assignment is hack
        self.mousePressEvent = lambda x: self.close()


class EventFlow(pywerscene.PywerScene):
    def new_node(self, type_):
        if type_ not in register.node_registry:
            return None
        event_node = register.node_registry[type_]
        node = appnode.EventNode.from_event_node(event_node())
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

        if len(target_plug.edges):
            return False

        return source_plug.plug_obj.type == target_plug.plug_obj.type

    def create_node_of_type(self, type_):
        node = self.new_node(type_)
        if node:
            self.add_node(node)
        return node

    def create_edge(self, source_plug, target_plug):
        super(EventFlow, self).create_edge(source_plug, target_plug)

    # def create_edge(self, source_plug, target_plug):
    #     edge = super().create_edge(source_plug, target_plug)
    #     if edge:
    #         plug = edge.source_plug or edge.taget_plug
    #         import eventnodes.signal
    #         if plug and isinstance(plug.plug_obj, eventnodes.signal.Signal):
    #             edge.line_width = 1.5
    #         else:
    #             edge.line_width = 0.75
    #
    #     return edge


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

    def remove_selected_nodes(self):
        nodes = self.get_selected_nodes()
        for node in nodes:
            node.node_obj.terminate()
        return super().remove_selected_nodes()

    def clear(self):
        for node in self.get_all_nodes():
            node.node_obj.terminate()
        return super().clear()

    def eval(self):
        selected_nodes = self.get_selected_nodes()
        if not selected_nodes:
            print('No nodes selected')
            return

        selected_node = selected_nodes[0]

        mnode = selected_node.node_obj
        if mnode.computable:
            mnode.calculate.emit()


class EventView(pywerview.PywerView):
    node_dropped_signal = QtCore.Signal(str, int, int)
    context_menu_signal = QtCore.Signal(int, int)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

    def dragMoveEvent(self, event):
        # needed to include this function for the drops to work
        pass

    def dragLeaveEvent(self, event):
        event.ignore()

    def dragEnterEvent(self, event):
        if event.mimeData().data('application/x-node'):
            if event.source():
                event.setDropAction(QtCore.Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        node = event.mimeData().data('application/x-node')
        position = event.pos()

        if node:
            self.node_dropped_signal.emit(bytes(node).decode(), position.x(), position.y())
            event.accept()
        else:
            event.ignore()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.setDragMode(self.NoDrag)
            return
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.setDragMode(self.RubberBandDrag)
        if event.button() == QtCore.Qt.RightButton:
            self.context_menu_signal.emit(event.pos().x(), event.pos().y())

        return super().mouseReleaseEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        view = EventView()
        scene = EventFlow()
        scene.setSceneRect(0, 0, 100000, 100000)
        scene.setItemIndexMethod(scene.NoIndex)
        view.setScene(scene)

        self.filename = None
        self.unsaved = False
        self.saved_data = None

        self.toolbox = ToolBox()
        self._populate_toolbox()
        self.toolbox.itemDoubleClickedSignal.connect(self.new_node_selected)

        scene.nodes_selected.connect(selected_nodes)
        scene.nodes_deleted.connect(deleted_nodes)
        scene.nodes_added.connect(added_nodes)
        scene.plugs_connected.connect(connected_plugs)
        scene.plugs_disconnected.connect(disconnected_plugs)
        scene.nodes_selected.connect(self.selected_nodes)
        scene.items_moved.connect(self.items_moved)

        self.scene = scene
        self.view = view

        self.parameters = Parameters()

        splitter = QSplitter()
        splitter.addWidget(self.toolbox)
        splitter.addWidget(view)
        splitter.addWidget(self.parameters)
        splitter.setSizes([100, 400, 100])

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(splitter)

        central_widget = QWidget(parent=self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.view.node_dropped_signal.connect(self.new_node_selected)
        self.view.context_menu_signal.connect(self.context_menu)

        toolbar = self.addToolBar('Run')
        action = toolbar.addAction('&Run')
        action.setIcon(QIcon(path + '/icons/run.jpg'))
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
        action = file_menu.addAction('&Reload Nodes')
        action.setShortcut(QtGui.QKeySequence('F3'))
        action.triggered.connect(self.refresh_nodes)

        file_menu.addSeparator()

        action = file_menu.addAction('&Exit')
        action.setShortcut(QtGui.QKeySequence('Ctrl+q'))
        action.triggered.connect(self.exit_app)

        edit_menu = self.menuBar().addMenu('&Edit')

        self._create_actions()

        edit_menu.addAction(self.group_action)

        edit_menu.addAction(self.empty_group_action)

        edit_menu.addSeparator()
        edit_menu.addAction(self.copy_action)
        edit_menu.addAction(self.paste_action)
        edit_menu.addAction(self.delete_action)

        edit_menu.addSeparator()
        action = edit_menu.addAction('&Select All')
        action.setShortcut(QtGui.QKeySequence('Ctrl+a'))
        action.triggered.connect(self.select_all)

        view_menu = self.menuBar().addMenu('&View')
        action = view_menu.addAction('&Sow/Hide names')
        action.setShortcut(QtGui.QKeySequence('Ctrl+.'))
        action.triggered.connect(lambda x: self.scene.toggle_labels())

        self.menuBar().addSeparator()

        run_menu = self.menuBar().addMenu('Process')

        action = run_menu.addAction('&Create new process')
        action.setShortcut(QtGui.QKeySequence('Ctrl+r'))
        action.triggered.connect(lambda x: self.spawn(background=False))

        action = run_menu.addAction('&Create new background process')
        action.setShortcut(QtGui.QKeySequence('Ctrl+Shift+r'))
        action.triggered.connect(lambda x: self.spawn(background=True))

        help_menu = self.menuBar().addMenu('Help')
        action = help_menu.addAction('About')
        action.triggered.connect(lambda x: show_splashscreen(animate=False))

        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(QIcon(path + '/icons/waves.003.png'))
        self.trayIcon.setVisible(True)
        self.trayIcon.activated.connect(self.showNormal)

        self.trayIconMenu = QMenu(self)
        self.trayIconMenu.addAction('Show/Hide Window').triggered.connect(self.toggle_visible)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction('Exit').triggered.connect(self.exit_app)

        self.trayIcon.setContextMenu(self.trayIconMenu)

        app = QApplication.instance()
        app.trayIcon = self.trayIcon

    def _populate_toolbox(self):
        self.toolbox.clear()
        self.toolbox.addSections(node_categories)
        for node_name, event_node in register.node_registry.items():
            self.toolbox.addItem(
                ToolItem(icon=QIcon(path + '/icons/flow.png'), label=node_name, sections=event_node.categories,
                         tooltip=event_node.description))

    def _create_actions(self):
        self.group_action = QAction('&Group Selection')
        self.group_action.setShortcut(QtGui.QKeySequence('Ctrl+G'))
        self.group_action.triggered.connect(self.group_selected)

        self.empty_group_action = QAction('&Empty Group')
        self.empty_group_action.setShortcut(QtGui.QKeySequence('Ctrl+Alt+G'))
        self.empty_group_action.triggered.connect(self.new_group)

        self.copy_action = QAction('&Copy')
        self.copy_action.setShortcut(QtGui.QKeySequence('Ctrl+c'))
        self.copy_action.triggered.connect(self.copy_selected)

        self.paste_action = QAction('&Paste')
        self.paste_action.setShortcut(QtGui.QKeySequence('Ctrl+v'))
        self.paste_action.triggered.connect(self.paste_selected)

        self.delete_action = QAction('&Delete')
        self.delete_action.setShortcut(QtGui.QKeySequence('Delete'))
        self.delete_action.triggered.connect(self.delete_selected)

    # @Slot()
    def start_thread(self):
        self.thread_ = eventnodes.base.Worker(parent=self)
        self.thread_.start()

    # @Slot()
    def stop_thread(self):
        self.scene.clear()
        self.thread_.exit()
        self.thread_.wait(QtCore.QDeadlineTimer(10000))  # wait 10sec if the thread is still running

    def spawn(self, background=True):
        import subprocess

        py_path = sys.executable
        app_path = os.path.abspath(__file__)
        json_string = self.dump_json()

        args = [py_path, app_path, '--load-json', json_string]
        if background:
            args = [py_path, app_path, '--background', '--load-json', json_string]

        proc_ = subprocess.Popen(args,
                                 creationflags=subprocess.CREATE_NEW_CONSOLE,
                                 close_fds=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 shell=False)

    def load_data(self, data):
        new_nodes = {}
        for node in data['nodes']:
            type_ = node['node_obj'].split('.')[-1]
            n = self.scene.create_node_of_type(type_)
            if not n:
                print('WARNING: was unable to create node of type', type_)
                continue
            n.node_obj.moveToThread(self.thread_)
            n.node_obj.obj_id = node['id']
            n.node_obj.set_active(node.get('active', True))
            n.setPos(*node['position'])
            n.setSize(*node.get('size', (100, 100)))

            new_nodes[n] = node

        # TODO: when saving files out, edges come in arbitrary order. so nodes with dynamic inputs need to be connected in the right order. sorting here is kind of hack to get the order right
        for edge in sorted(data['edges'], key=lambda edge_pair: edge_pair[1]):
            source, target = edge
            s_obj_id, s_plug = source.split('.')
            t_obj_id, t_plug = target.split('.')

            source_plug = target_plug = None
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

            if source_plug and target_plug:
                self.scene.create_edge(source_plug, target_plug)

        for n, node in new_nodes.items():
            for pluggable, params in node.get('params', {}).items():
                pluggable = int(pluggable)
                for param, value in params.items():
                    if type(value) == list:
                        p = n.node_obj.get_first_param(param, pluggable=pluggable)
                        from eventnodes.params import StringParam
                        s = []
                        for item in value:
                            s.append(StringParam(value=item))

                        p.value.clear()
                        p.value.extend(s)
                        continue
                    p = n.node_obj.get_first_param(param, pluggable=pluggable)
                    from enum import Enum
                    if not p:
                        continue
                    if issubclass(p.value.__class__, Enum):
                        p._value = p.enum(value)
                    else:
                        p._value = value
            n.node_obj.update()

        for group in data['groups']:
            g = self.scene.create_group()
            g.setPos(*group['position'])
            g.setSize(*group['size'])

            # print(data)

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

        self.unsaved = False
        self.filename = file_name
        self.saved_data = {}

    def save_file(self, file_name):
        data = self.save_data()
        with open(file_name, 'w') as fp:
            json.dump(data, fp, indent=4)

        self.unsaved = False
        self.filename = file_name

    def keyPressEvent(self, event):
        pass

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

        self.unsaved = True

    @Slot()
    def group_selected(self):
        self.scene.group_selected_nodes()

        self.unsaved = True

    @Slot()
    def delete_selected(self):
        self.scene.remove_selected_nodes()
        self.scene.remove_selected_groups()

        self.unsaved = True
        self.parameters.set_node_obj(None)

    @Slot()
    def select_all(self):
        self.scene.select_all()

    # TODO this function is almost identical to save_data
    @Slot()
    def copy_selected(self):
        data = {'nodes': [], 'edges': [], 'groups': []}
        # selected_nodes =  sorted(self.scene.get_selected_nodes(), key=lambda n: n.pos().x())

        for node in sorted(self.scene.get_selected_nodes(), key=lambda n: (n.pos().x(), n.pos().y())):
            data['nodes'].append(node.to_dict())

        all_ids = [n['id'] for n in data['nodes']]

        # TODO: should do edges and groups like nodes with to_dict()

        for edge in self.scene.get_all_edges():
            source_id = str(edge.source_plug.parentItem().node_obj.obj_id)
            target_id = str(edge.target_plug.parentItem().node_obj.obj_id)
            if (source_id in all_ids) and (target_id in all_ids):
                edge_info = (str(edge.source_plug.parentItem().node_obj.obj_id) + '.' + edge.source_plug.type_,
                             str(edge.target_plug.parentItem().node_obj.obj_id) + '.' + edge.target_plug.type_)
                data['edges'].append(edge_info)

        # for group in self.scene.get_selected_groups():
        for group in sorted(self.scene.get_selected_groups(), key=lambda g: (g.pos().x(), g.pos().y())):
            data['groups'].append(
                {'position': (group.pos().x(), group.pos().y()),
                 'size': (group.width, group.height)
                 }
            )

        self.saved_data = data

    # TODO this function is almost identical to load_data
    @Slot()
    def paste_selected(self):

        pos = self.view.mapFromGlobal(QtGui.QCursor.pos())
        pos = self.view.mapToScene(pos)

        if not self.saved_data:
            return

        data = self.saved_data
        node_map = {}  # map from copied node id to newly created node id
        new_nodes = {}  # hold onto newly created nodes so that we can change the selection to them after paste

        relative_pos = None
        for node in data['nodes']:
            type_ = node['node_obj'].split('.')[-1]
            n = self.scene.create_node_of_type(type_)
            n.node_obj.moveToThread(self.thread_)
            n.node_obj.set_active(node.get('active', True))

            if not relative_pos:
                relative_pos = QtCore.QPointF(node['position'][0], node['position'][1])
                n.setPos(pos.x(), pos.y())
            else:
                offset_x = node['position'][0] - relative_pos.x()
                offset_y = node['position'][1] - relative_pos.y()

                n.setPos(pos.x() + offset_x, pos.y() + offset_y)

            # n.setPos(node['position'][0] + 20, node['position'][1] + 20)
            n.setSize(*node.get('size', (100, 100)))
            new_nodes[n] = node

            # map the id of the copied node to the id of the newly created one.
            # we'll need this to know how to reconnect the copied edges
            node_map[node['id']] = n.node_obj.obj_id

        # TODO: when saving files out, edges come in arbitrary order. so nodes with dynamic inputs need to be connected in the right order. sorting here is kind of hack to get the order right
        for edge in sorted(data['edges'], key=lambda edge_pair: edge_pair[1]):
            source, target = edge
            s_obj_id, s_plug = source.split('.')
            t_obj_id, t_plug = target.split('.')

            # remap the source and target nodes to the newly created nodes
            s_obj_id = node_map[s_obj_id]
            t_obj_id = node_map[t_obj_id]

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

            if source_plug and target_plug:
                self.scene.create_edge(source_plug, target_plug)

        for n, node in new_nodes.items():
            for pluggable, params in node.get('params', {}).items():
                pluggable = int(pluggable)
                for param, value in params.items():
                    if type(value) == list:
                        p = n.node_obj.get_first_param(param, pluggable=pluggable)
                        from eventnodes.params import StringParam
                        s = []
                        for item in value:
                            s.append(StringParam(value=item))

                        p.value.clear()
                        p.value.extend(s)
                        continue
                    p = n.node_obj.get_first_param(param, pluggable=pluggable)
                    from enum import Enum
                    if not p:
                        continue
                    if issubclass(p.value.__class__, Enum):
                        p._value = p.enum(value)
                    else:
                        p._value = value
            n.node_obj.update()

        for group in data['groups']:
            g = self.scene.create_group()
            # g.setPos(group['position'][0] + 20, group['position'][1] + 20)
            # g.setPos(pos.x(), pos.y())
            if not relative_pos:
                relative_pos = QtCore.QPointF(group['position'][0], group['position'][1])
                g.setPos(pos.x(), pos.y())
            else:
                offset_x = group['position'][0] - relative_pos.x()
                offset_y = group['position'][1] - relative_pos.y()

                g.setPos(pos.x() + offset_x, pos.y() + offset_y)

            g.setSize(*group['size'])
            new_nodes[g] = group

        self.scene.clearSelection()
        for n in new_nodes.keys():
            n.setSelected(True)

        self.copy_selected()

    @Slot(str, int, int)
    def new_node_selected(self, item, x=100, y=100):
        node = self.scene.create_node_of_type(item)
        node.node_obj.moveToThread(self.thread_)
        position = self.view.mapToScene(x, y)
        node.setPos(position)
        self.scene.select_node(node)

        self.unsaved = True

    @Slot(int, int)
    def context_menu(self, x, y):
        def get_nodes_by_category():
            from collections import defaultdict
            nodes_by_categories = defaultdict(list)

            for category in node_categories:  # prime with default category set to get desired order in UI
                nodes_by_categories[category] = []

            for node_name, node_obj in register.node_registry.items():
                for category in node_obj.categories:
                    nodes_by_categories[category].append(node_name)

            return nodes_by_categories

        def show_options_menu():
            menu = QMenu(self)
            menu.exec_(self.view.mapToGlobal(QtCore.QPoint(x, y)))

        def show_new_nodes_menu():
            menu = QMenu(self)

            new_node_menu = menu.addMenu('Add Node')
            for category, node_names in get_nodes_by_category().items():
                submenu = new_node_menu.addMenu(category)
                for node_name in node_names:
                    submenu.addAction(node_name,
                                      lambda node_name=node_name: self.new_node_selected(node_name, x + 1,
                                                                                         y))  # TODO: if I dont add 1 here, the app will crash when setPos is called in the slot function

            menu.addSeparator()
            menu.addAction(self.group_action)
            menu.addAction(self.copy_action)
            menu.addAction(self.paste_action)
            menu.addAction(self.delete_action)
            menu.exec_(self.view.mapToGlobal(QtCore.QPoint(x, y)))

        node = self.view.get_node_at(QtCore.QPoint(x, y))
        # if node:
        #     show_options_menu()
        # else:
        show_new_nodes_menu()

    @Slot(list)
    def selected_nodes(self, nodes):
        if nodes:
            self.parameters.set_node_obj(nodes[0].node_obj)
        else:
            self.parameters.set_node_obj(None)

    @Slot()
    def items_moved(self):
        self.unsaved = True

    def save_changes_dialog(self):
        """

        :return: True if okay to continue, otherwise False
        """
        if self.unsaved:
            filename = os.path.basename(self.filename) if self.filename else 'Untitled'
            save_dialog = QMessageBox()
            save_dialog.setWindowTitle("Save changes to '{filename}' before closing?".format(filename=filename))
            save_dialog.setText("Changes will be lost if you don't save them")
            save_dialog.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            save_dialog.setDefaultButton(QMessageBox.Save)

            ret = save_dialog.exec_()
            if ret == QMessageBox.Save:
                self.save_scene()
                return True
            elif ret == QMessageBox.Discard:
                return True
            elif ret == QMessageBox.Cancel:
                return False

        return True

    @Slot()
    def refresh_nodes(self):
        register.reload_node_registry()
        self._populate_toolbox()

    @Slot()
    def new_scene(self):
        if self.save_changes_dialog():
            self.stop_thread()
            self.stop_timers()
            self.start_thread()  # TODO: do i need this? test removing it.
            self.scene.clear()

            self.filename = None
            self.unsaved = False
            self.saved_data = {}

    @Slot()
    def open_scene(self):
        if self.save_changes_dialog():
            filename, filter_ = QFileDialog.getOpenFileName(self, 'Open Scene', os.getcwd(), 'Scene Files (*.json)')
            if filename:
                self.stop_thread()
                self.stop_timers()
                self.scene.clear()
                self.start_thread()  # TODO: do i need this? test removing it.
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

    def toggle_visible(self):
        self.setVisible(not self.isVisible())

    @Slot()
    def exit_app(self):
        self.stop_thread()
        self.thread_.deleteLater()
        qapp = QApplication.instance()
        qapp.exit()

    def closeEvent(self, event):
        if not event.spontaneous() or not self.isVisible():
            return

        self.hide()
        event.ignore()


def show_about(parent):
    show_splashscreen(animate=False)


def show_splashscreen(animate=False):
    splash_pix = QtGui.QPixmap(path + '/icons/splashscreen.002.png')
    splash = SplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.showMessage(splash.tr("Subotai 1.0.0 Beta"),
                       QtCore.Qt.AlignBottom or QtCore.Qt.AlignHCenter,
                       color=QtGui.QColor(255, 255, 255))

    splash.show()
    if animate:
        import time
        opaqueness = 0.0
        step = 0.05
        splash.setWindowOpacity(opaqueness)
        splash.show()

        while opaqueness < 1.1:
            splash.setWindowOpacity(opaqueness)
            time.sleep(step)
            opaqueness += (1 * step)
        time.sleep(2)
        splash.close()
        return

    splash.show()


def set_params(scene, params={}):
    for node in scene.get_all_nodes():
        if isinstance(node.node_obj, eventnodes.parameter.ParamNode):
            promote_state = node.node_obj.get_first_param('promote state')
            promote_name = node.node_obj.get_first_param('promote name')
            param = node.node_obj.get_first_param('param')

            if promote_state.value:
                if promote_name.value in params:
                    value = param.cast(params[promote_name.value])  # cast it to the type of the param
                    param.value = value


def print_params_from_scene(scene):
    promoted_params = {}
    for node in scene.get_all_nodes():
        if isinstance(node.node_obj, eventnodes.parameter.ParamNode):
            promote_state = node.node_obj.get_first_param('promote state')
            promote_name = node.node_obj.get_first_param('promote name')
            param = node.node_obj.get_first_param('param')

            if promote_state.value:
                promoted_params[promote_name.value] = str(node.node_obj.type)

    print('{name} {type}'.format(name='PARAMETER NAME'.ljust(25), type=('PARAMETER TYPE').ljust(25)))
    print('{name} {type}'.format(name='--------------'.ljust(25), type=('--------------').ljust(25)))
    for n, t in promoted_params.items():
        print('{name} {type}'.format(name=n.ljust(25), type=t.ljust(25)))


def print_params_from_data(data):
    promoted_params = {}
    for node in data['nodes']:
        state = node.get('params', {}).get('0', {}).get('promote state', False)
        name = node.get('params', {}).get('0', {}).get('promote name', '')

        if state:
            promoted_params[name] = node['node_obj'].split('.')[-1]

    print('{name} {type}'.format(name='PARAMETER NAME'.ljust(25), type=('PARAMETER TYPE').ljust(25)))
    print('{name} {type}'.format(name='--------------'.ljust(25), type=('--------------').ljust(25)))
    for n, t in promoted_params.items():
        print('{name} {type}'.format(name=n.ljust(25), type=t.ljust(25)))


def main(splashscreen=True, background=False, scene_file=None, json_string=None, list_params=False, params={}):
    register.reload_node_registry()

    if list_params:
        with open(scene_file, 'r') as fp:
            data = json.load(fp)
        print_params_from_data(data=data)
        sys.exit()

    app = QApplication(sys.argv)
    app.startingUp()
    app.setWindowIcon(QIcon(path + "/icons/waves.003.png"))

    main_window = MainWindow()
    main_window.start_thread()  # TODO: I seem to need this, otherwise moveToThread of Worker thread doesnt work in all situations. Somethign to do with when signals are created and emitted
    # QtCore.QTimer(app).singleShot(0, self.start_thread)
    main_window.setWindowTitle('Subotai')
    main_window.setWindowIcon(QIcon(path + "/icons/waves.003.png"))

    if scene_file:
        main_window.load_file(scene_file)
    else:
        if json_string:
            main_window.load_json(json_string)

    set_params(scene=main_window.scene, params=params)

    if background:
        import signal as signal_
        signal_.signal(signal_.SIGINT, signal_.SIG_DFL)  # accept ctrl-c signal when in background mode to quit
    else:
        if splashscreen:
            show_splashscreen(animate=True)

        main_window.move(600, 200)  # TODO: Calculate center of desktop to position the MainWindow
        main_window.show()
    # app.aboutToQuit.connect(main_window.stop_thread)
    return app, main_window


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--splash", action='store_true', default=False,
                        help="show startup splashscreen (only in GUI mode)")
    parser.add_argument("--background", action='store_true', help="run in a background process (no GUI)")
    parser.add_argument('--list-params', action='store_true',
                        help='list the params available in the given scene file')
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--load-file", type=str, metavar='<FILENAME>',
                       help="loads the given scene .json file in")
    group.add_argument("--load-json", type=str, metavar='<JSON STRING>',
                       help="loads the given json string in")

    # TODO: just grabbed this one-liner off the web. Worth revisiting to make clearer
    parser.add_argument('--param', action=type('', (argparse.Action,), dict(
        __call__=lambda a, p, n, v, o: getattr(n, a.dest).update(dict([v.split('=')])))),
                        default={}, dest='params')  # anonymously subclassing argparse.Action

    args = parser.parse_args()

    background = args.background
    list_params = args.list_params

    scene_file = None
    if args.load_file:
        scene_file = os.path.abspath(args.load_file)

    json_string = None
    if args.load_json:
        json_string = args.load_json

    splashscreen = args.splash

    params = args.params

    app, main_window = main(background=background, scene_file=scene_file, json_string=json_string,
                            splashscreen=splashscreen, list_params=list_params, params=params)
    sys.exit(app.exec_())
