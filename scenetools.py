from PySide2 import QtCore

from pywerlines import pyweritems

from appnode import new_node, new_group
import commands


def load_scene_data(scene, data, pos=None):
    node_map = {}  # map from copied node id to newly created node id
    new_nodes = {}  # hold onto newly created nodes so that we can change the selection to them after paste

    relative_pos = None
    for node in data['nodes']:
        type_ = node['node_obj'].split('.')[-1]
        n = new_node(type_)
        n.node_obj.set_active(node.get('active', True))

        if pos:
            if not relative_pos:
                relative_pos = QtCore.QPointF(node['position'][0], node['position'][1])
                n.setPos(pos.x(), pos.y())
            else:
                offset_x = node['position'][0] - relative_pos.x()
                offset_y = node['position'][1] - relative_pos.y()
                n.setPos(pos.x() + offset_x, pos.y() + offset_y)
        else:
            n.setPos(*node['position'])

        n.setSize(*node.get('size', (100, 100)))
        n.name.setPlainText(node.get('name', n.name_))

        scene.add_node(n)

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

        s_node = scene.get_node_by_id(s_obj_id)
        for o in s_node.outputs:
            if o.type_ == s_plug:
                source_plug = o
                break

        t_node = scene.get_node_by_id(t_obj_id)
        for o in t_node.inputs:
            if o.type_ == t_plug:
                target_plug = o
                break

        if source_plug and target_plug:
            scene.create_edge(source_plug, target_plug)

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
        g = new_group()
        if pos:
            if not relative_pos:
                relative_pos = QtCore.QPointF(group['position'][0], group['position'][1])
                g.setPos(pos.x(), pos.y())
            else:
                offset_x = group['position'][0] - relative_pos.x()
                offset_y = group['position'][1] - relative_pos.y()

                g.setPos(pos.x() + offset_x, pos.y() + offset_y)
        else:
            g.setPos(*group['position'])

        g.setSize(*group['size'])
        g.name.setPlainText(group.get('name', g.name_))
        scene.add_group(g)
        new_nodes[g] = group

    return new_nodes


def load_macro(context, undo_stack, data, pos=None):
    scene = context.get('scene')

    node_map = {}  # map from copied node id to newly created node id
    new_nodes = {}  # hold onto newly created nodes so that we can change the selection to them after paste

    relative_pos = None
    for node in data['nodes']:
        type_ = node['node_obj'].split('.')[-1]

        if pos:
            if not relative_pos:
                relative_pos = QtCore.QPointF(node['position'][0], node['position'][1])
                position = QtCore.QPointF(pos.x(), pos.y())
            else:
                offset_x = node['position'][0] - relative_pos.x()
                offset_y = node['position'][1] - relative_pos.y()
                position = QtCore.QPointF(pos.x() + offset_x, pos.y() + offset_y)
        else:
            position = QtCore.QPointF(*node['position'])

        size = QtCore.QSize(*node.get('size', (100, 100)))

        undo_stack.push(commands.AddNode(context, type_, position=position, size=size))
        n = scene.get_selected_nodes()[0]
        n.node_obj.set_active(node.get('active', True))
        n.name.setPlainText(node.get('name', n.name_))
        n.node_obj.obj_id = node['id']

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

        s_node = scene.get_node_by_id(s_obj_id)
        for o in s_node.outputs:
            if o.type_ == s_plug:
                source_plug = o
                break

        t_node = scene.get_node_by_id(t_obj_id)
        for o in t_node.inputs:
            if o.type_ == t_plug:
                target_plug = o
                break

        if source_plug and target_plug:
            undo_stack.push(commands.ConnectPlugs(context, source_plug, target_plug))

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
        if pos:
            if not relative_pos:
                relative_pos = QtCore.QPointF(group['position'][0], group['position'][1])
                position = QtCore.QPointF(pos.x(), pos.y())
            else:
                offset_x = group['position'][0] - relative_pos.x()
                offset_y = group['position'][1] - relative_pos.y()

                position = QtCore.QPointF(pos.x() + offset_x, pos.y() + offset_y)
        else:
            position = QtCore.QPointF(*group['position'])

        size = QtCore.QSize(*group['size'])

        undo_stack.push(commands.AddGroup(context, position, size))
        g = scene.get_selected_groups()[0]
        g.name.setPlainText(group.get('name', g.name_))
        g.node_obj.obj_id = group['id']

        new_nodes[g] = group

    return new_nodes


def paste_macro(context, undo_stack, data, pos=None):
    # TODO: this function is identical to load_macro except it creates new object id's for the pasted items

    scene = context.get('scene')

    node_map = {}  # map from copied node id to newly created node id
    new_nodes = {}  # hold onto newly created nodes so that we can change the selection to them after paste

    relative_pos = None
    for node in data['nodes']:
        type_ = node['node_obj'].split('.')[-1]

        if pos:
            if not relative_pos:
                relative_pos = QtCore.QPointF(node['position'][0], node['position'][1])
                position = QtCore.QPointF(pos.x(), pos.y())
            else:
                offset_x = node['position'][0] - relative_pos.x()
                offset_y = node['position'][1] - relative_pos.y()
                position = QtCore.QPointF(pos.x() + offset_x, pos.y() + offset_y)
        else:
            position = QtCore.QPointF(*node['position'])

        size = QtCore.QSize(*node.get('size', (100, 100)))

        undo_stack.push(commands.AddNode(context, type_, position=position, size=size))
        n = scene.get_selected_nodes()[0]
        n.node_obj.set_active(node.get('active', True))
        n.name.setPlainText(node.get('name', n.name_))

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

        s_node = scene.get_node_by_id(s_obj_id)
        for o in s_node.outputs:
            if o.type_ == s_plug:
                source_plug = o
                break

        t_node = scene.get_node_by_id(t_obj_id)
        for o in t_node.inputs:
            if o.type_ == t_plug:
                target_plug = o
                break

        if source_plug and target_plug:
            undo_stack.push(commands.ConnectPlugs(context, source_plug, target_plug))

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
        if pos:
            if not relative_pos:
                relative_pos = QtCore.QPointF(group['position'][0], group['position'][1])
                position = QtCore.QPointF(pos.x(), pos.y())
            else:
                offset_x = group['position'][0] - relative_pos.x()
                offset_y = group['position'][1] - relative_pos.y()

                position = QtCore.QPointF(pos.x() + offset_x, pos.y() + offset_y)
        else:
            position = QtCore.QPointF(*group['position'])

        size = QtCore.QSize(*group['size'])

        undo_stack.push(commands.AddGroup(context, position, size))
        g = scene.get_selected_groups()[0]
        g.name.setPlainText(group.get('name', g.name_))

        new_nodes[g] = group

    return new_nodes


def get_scene_data(scene, selection=None):
    data = {'nodes': [], 'edges': [], 'groups': []}

    if selection:
        nodes = sorted([n for n in selection if isinstance(n, pyweritems.PywerNode)],
                       key=lambda n: (n.pos().x(), n.pos().y()))
        groups = sorted([g for g in selection if isinstance(g, pyweritems.PywerGroup)],
                        key=lambda g: (g.pos().x(), g.pos().y()))
    else:
        nodes = scene.get_all_nodes()
        groups = scene.get_all_groups()

    for node in nodes:
        data['nodes'].append(node.to_dict())

    all_ids = [n['id'] for n in data['nodes']]

    # TODO: should do edges and groups like nodes with to_dict()

    for edge in scene.get_all_edges():
        source_id = str(edge.source_plug.parentItem().node_obj.obj_id)
        target_id = str(edge.target_plug.parentItem().node_obj.obj_id)
        if (source_id in all_ids) and (target_id in all_ids):
            edge_info = (str(edge.source_plug.parentItem().node_obj.obj_id) + '.' + edge.source_plug.type_,
                         str(edge.target_plug.parentItem().node_obj.obj_id) + '.' + edge.target_plug.type_)
            data['edges'].append(edge_info)

    for group in groups:
        data['groups'].append(group.to_dict())

    return data


def create_group(scene, position):
    group = scene.create_group()
    group.setPos(position)


def group_selected_nodes(scene):
    scene.group_selected_nodes()


def delete_selected(scene):
    scene.remove_selected_items()


def select_all(scene):
    scene.select_all()


def select(scene, items=None):
    if items is None:
        items = []

    scene.clearSelection()
    for item in items:
        item.setSelected(True)
