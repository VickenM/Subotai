import os
import pkgutil
import inspect
import sys
import importlib

import config
import eventnodes

node_registry = {}


def _register_nodes_module(mod):
    for importer, modname, ispkg in pkgutil.iter_modules(mod.__path__, mod.__name__ + '.'):
        if ispkg:
            try:
                pkg = importlib.import_module(modname)
                importlib.reload(pkg)
            except Exception as e:
                print('Error: Unable to load node package {} {}'.format(modname, e))
                continue
            _register_nodes_module(pkg)
        else:
            try:
                module = importlib.import_module(modname)
                importlib.reload(module)
            except Exception as e:
                print('Error: Unable to load node module {} {}'.format(modname, e))
                continue
            for name, obj in inspect.getmembers(module, lambda member: inspect.isclass(member) and (
                    member.__module__.startswith(mod.__name__ + '.'))):

                if not issubclass(obj, eventnodes.base.BaseNode):
                    continue

                # skip classes that dont have a type attr. they're not nodes, or they're base classes (BaseNode, ComputeNode, EventNode)
                if not hasattr(obj, 'type'):
                    continue

                # if obj.type in node_registry:
                #     print('ERROR: Node with name', obj.type, 'can only be added once')
                #     continue
                node_registry[obj.type] = obj


def register_addon_nodes_module():
    addons_path = os.getenv(config.addons_env_var)
    if addons_path:
        if addons_path not in sys.path:
            sys.path.append(addons_path)
        if addons_path + '/modules' not in sys.path:
            sys.path.append(addons_path + '/modules')
        try:
            import nodes
            importlib.reload(nodes)
        except ImportError as e:
            print('Error: unable to include nodes from addons path {}'.format(e))
        else:
            _register_nodes_module(nodes)


def register_core_nodes_module():
    _register_nodes_module(eventnodes)


def clear_node_registry():
    global node_registry
    node_registry = {}
