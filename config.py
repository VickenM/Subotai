import os

version = '0.1.0'

path = os.path.dirname(os.path.abspath(__file__))

addons_env_var = 'SUBOTAI_ADDONS'

# default set of categories in desired order for ui elements
node_categories = ['Events', 'FileSystem', 'Data', 'Math', 'String', 'Flow Control', 'Image', 'I/O']

action_shortcuts = {
    'group': 'Ctrl+G',
    'empty_group': 'Ctrl+Alt+G',
    'copy': 'Ctrl+c',
    'paste': 'Ctrl+v',
    'delete': 'Delete',
    'select_all': 'Ctrl+a',
    'toggle_names': 'Ctrl+.',
    'run': 'Space',
    'new_scene': 'Ctrl+n',
    'open_scene': 'Ctrl+o',
    'save_scene': 'Ctrl+s',
    'save_scene_as': 'Ctrl+Shift+s',
    'exit': 'Ctrl+q',
    'undo': 'Ctrl+z',
    'redo': 'Ctrl+Shift+z',
    'reload': 'F3',
    'new_process': 'Ctrl+r',
    'new_background_process': 'Ctrl+Shift+r',
 }
