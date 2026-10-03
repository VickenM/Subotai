"""Versioned graph snapshots, pure migration, validation and staged restoration."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from enum import Enum
import json
from pathlib import Path
import uuid

from jsonschema import Draft202012Validator
from PySide6 import QtCore

import appnode
import register
from eventnodes.params import Param, StringParam, IntParam, FloatParam, BoolParam, ListParam
from eventnodes.signal import Signal
from persistence import PersistenceError, encode_value, decode_value, inert_construction, dumps


SCHEMA = json.loads((Path(__file__).parent / 'docs/persistence/graph-v1.schema.json').read_text(encoding='utf-8'))
VALIDATOR = Draft202012Validator(SCHEMA)


def binding(name, flags):
    """Identify a parameter independently of its editable presentation."""
    return ('input:' if flags & 1 else 'output:' if flags & 2 else 'property:') + name


def registry():
    """Index registered classes, refusing duplicate stable identities."""
    result = {}
    for cls in register.node_registry.values():
        try:
            key = cls.persistence_type_id()
        except AttributeError as error:
            raise PersistenceError('Registered node must declare a namespaced persistence_type: ' + cls.__name__) from error
        if key in result:
            raise PersistenceError('Duplicate registered type ID: ' + key)
        result[key] = cls
    return result


def definitions(cls, names=()):
    """Expand a node's declared dynamic input family without constructing it."""
    result = cls.describe_parameters()
    prefix = cls.dynamic_input_prefix
    if prefix:
        indices = {1}
        for key in names:
            if key.startswith('input:' + prefix):
                suffix = key[len('input:' + prefix):]
                if not suffix.isdecimal() or int(suffix) < 1 or str(int(suffix)) != suffix:
                    raise PersistenceError('Invalid dynamic input binding')
                indices.add(int(suffix))
        if max(indices) > 10000:
            raise PersistenceError('Dynamic port limit exceeded')
        for index in range(1, max(indices) + 1):
            name = prefix + str(index)
            original = result['input:' + prefix + '1']
            result['input:' + name] = replace(original, options={**original.options, 'name': name})
    return result


def declared_ports(cls, specs):
    """Describe event and value ports from node-owned declarations."""
    ports = []
    for key, (name, flags) in cls.signal_definitions.items():
        direction = 'input' if flags & 1 else 'output'
        ports.append(dict(id='event:' + key, name=name, direction=direction, kind='event', binding=name))
    for key, spec in specs.items():
        for flag, direction in ((1, 'input'), (2, 'output')):
            if spec.options['pluggable'] & flag:
                name = spec.options['name']
                ports.append(dict(id='value:' + direction + ':' + name, name=name,
                                  direction=direction, kind='value', binding=key))
    return ports


def local_value(param):
    """Read backing values only, never connected or computed getters."""
    value = param._value
    if isinstance(param, ListParam):
        return [local_value(item) if isinstance(item, Param) else deepcopy(item) for item in value]
    return value


def decode_parameter(record, spec):
    """Validate a stored value against its declared parameter type."""
    prototype = spec.create(None)
    value = decode_value(record, enum=getattr(prototype, 'enum', None))
    if value is None:
        if prototype._value is not None:
            raise PersistenceError('Null is not permitted for this binding')
    elif prototype.type is Enum:
        if not isinstance(value, prototype.enum):
            raise PersistenceError('Expected declared enum type')
    elif type(value) is not prototype.type:
        raise PersistenceError('Parameter value type does not match declaration')
    if type(value) in (int, float) and hasattr(prototype, 'minimum'):
        if not prototype.minimum <= value <= prototype.maximum:
            raise PersistenceError('Parameter value is outside declared bounds')
    return value


def parameter_record(key, spec, value):
    return dict(id=key, name=spec.options['name'], flags=spec.options['pluggable'], value=encode_value(value))


def snapshot(scene, selection=None):
    """Capture persistent state, preserving local fallbacks and edge identities."""
    locked = []
    try:
        for node in scene.get_all_nodes():
            obj = node.node_obj
            if not obj._state_lock.acquire(blocking=False):
                raise PersistenceError('Graph is busy; save again after computation finishes')
            locked.append(obj)
            if obj._state_busy:
                raise PersistenceError('Graph is busy; save again after computation finishes')
        return _snapshot(scene, selection)
    finally:
        for obj in reversed(locked):
            obj._state_lock.release()


def _snapshot(scene, selection=None):
    nodes = scene.get_all_nodes() if selection is None else [n for n in selection if n in scene.get_all_nodes()]
    groups = scene.get_all_groups() if selection is None else [g for g in selection if g in scene.get_all_groups()]
    result = dict(format='subotai.graph', schema_version=1, nodes=[], edges=[], groups=[])
    for node in sorted(nodes, key=lambda n: str(n.node_obj.obj_id)):
        obj = node.node_obj
        params = {binding(p.name, p.pluggable): p for p in obj.params}
        specs = definitions(type(obj), params)
        if set(params) != set(specs):
            raise PersistenceError('Undeclared parameter on node ' + str(obj.obj_id))
        parameters = [parameter_record(key, spec, local_value(params[key]))
                      for key, spec in sorted(specs.items()) if spec.storage == 'stored']
        ports = []
        for direction, plugs in (('input', node.inputs), ('output', node.outputs)):
            for plug in plugs:
                kind = 'event' if isinstance(plug.plug_obj, Signal) else 'value'
                key = plug.type_ if kind == 'event' else binding(plug.plug_obj.name, plug.plug_obj.pluggable)
                ports.append(dict(id=kind + ':' + direction + ':' + plug.type_, name=plug.type_,
                                  direction=direction, kind=kind, binding=key))
        raw_state = obj.save_state()
        if set(raw_state) != set(obj.state_fields):
            raise PersistenceError('Custom state hook returned undeclared fields')
        result['nodes'].append(dict(id=str(obj.obj_id), type=obj.persistence_type_id(),
            type_version=obj.type_version, name=node.name.toPlainText(), enabled=obj.active,
            position=[node.x(), node.y()], size=list(node.size()), parameters=parameters,
            ports=ports, state={key: encode_value(value) for key, value in raw_state.items()}))
    ids = {n['id'] for n in result['nodes']}
    for edge in sorted(scene.get_all_edges(), key=lambda e: e.persistence_order):
        if not edge.source_plug or not edge.target_plug:
            continue
        ends = []
        for direction, plug in (('output', edge.source_plug), ('input', edge.target_plug)):
            kind = 'event' if isinstance(plug.plug_obj, Signal) else 'value'
            ends.append(dict(node_id=str(plug.parentItem().node_obj.obj_id), port_id=kind + ':' + direction + ':' + plug.type_))
        if all(end['node_id'] in ids for end in ends):
            result['edges'].append(dict(id=edge.persistence_id, source=ends[0], target=ends[1]))
    for group in sorted(groups, key=lambda g: str(g.node_obj.obj_id)):
        result['groups'].append(dict(id=str(group.node_obj.obj_id), name=group.name.toPlainText(),
                                    position=[group.x(), group.y()], size=list(group.size())))
    validate(result)
    return result


def validate(document):
    """Validate shape, identities, declarations, endpoints and value dependencies."""
    pending = [(document, 0)]
    while pending:
        value, depth = pending.pop()
        if depth > 128:
            raise PersistenceError('Document exceeds maximum nesting depth (128)')
        if type(value) is dict:
            pending.extend((item, depth + 1) for item in value.values())
        elif type(value) is list:
            pending.extend((item, depth + 1) for item in value)
    if len(dumps(document).encode('utf-8')) > 32 * 1024 * 1024:
        raise PersistenceError('Document exceeds the 32 MiB limit')
    error = next(VALIDATOR.iter_errors(document), None)
    if error:
        raise PersistenceError('Invalid document at /' + '/'.join(map(str, error.absolute_path)) + ' (' + error.validator + ')')
    classes = registry()
    all_ids, nodes, port_maps = set(), {}, {}
    for item in document['nodes'] + document['groups'] + document['edges']:
        if item['id'] in all_ids:
            raise PersistenceError('Duplicate document ID: ' + item['id'])
        all_ids.add(item['id'])
    for record in document['nodes']:
        cls = classes.get(record['type'])
        if cls is None:
            raise PersistenceError('Unavailable node type: ' + record['type'])
        if record['type_version'] != cls.type_version:
            raise PersistenceError('Unsupported node version: ' + record['type'])
        specs = definitions(cls, [p['id'] for p in record['parameters']])
        expected = {key for key, spec in specs.items() if spec.storage == 'stored'}
        params = record['parameters']
        if len({p['id'] for p in params}) != len(params) or {p['id'] for p in params} != expected:
            raise PersistenceError('Missing, duplicate or unknown parameters on ' + record['id'])
        for param in params:
            spec = specs[param['id']]
            if param['name'] != spec.options['name'] or param['flags'] != spec.options['pluggable']:
                raise PersistenceError('Parameter declaration mismatch on ' + record['id'])
            try:
                decode_parameter(param['value'], spec)
            except PersistenceError as exc:
                raise PersistenceError(record['id'] + '/' + param['id'] + ': ' + str(exc)) from None
        ports = {p['id']: p for p in record['ports']}
        expected_ports = {p['id']: p for p in declared_ports(cls, specs)}
        if len(ports) != len(record['ports']) or ports != expected_ports:
            raise PersistenceError('Port declaration mismatch on ' + record['id'])
        if set(record['state']) != set(cls.state_fields):
            raise PersistenceError('State declaration mismatch on ' + record['id'])
        for key, value in record['state'].items():
            decoded = decode_value(value)
            if type(decoded) is not type(cls.state_fields[key].default):
                raise PersistenceError('State value type mismatch on ' + record['id'])
        nodes[record['id']] = (record, specs)
        port_maps[record['id']] = ports
    occupied, pairs = set(), set()
    dependencies = {key: set() for key in nodes}
    for edge in document['edges']:
        source, target = edge['source'], edge['target']
        try:
            sp = port_maps[source['node_id']][source['port_id']]
            tp = port_maps[target['node_id']][target['port_id']]
        except KeyError:
            raise PersistenceError('Missing endpoint on edge ' + edge['id']) from None
        pair = (source['node_id'], source['port_id'], target['node_id'], target['port_id'])
        if pair in pairs or source['node_id'] == target['node_id']:
            raise PersistenceError('Duplicate or same-node edge ' + edge['id'])
        pairs.add(pair)
        if sp['direction'] != 'output' or tp['direction'] != 'input' or sp['kind'] != tp['kind']:
            raise PersistenceError('Incompatible endpoint direction/kind on ' + edge['id'])
        if sp['kind'] == 'value':
            endpoint = (target['node_id'], target['port_id'])
            if endpoint in occupied:
                raise PersistenceError('Multiple incoming value edges')
            occupied.add(endpoint)
            ss = nodes[source['node_id']][1][sp['binding']]
            ts = nodes[target['node_id']][1][tp['binding']]
            # Parameter subclasses share their root value class even for lazy outputs.
            roots = (StringParam, IntParam, FloatParam, BoolParam, ListParam)
            def family(factory):
                return next((base for base in roots if issubclass(factory, base)), factory)
            if family(ss.factory) != family(ts.factory):
                raise PersistenceError('Incompatible value types on ' + edge['id'])
            # Only lazy derived outputs recurse through their source inputs.
            if ss.storage == 'derived':
                dependencies[target['node_id']].add(source['node_id'])
    visiting, visited = set(), set()
    def visit(key):
        if key in visiting:
            raise PersistenceError('Recursive value dependency cycle')
        if key not in visited:
            visiting.add(key)
            for parent in dependencies[key]:
                visit(parent)
            visiting.remove(key)
            visited.add(key)
    for key in nodes:
        visit(key)
    return document


def migrate(data):
    """Convert a detached legacy record using class-owned defaults and aliases."""
    if type(data) is not dict:
        raise PersistenceError('Graph document must be an object')
    data = deepcopy(data)
    if 'schema_version' in data or 'format' in data:
        if data.get('format') != 'subotai.graph' or type(data.get('schema_version')) is not int or data['schema_version'] != 1:
            raise PersistenceError('Unsupported graph format/version; upgrade Subotai')
        classes = registry()
        if type(data.get('nodes')) is not list:
            raise PersistenceError('Graph nodes must be an array')
        for record in data.get('nodes', []):
            if type(record) is not dict:
                raise PersistenceError('Malformed node record')
            if type(record.get('type')) is not str:
                raise PersistenceError('Node type must be a string')
            cls = classes.get(record.get('type'))
            if cls is None:
                continue  # Full validation supplies the missing-dependency error.
            version = record.get('type_version')
            if type(version) is not int:
                raise PersistenceError('Node version must be an integer')
            while version < cls.type_version:
                transform = cls.type_migrations.get(version)
                if transform is None:
                    raise PersistenceError('Missing node migration for ' + record['type'])
                updated = transform(deepcopy(record))
                if type(updated) is not dict or updated.get('type_version') != version + 1 or updated.get('id') != record.get('id') or updated.get('type') != record.get('type'):
                    raise PersistenceError('Invalid node migration result')
                record.clear()
                record.update(updated)
                version += 1
        return validate(data)
    if set(data) != {'nodes', 'edges', 'groups'} or any(type(data[key]) is not list for key in data):
        raise PersistenceError('Unrecognized legacy document')
    aliases = {}
    for cls in registry().values():
        for alias in (cls.__module__ + '.' + cls.type, *getattr(cls, 'legacy_aliases', ())):
            if alias in aliases:
                raise PersistenceError('Ambiguous legacy node alias')
            aliases[alias] = cls
    result = dict(format='subotai.graph', schema_version=1, nodes=[], edges=[], groups=[])
    try:
        for old in data['nodes']:
            cls = aliases.get(old['node_obj'])
            if cls is None:
                raise PersistenceError('Unavailable legacy type: ' + old['node_obj'])
            raw = {}
            for flags, entries in old.get('params', {}).items():
                flag = int(flags)
                if not 0 <= flag <= 7:
                    raise PersistenceError('Invalid legacy parameter flags')
                for name, value in entries.items():
                    key = binding(name, flag)
                    if key in raw:
                        raise PersistenceError('Duplicate legacy parameter binding')
                    raw[key] = (flag, value)
            extra = list(raw)
            if cls.dynamic_input_prefix:
                for source, target in data['edges']:
                    node_id, name = target.split('.', 1)
                    if node_id == old['id'] and name.startswith(cls.dynamic_input_prefix):
                        index = int(name[len(cls.dynamic_input_prefix):])
                        extra.extend(['input:' + name, 'input:' + cls.dynamic_input_prefix + str(index + 1)])
            specs = definitions(cls, extra)
            if set(raw) - set(specs):
                raise PersistenceError('Unknown legacy parameter on ' + old['id'])
            params = []
            for key, spec in sorted(specs.items()):
                if key in raw and raw[key][0] != spec.options['pluggable']:
                    raise PersistenceError('Legacy flag mismatch on ' + old['id'])
                if spec.storage != 'stored':
                    continue
                prototype = spec.create(None)
                value = raw[key][1] if key in raw else local_value(prototype)
                if isinstance(prototype._value, Enum) and not isinstance(value, Enum):
                    value = prototype.enum(value)
                params.append(parameter_record(key, spec, value))
            result['nodes'].append(dict(id=old['id'], type=cls.persistence_type_id(), type_version=cls.type_version,
                name=old.get('name', 'name'), enabled=old.get('active', True), position=old['position'],
                size=old.get('size', [100, 100]), parameters=params, ports=declared_ports(cls, specs),
                state={key: encode_value(field.default) for key, field in cls.state_fields.items()}))
        port_maps = {n['id']: n['ports'] for n in result['nodes']}
        used = {n['id'] for n in result['nodes']} | {g['id'] for g in data['groups'] if 'id' in g}
        def fresh(label):
            candidate = str(uuid.uuid5(uuid.NAMESPACE_URL, 'subotai:legacy:' + label))
            while candidate in used:
                candidate = str(uuid.uuid5(uuid.NAMESPACE_URL, candidate))
            used.add(candidate)
            return candidate
        for index, pair in enumerate(data['edges']):
            ends = []
            if len(pair) != 2:
                raise PersistenceError('Malformed legacy edge')
            for direction, endpoint in zip(('output', 'input'), pair):
                node_id, name = endpoint.split('.', 1)
                choices = [p for p in port_maps[node_id] if p['name'] == name and p['direction'] == direction]
                if len(choices) != 1:
                    raise PersistenceError('Ambiguous or missing legacy endpoint')
                ends.append(dict(node_id=node_id, port_id=choices[0]['id']))
            result['edges'].append(dict(id=fresh('edge:' + str(index)), source=ends[0], target=ends[1]))
        for index, old in enumerate(data['groups']):
            result['groups'].append(dict(id=old['id'] if 'id' in old else fresh('group:' + str(index)),
                name=old.get('name', 'name'), position=old['position'], size=old['size']))
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        if isinstance(exc, PersistenceError):
            raise
        raise PersistenceError('Malformed or unsupported legacy graph record') from None
    return validate(result)


def wrapped_list(values):
    """Recreate list item parameter wrappers without coercing all items to strings."""
    factories = {str: StringParam, int: IntParam, float: FloatParam, bool: BoolParam, list: ListParam}
    result = []
    for value in values:
        if type(value) is list:
            value = wrapped_list(value)
            factory = ListParam
        else:
            factory = factories.get(type(value), Param)
        result.append(factory(name='', value=value))
    return result


def stage(document):
    """Build an inactive scene; any failure disposes staging and escapes safely."""
    validate(document)
    from appscene import AppScene
    scene = AppScene()
    classes = registry()
    try:
        with inert_construction():
            for record in document['nodes']:
                cls = classes[record['type']]
                node = appnode.AppNode.from_event_node(cls())
                scene.add_node(node)
                obj = node.node_obj
                obj.obj_id = record['id']
                obj.active = record['enabled']
                specs = definitions(cls, [p['id'] for p in record['parameters']])
                params = {binding(p.name, p.pluggable): p for p in obj.params}
                for key, spec in specs.items():
                    if key not in params:
                        param = spec.create(obj)
                        obj.params.append(param)
                        obj.string_params.append(param)
                        node.add_input(appnode.Plug.from_param(param))
                        params[key] = param
                for item in record['parameters']:
                    value = decode_parameter(item['value'], specs[item['id']])
                    params[item['id']]._value = wrapped_list(value) if type(value) is list else value
                obj.restore_state({key: decode_value(value) for key, value in record['state'].items()})
                node.name.setPlainText(record['name'])
                node.setPos(*record['position'])
                node.setSize(*record['size'])
                for direction, attr in (('input', 'inputs'), ('output', 'outputs')):
                    plugs = getattr(node, attr)
                    def port_id(plug):
                        return ('event' if isinstance(plug.plug_obj, Signal) else 'value') + ':' + direction + ':' + plug.type_
                    lookup = {port_id(p): p for p in plugs}
                    plugs[:] = [lookup[p['id']] for p in record['ports'] if p['direction'] == direction]
                node.adjust()
            nodes = {str(n.node_obj.obj_id): n for n in scene.get_all_nodes()}
            from pywerlines.pyweritems import PywerEdge
            for record in document['edges']:
                ends = []
                for key, direction in (('source', 'output'), ('target', 'input')):
                    endpoint = record[key]
                    node = nodes[endpoint['node_id']]
                    plugs = node.outputs if direction == 'output' else node.inputs
                    ends.append(next(p for p in plugs if ('event' if isinstance(p.plug_obj, Signal) else 'value') + ':' + direction + ':' + p.type_ == endpoint['port_id']))
                edge = PywerEdge()
                edge.persistence_id = record['id']
                scene.addItem(edge)
                edge.connect_plugs(*ends)
                appnode.connect_plugs(*ends)
            for record in document['groups']:
                group = appnode.new_group()
                scene.add_group(group)
                group.node_obj.obj_id = record['id']
                group.name.setPlainText(record['name'])
                group.setPos(*record['position'])
                group.setSize(*record['size'])
        return scene
    except Exception as error:
        try:
            scene.clear()
        except Exception:
            pass
        if isinstance(error, PersistenceError):
            raise
        raise PersistenceError('Unable to reconstruct graph; check the installed node implementations') from error


def activate(scene, nodes=None):
    """Apply saved activation after commit; return resource errors without rollback."""
    return activate_nodes(scene.get_all_nodes() if nodes is None else nodes)


def activate_nodes(nodes):
    """Activate only the newly installed subset, leaving existing sources alone."""
    errors = []
    for node in nodes:
        obj = node.node_obj
        intended = obj.active
        obj.restoring = False
        try:
            obj.sync_restored_controls()
            obj.activate_resources()
            obj.set_active(intended)
        except Exception:
            errors.append('Activation failed for node ' + str(obj.obj_id))
            try:
                obj.terminate()
            except Exception:
                pass
            obj.active = intended
    return errors


def install(scene, staged):
    """Transfer already reconstructed items into the destination scene."""
    roots = [item for item in staged.items() if item.parentItem() is None]
    for item in roots:
        staged.removeItem(item)
        scene.addItem(item)


def load_into(scene, data, *, activate_nodes=True):
    """Append a validated graph without mutating the destination on load failure."""
    document = migrate(data)
    check_collisions(scene, document)
    staged = stage(document)
    new_nodes = staged.get_all_nodes()
    install(scene, staged)
    if activate_nodes:
        return activate(scene, new_nodes)
    return []


def check_collisions(scene, document):
    """Reject insertion identities already owned by the destination scene."""
    existing = {str(item.node_obj.obj_id) for item in scene.get_all_nodes() + scene.get_all_groups()}
    existing.update(edge.persistence_id for edge in scene.get_all_edges())
    incoming = {item['id'] for key in ('nodes', 'groups', 'edges') for item in document[key]}
    if existing & incoming:
        raise PersistenceError('Loaded graph IDs collide with the current scene')
