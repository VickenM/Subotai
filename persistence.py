"""Shared typed state codecs and strict, atomic JSON document I/O.

Node declarations and graph reconstruction are layered on these primitives;
this module never evaluates node getters or executes a workflow.
"""
from __future__ import annotations

from copy import deepcopy
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from enum import Enum
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Any, Callable


class PersistenceError(ValueError):
    """An invalid or unsupported document, without disclosing its payload."""


@dataclass(frozen=True)
class StateField:
    """A node-owned declaration for an extra persistent attribute."""

    attribute: str
    default: Any


@dataclass(frozen=True)
class ParameterDefinition:
    """Node-owned parameter constructor metadata and persistence policy.

    Stored parameters are constructed from these same options, so documentation,
    defaults and runtime construction do not maintain separate copies.
    """

    factory: type
    options: dict[str, Any]
    storage: str = 'stored'
    bind_node: bool = False

    def create(self, node: Any) -> Any:
        """Create a fresh parameter, detaching mutable constructor defaults."""
        options = deepcopy(self.options)
        if self.bind_node:
            options['node'] = node
        return self.factory(**options)


@dataclass(frozen=True)
class ValueCodec:
    """A versioned, explicitly registered custom value conversion."""

    version: int
    accepts: Callable[[Any], bool]
    encode: Callable[[Any], Any]
    decode: Callable[[Any], Any]


_codecs: dict[str, ValueCodec] = {}
_constructing = ContextVar('subotai_inert_construction', default=False)


@contextmanager
def inert_construction():
    """Mark node construction as staging, without starting runtime resources."""
    token = _constructing.set(True)
    try:
        yield
    finally:
        _constructing.reset(token)


def is_restoring() -> bool:
    """Whether the caller is constructing an inactive staging node."""
    return _constructing.get()


def register_codec(name: str, codec: ValueCodec) -> None:
    """Register a namespaced codec; reject accidental replacement."""
    if ':' not in name or not name.split(':', 1)[0] or name in _codecs:
        raise PersistenceError('Codec requires a unique namespaced ID')
    if type(codec.version) is not int or codec.version < 1:
        raise PersistenceError('Codec version must be a positive integer')
    _codecs[name] = codec


def encode_value(value: Any) -> dict[str, Any]:
    """Detach a logical value into a typed JSON envelope, preserving null."""
    if value is None:
        return {'codec': 'null', 'data': None}
    if isinstance(value, Enum):
        return {'codec': 'enum', 'data': value.name}
    primitive = {bool: 'bool', int: 'int', float: 'float', str: 'string'}
    if type(value) in primitive:
        if type(value) is float and not math.isfinite(value):
            raise PersistenceError('Nonfinite numbers cannot be saved')
        return {'codec': primitive[type(value)], 'data': value}
    if type(value) is list:
        return {'codec': 'list', 'data': [encode_value(item) for item in value]}
    if type(value) is dict and all(type(key) is str for key in value):
        return {'codec': 'object', 'data': {key: encode_value(item) for key, item in value.items()}}
    for name, codec in _codecs.items():
        if codec.accepts(value):
            try:
                data = json.loads(json.dumps(codec.encode(value), allow_nan=False))
            except Exception:
                raise PersistenceError('Custom codec failed to encode: ' + name) from None
            return {'codec': name, 'version': codec.version, 'data': data}
    raise PersistenceError('Unsupported persistent value type: ' + type(value).__name__)


def decode_value(record: dict[str, Any], *, enum: type[Enum] | None = None) -> Any:
    """Validate and decode an envelope; custom decoders are opt-in only."""
    if type(record) is not dict or 'codec' not in record or 'data' not in record:
        raise PersistenceError('Expected a typed value envelope')
    name, data = record['codec'], record['data']
    if type(name) is not str:
        raise PersistenceError('Codec ID must be a string')
    expected_keys = {'codec', 'data', 'version'} if name in _codecs else {'codec', 'data'}
    if set(record) != expected_keys:
        raise PersistenceError('Unexpected or missing value fields')
    primitive = {'null': type(None), 'bool': bool, 'int': int, 'float': float, 'string': str}
    if name in primitive:
        if name == 'float' and type(data) in (int, float):
            try:
                value = float(data)
            except OverflowError:
                raise PersistenceError('Float is outside the supported range') from None
            if math.isfinite(value):
                return value
        elif type(data) is primitive[name]:
            return data
        raise PersistenceError('Value does not match codec ' + name)
    if name == 'enum':
        if enum is None or type(data) is not str or data not in enum.__members__:
            raise PersistenceError('Unknown enum member or missing enum declaration')
        return enum[data]
    if name == 'list' and type(data) is list:
        return [decode_value(item, enum=enum) for item in data]
    if name == 'object' and type(data) is dict:
        return {key: decode_value(item, enum=enum) for key, item in data.items()}
    if name in _codecs:
        codec = _codecs[name]
        if type(record['version']) is not int or record['version'] != codec.version:
            raise PersistenceError('Unsupported custom codec version: ' + name)
        try:
            return codec.decode(deepcopy(data))
        except Exception:
            raise PersistenceError('Custom codec failed to decode: ' + name) from None
    raise PersistenceError('Unsupported codec or malformed collection: ' + name)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise PersistenceError('Duplicate JSON object key')
        result[key] = value
    return result


def loads(text: str) -> dict[str, Any]:
    """Parse strict JSON without accepting duplicate keys or nonfinite numbers."""
    if len(text.encode('utf-8')) > 32 * 1024 * 1024:
        raise PersistenceError('Document exceeds the 32 MiB limit')
    def invalid_constant(_value: str) -> None:
        raise PersistenceError('Nonfinite JSON number')
    def finite_float(value: str) -> float:
        result = float(value)
        if not math.isfinite(result):
            raise PersistenceError('Nonfinite JSON number')
        return result
    try:
        data = json.loads(text, object_pairs_hook=_unique_object, parse_constant=invalid_constant,
                          parse_float=finite_float)
    except (json.JSONDecodeError, RecursionError):
        raise PersistenceError('Invalid JSON document') from None
    if type(data) is not dict:
        raise PersistenceError('Document root must be an object')
    return data


def dumps(document: dict[str, Any]) -> str:
    """Encode a detached document as readable UTF-8-compatible strict JSON."""
    try:
        return json.dumps(document, ensure_ascii=False, allow_nan=False, indent=2) + '\n'
    except (ValueError, TypeError, RecursionError):
        raise PersistenceError('Document contains unsupported JSON values') from None


def read_document(path: str | Path) -> dict[str, Any]:
    """Read a bounded UTF-8 JSON document without constructing nodes."""
    with open(path, 'rb') as stream:
        raw = stream.read(32 * 1024 * 1024 + 1)
    if len(raw) > 32 * 1024 * 1024:
        raise PersistenceError('Document exceeds the 32 MiB limit')
    try:
        return loads(raw.decode('utf-8-sig'))
    except UnicodeError:
        raise PersistenceError('Document is not UTF-8') from None


def write_document(path: str | Path, document: dict[str, Any]) -> None:
    """Replace a file only after complete serialization and flushed sibling I/O."""
    payload = dumps(document)
    destination = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='\n',
                                         dir=destination.parent, delete=False,
                                         prefix='.' + destination.name + '.', suffix='.tmp') as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
