import argparse
import json
import os
import sys

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

from pywerlines import pyweritems

from ui.parameters import Parameters
from ui.toolbox import ToolBox, ToolItem
from ui.splashscreen import SplashScreen

from appscene import AppScene
from appview import AppView

import commands
import actions
import config
import register
import eventnodes
import scenetools


@QtCore.Slot(list)
def selected_nodes(data):
    pass


@QtCore.Slot(list)
def added_nodes(data):
    pass


@QtCore.Slot(list)
def deleted_nodes(data):
    pass


@QtCore.Slot(pyweritems.PywerPlug, pyweritems.PywerPlug)
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


@QtCore.Slot(pyweritems.PywerPlug, pyweritems.PywerPlug)
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


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Subotai')
        self.setWindowIcon(QtGui.QIcon(config.path + "/icons/icon.png"))

        self.view = AppView()
        self.scene = AppScene()
        self.scene.setSceneRect(0, 0, 100000, 100000)
        self.scene.setItemIndexMethod(self.scene.NoIndex)
        self.view.setScene(self.scene)

        self.undo_stack = QtWidgets.QUndoStack()

        self.filename = None
        self.unsaved = False
        self.saved_data = None

        self.toolbox = ToolBox()
        self._populate_toolbox()
        self.toolbox.itemDoubleClickedSignal.connect(self.new_node_selected)

        self.scene.nodes_selected.connect(selected_nodes)
        self.scene.nodes_deleted.connect(deleted_nodes)
        self.scene.nodes_added.connect(added_nodes)
        self.scene.plugs_connected.connect(connected_plugs)
        self.scene.plugs_disconnected.connect(disconnected_plugs)
        self.scene.nodes_selected.connect(self.selected_nodes)
        self.scene.items_moved.connect(self.items_moved)

        self.parameters = Parameters()
        self.parameters.parameter_changed.connect(self.parameter_changed)

        splitter = QtWidgets.QSplitter()
        splitter.addWidget(self.toolbox)
        splitter.addWidget(self.view)
        splitter.addWidget(self.parameters)
        splitter.setSizes([100, 400, 100])

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(splitter)
        central_widget = QtWidgets.QWidget(parent=self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.view.node_dropped_signal.connect(self.new_node_selected)
        self.view.context_menu_signal.connect(self.context_menu)

        self.actions_map = actions.ActionMap()
        self._init_actions(config.action_shortcuts, self.actions_map)

        toolbar = self.addToolBar('Run')
        toolbar.addAction(self.actions_map.get_action('run'))

        file_menu = self.menuBar().addMenu('&File')
        file_menu.addAction(self.actions_map.get_action('new_scene'))
        file_menu.addAction(self.actions_map.get_action('open_scene'))
        file_menu.addSeparator()
        file_menu.addAction(self.actions_map.get_action('save_scene'))
        file_menu.addAction(self.actions_map.get_action('save_scene_as'))
        file_menu.addSeparator()
        file_menu.addAction(self.actions_map.get_action('reload'))
        file_menu.addSeparator()
        file_menu.addAction(self.actions_map.get_action('exit'))

        edit_menu = self.menuBar().addMenu('&Edit')
        edit_menu.addAction(self.actions_map.get_action('undo'))
        edit_menu.addAction(self.actions_map.get_action('redo'))
        edit_menu.addSeparator()
        edit_menu.addAction(self.actions_map.get_action('group'))
        edit_menu.addAction(self.actions_map.get_action('empty_group'))
        edit_menu.addSeparator()
        edit_menu.addAction(self.actions_map.get_action('copy'))
        edit_menu.addAction(self.actions_map.get_action('paste'))
        edit_menu.addAction(self.actions_map.get_action('delete'))
        edit_menu.addSeparator()
        edit_menu.addAction(self.actions_map.get_action('select_all'))
        edit_menu.addAction(self.actions_map.get_action('toggle_names'))

        view_menu = self.menuBar().addMenu('&View')
        view_menu.addAction(self.actions_map.get_action('toggle_names'))

        self.menuBar().addSeparator()
        run_menu = self.menuBar().addMenu('Process')
        run_menu.addAction(self.actions_map.get_action('new_process'))
        run_menu.addAction(self.actions_map.get_action('new_background_process'))

        help_menu = self.menuBar().addMenu('Help')
        help_menu.addAction(self.actions_map.get_action('about'))

        self.trayIconMenu = QtWidgets.QMenu(self)
        self.trayIconMenu.addAction(self.actions_map.get_action('toggle_window'))
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.actions_map.get_action('exit'))

        self.trayIcon = QtWidgets.QSystemTrayIcon(self)
        self.trayIcon.setIcon(QtGui.QIcon(config.path + '/icons/icon.png'))
        self.trayIcon.setVisible(True)
        self.trayIcon.activated.connect(self.showNormal)
        self.trayIcon.setContextMenu(self.trayIconMenu)

        QtWidgets.QApplication.instance().trayIcon = self.trayIcon

    def _update_window_title(self):
        title = 'Subotai'

        if self.filename:
            title += ' - {}'.format(self.filename)

        if self.unsaved:
            title += '*'

        self.setWindowTitle(title)

    def _populate_toolbox(self):
        self.toolbox.clear()
        self.toolbox.addSections(config.node_categories)
        for node_name, event_node in register.node_registry.items():
            self.toolbox.addItem(
                ToolItem(icon=QtGui.QIcon(config.path + '/icons/flow.png'), label=node_name,
                         sections=event_node.categories,
                         tooltip=event_node.description))

    def _init_actions(self, action_shortcuts, action_map):

        # set action shortcuts
        for action_name, shortcut in action_shortcuts.items():
            action = action_map.get_action(action_name)
            if action:
                action.setShortcut(QtGui.QKeySequence(shortcut))

        # set action icons
        self.actions_map.get_action('run').setIcon(QtGui.QIcon(config.path + '/icons/run.jpg'))

        # set action slots
        self.actions_map.get_action('group').triggered.connect(self.group_selected)
        self.actions_map.get_action('empty_group').triggered.connect(self.new_group)
        self.actions_map.get_action('copy').triggered.connect(self.copy_selected)
        self.actions_map.get_action('paste').triggered.connect(self.paste_selected)
        self.actions_map.get_action('delete').triggered.connect(self.delete_selected)
        self.actions_map.get_action('run').triggered.connect(lambda x: self.scene.eval())
        self.actions_map.get_action('new_scene').triggered.connect(self.new_scene)
        self.actions_map.get_action('open_scene').triggered.connect(self.open_scene)
        self.actions_map.get_action('save_scene').triggered.connect(self.save_scene)
        self.actions_map.get_action('save_scene_as').triggered.connect(self.save_scene_as)
        self.actions_map.get_action('reload').triggered.connect(self.refresh_nodes)
        self.actions_map.get_action('undo').triggered.connect(self.undo)
        self.actions_map.get_action('redo').triggered.connect(self.redo)

        self.actions_map.get_action('exit').triggered.connect(self.exit_app)
        self.actions_map.get_action('select_all').triggered.connect(self.select_all)
        self.actions_map.get_action('toggle_names').triggered.connect(lambda x: self.scene.toggle_names())
        self.actions_map.get_action('new_process').triggered.connect(lambda x: self.spawn(background=False))
        self.actions_map.get_action('new_background_process').triggered.connect(lambda x: self.spawn(background=True))
        self.actions_map.get_action('about').triggered.connect(lambda x: show_splashscreen(animate=False))
        self.actions_map.get_action('toggle_window').triggered.connect(self.toggle_visible)

    # @QtCore.Slot()
    def start_thread(self):
        self.thread_ = eventnodes.base.Worker(parent=self)
        self.thread_.start()

    # @QtCore.Slot()
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
        new_items = scenetools.load_scene_data(self.scene, data, pos=None)
        for n in new_items.keys():
            if isinstance(n, pyweritems.PywerNode):
                n.node_obj.moveToThread(self.thread_)

    def save_data(self):
        return scenetools.get_scene_data(self.scene, selected=False)

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

        self._update_window_title()

    def save_file(self, file_name):
        data = self.save_data()
        with open(file_name, 'w') as fp:
            json.dump(data, fp, indent=4)

        self.unsaved = False
        self.filename = file_name

        self._update_window_title()

    def keyPressEvent(self, event):
        pass

    def deactivate_event_nodes(self):
        scene_nodes = self.scene.list_nodes()
        for node in scene_nodes:
            node.stop_spinner()
            if node.node_obj.is_computable():
                node.node_obj.unset_ui_node()

        timers = [item for item in scene_nodes if isinstance(item.node_obj, eventnodes.base.EventNode)]
        for timer in timers:
            timer.node_obj.deactivate()

    @QtCore.Slot()
    def new_group(self):
        position = QtCore.QPointF(self.view.mapToScene(self.view.mouse_position))
        scenetools.create_group(self.scene, position)

        self.unsaved = True
        self._update_window_title()

    @QtCore.Slot()
    def group_selected(self):
        scenetools.group_selected_nodes(self.scene)

        self.unsaved = True
        self._update_window_title()

    @QtCore.Slot()
    def delete_selected(self):
        scenetools.delete_selected(self.scene)

        self.unsaved = True
        self.parameters.set_node_obj(None)
        self._update_window_title()

    @QtCore.Slot()
    def select_all(self):
        scenetools.select_all(self.scene)

    @QtCore.Slot()
    def copy_selected(self):
        self.saved_data = scenetools.get_scene_data(self.scene, selected=True)

    @QtCore.Slot()
    def paste_selected(self):
        if not self.saved_data:
            return

        pos = self.view.mapFromGlobal(QtGui.QCursor.pos())
        pos = self.view.mapToScene(pos)

        new_items = scenetools.load_scene_data(self.scene, self.saved_data, pos=pos)
        new_items = new_items.keys()

        new_nodes = [n for n in new_items if isinstance(n, pyweritems.PywerNode)]
        for n in new_nodes:
            n.node_obj.moveToThread(self.thread_)

        scenetools.select(self.scene, items=new_items)
        self.copy_selected()

    @QtCore.Slot(str, int, int)
    def new_node_selected(self, item, x=100, y=100):
        node = self.scene.create_node_of_type(item)
        node.node_obj.moveToThread(self.thread_)
        position = self.view.mapToScene(x, y)
        node.setPos(position)

        scenetools.select(self.scene, items=[node])

        self.unsaved = True
        self._update_window_title()

    @QtCore.Slot(int, int)
    def context_menu(self, x, y):
        def get_nodes_by_category():
            from collections import defaultdict
            nodes_by_categories = defaultdict(list)

            for category in config.node_categories:  # prime with default category set to get desired order in UI
                nodes_by_categories[category] = []

            for node_name, node_obj in register.node_registry.items():
                for category in node_obj.categories:
                    nodes_by_categories[category].append(node_name)

            return nodes_by_categories

        def show_options_menu():
            menu = QtWidgets.QMenu(self)
            menu.exec_(self.view.mapToGlobal(QtCore.QPoint(x, y)))

        def show_new_nodes_menu():
            menu = QtWidgets.QMenu(self)

            new_node_menu = menu.addMenu('Add Node')
            for category, node_names in get_nodes_by_category().items():
                submenu = new_node_menu.addMenu(category)
                for node_name in node_names:
                    submenu.addAction(node_name,
                                      lambda node_name=node_name: self.new_node_selected(node_name, x + 1,
                                                                                         y))  # TODO: if I dont add 1 here, the app will crash when setPos is called in the slot function

            menu.addSeparator()
            menu.addAction(self.actions_map.get_action('group'))
            menu.addAction(self.actions_map.get_action('copy'))
            menu.addAction(self.actions_map.get_action('paste'))
            menu.addAction(self.actions_map.get_action('delete'))
            menu.exec_(self.view.mapToGlobal(QtCore.QPoint(x, y)))

        node = self.view.get_node_at(QtCore.QPoint(x, y))
        # if node:
        #     show_options_menu()
        # else:
        show_new_nodes_menu()

    @QtCore.Slot(list)
    def selected_nodes(self, items):
        print(items)
        self.undo_stack.beginMacro('selection changed')
        for item in items:
            self.undo_stack.push(commands.SelectionChanged(item))
        self.undo_stack.endMacro()

        nodes = self.scene.get_selected_nodes()
        if nodes:
            self.parameters.set_node_obj(nodes[0].node_obj)
        else:
            self.parameters.set_node_obj(None)

    @QtCore.Slot(list)
    def items_moved(self, items, ):
        self.undo_stack.beginMacro('items moved')
        for item in items:
            self.undo_stack.push(commands.ItemMoved(item))
        self.undo_stack.endMacro()

        self.unsaved = True
        self._update_window_title()

    @QtCore.Slot()
    def undo(self):
        self.undo_stack.undo()

    @QtCore.Slot()
    def redo(self):
        self.undo_stack.redo()

    @QtCore.Slot()
    def parameter_changed(self):
        self.unsaved = True
        self._update_window_title()

    def save_changes_dialog(self):
        """

        :return: True if okay to continue, otherwise False
        """
        if self.unsaved:
            filename = os.path.basename(self.filename) if self.filename else 'Untitled'
            save_dialog = QtWidgets.QMessageBox()
            save_dialog.setWindowTitle("Save changes to '{filename}' before closing?".format(filename=filename))
            save_dialog.setText("Changes will be lost if you don't save them")
            save_dialog.setStandardButtons(
                QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel)
            save_dialog.setDefaultButton(QtWidgets.QMessageBox.Save)

            ret = save_dialog.exec_()
            if ret == QtWidgets.QMessageBox.Save:
                self.save_scene()
                return True
            elif ret == QtWidgets.QMessageBox.Discard:
                return True
            elif ret == QtWidgets.QMessageBox.Cancel:
                return False

        return True

    @QtCore.Slot()
    def refresh_nodes(self):
        register.reload_node_registry()
        self._populate_toolbox()

    @QtCore.Slot()
    def new_scene(self):
        if self.save_changes_dialog():
            self.deactivate_event_nodes()
            self.stop_thread()
            self.start_thread()  # TODO: do i need this? test removing it.
            self.scene.clear()

            self.filename = None
            self.unsaved = False
            self.saved_data = {}

            self._update_window_title()

    @QtCore.Slot()
    def open_scene(self):
        if self.save_changes_dialog():
            filename, filter_ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Scene', os.getcwd(),
                                                                      'Scene Files (*.json)')
            if filename:
                self.deactivate_event_nodes()
                self.stop_thread()
                self.scene.clear()
                self.start_thread()  # TODO: do i need this? test removing it.
                self.load_file(filename)

                self._update_window_title()

    @QtCore.Slot()
    def save_scene_as(self):
        filename, filter_ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Scene', os.getcwd(),
                                                                  'Scene Files (*.json)')
        if filename:
            self.save_file(filename)

    @QtCore.Slot()
    def save_scene(self):
        if self.filename:
            self.save_file(self.filename)
        else:
            self.save_scene_as()
        self._update_window_title()

    def toggle_visible(self):
        self.setVisible(not self.isVisible())

    @QtCore.Slot()
    def exit_app(self):
        self.stop_thread()
        self.thread_.deleteLater()
        qapp = QtWidgets.QApplication.instance()
        qapp.exit()

    def closeEvent(self, event):
        if not event.spontaneous() or not self.isVisible():
            return

        self.hide()
        event.ignore()


def show_about(parent):
    show_splashscreen(animate=False)


def show_splashscreen(animate=False):
    splash_pix = QtGui.QPixmap(config.path + '/icons/splashscreen.png')
    splash = SplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.showMessage(splash.tr("Subotai " + config.version),
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

    app = QtWidgets.QApplication(sys.argv)
    app.startingUp()
    app.setWindowIcon(QtGui.QIcon(config.path + "/icons/icon.png"))

    main_window = MainWindow()
    main_window.start_thread()  # TODO: I seem to need this, otherwise moveToThread of Worker thread doesnt work in all situations. Somethign to do with when signals are created and emitted
    # QtCore.QTimer(app).singleShot(0, self.start_thread)

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
