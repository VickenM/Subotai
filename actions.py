from PySide2 import QtWidgets
from PySide2 import QtGui


class ActionMap:
    def __init__(self):
        self._actions = {
            'group': QtWidgets.QAction('&Group Selection'),
            'empty_group': QtWidgets.QAction('&Empty Group'),
            'copy': QtWidgets.QAction('&Copy'),
            'paste': QtWidgets.QAction('&Paste'),
            'delete': QtWidgets.QAction('&Delete'),
            'run': QtWidgets.QAction('&Run'),
            'new_scene': QtWidgets.QAction('&New Scene'),
            'open_scene': QtWidgets.QAction('&Open Scene'),
            'save_scene': QtWidgets.QAction('&Save Scene'),
            'save_scene_as': QtWidgets.QAction('&Save Scene As'),
            'exit': QtWidgets.QAction('&Exit'),
            'select_all': QtWidgets.QAction('&Select All'),
            'toggle_names': QtWidgets.QAction('&Show/Hide Names'),
            'reload': QtWidgets.QAction('&Reload Nodes'),
            'new_process': QtWidgets.QAction('&Create New Process'),
            'new_background_process': QtWidgets.QAction('&Create New Background Process'),
            'about': QtWidgets.QAction('About'),
            'help': QtWidgets.QAction('Help'),
            'toggle_window': QtWidgets.QAction('Show/Hide Window'),
        }

    def get_action(self, action):
        return self._actions.get(action)

    def set_action_shortcut(self, action, shortcut):
        action = self.get_action(action)
        if action:
            action.setShortcut(QtGui.QKeySequence(shortcut))
