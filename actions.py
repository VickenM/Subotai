from PySide6 import QtWidgets
from PySide6 import QtGui


class ActionMap:
    def __init__(self):
        self._actions = {
            'group': QtGui.QAction('&Group Selection'),
            'empty_group': QtGui.QAction('&Empty Group'),
            'copy': QtGui.QAction('&Copy'),
            'paste': QtGui.QAction('&Paste'),
            'delete': QtGui.QAction('&Delete'),
            'run': QtGui.QAction('&Run'),
            'new_scene': QtGui.QAction('&New Scene'),
            'open_scene': QtGui.QAction('&Open Scene'),
            'save_scene': QtGui.QAction('&Save Scene'),
            'save_scene_as': QtGui.QAction('&Save Scene As'),
            'exit': QtGui.QAction('&Exit'),
            'select_all': QtGui.QAction('&Select All'),
            'toggle_names': QtGui.QAction('&Show/Hide Names'),
            'reload': QtGui.QAction('&Reload Nodes'),
            'new_process': QtGui.QAction('&Create New Process'),
            'new_background_process': QtGui.QAction('&Create New Background Process'),
            'about': QtGui.QAction('About'),
            'help': QtGui.QAction('Help'),
            'toggle_window': QtGui.QAction('Show/Hide Window'),
            'undo': QtGui.QAction('Undo'),
            'redo': QtGui.QAction('Redo'),
        }

    def get_action(self, action):
        return self._actions.get(action)

    def set_action_shortcut(self, action, shortcut):
        action = self.get_action(action)
        if action:
            action.setShortcut(QtGui.QKeySequence(shortcut))
