"""Regression checks for strict value codecs and destination preservation."""
from enum import Enum
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import persistence


class PersistenceIOTests(unittest.TestCase):
    def test_nested_values_preserve_types_and_detach(self):
        original = [None, True, 1, 1.0, 'caf\u00e9', {'nested': [False, 2]}]
        encoded = persistence.encode_value(original)
        original[-1]['nested'].append(3)
        restored = persistence.decode_value(encoded)
        self.assertEqual(restored, [None, True, 1, 1.0, 'caf\u00e9', {'nested': [False, 2]}])
        self.assertIs(type(restored[1]), bool)
        self.assertIs(type(restored[2]), int)
        self.assertIs(type(restored[3]), float)

    def test_enum_requires_declared_members(self):
        class Operation(Enum):
            add = 5
        value = persistence.encode_value(Operation.add)
        self.assertEqual(value, {'codec': 'enum', 'data': 'add'})
        self.assertIs(persistence.decode_value(value, enum=Operation), Operation.add)
        with self.assertRaises(persistence.PersistenceError):
            persistence.decode_value(value)

    def test_invalid_values_are_not_coerced_or_stringified(self):
        for value in [object(), float('nan'), float('inf'), {1: 'bad'}]:
            with self.subTest(type=type(value)), self.assertRaises(persistence.PersistenceError):
                persistence.encode_value(value)
        for value in [{'codec': 'int', 'data': True}, {'codec': 'bool', 'data': 1},
                      {'codec': 'float', 'data': float('nan')},
                      {'codec': 'string', 'data': None}, {'codec': 'unknown', 'data': 1}]:
            with self.subTest(value=value), self.assertRaises(persistence.PersistenceError):
                persistence.decode_value(value)

    def test_strict_parser_rejects_duplicates_and_nonfinite_values(self):
        for text in ['{"a":1,"a":2}', '{"a": NaN}', '{"a": Infinity}',
                     '{"a":1e999}', '[]', '{']:
            with self.subTest(text=text), self.assertRaises(persistence.PersistenceError):
                persistence.loads(text)

    def test_failed_serialization_preserves_existing_file(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            path = Path(directory) / 'graph.json'
            path.write_bytes(b'original')
            with self.assertRaises(persistence.PersistenceError):
                persistence.write_document(path, {'unsupported': object()})
            self.assertEqual(path.read_bytes(), b'original')
            self.assertEqual(list(Path(directory).iterdir()), [path])

    def test_failed_replace_preserves_file_and_cleans_temporary(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            path = Path(directory) / 'graph.json'
            path.write_bytes(b'original')
            with patch('persistence.os.replace', side_effect=OSError('simulated failure')):
                with self.assertRaises(OSError):
                    persistence.write_document(path, {'nodes': []})
            self.assertEqual(path.read_bytes(), b'original')
            self.assertEqual(list(Path(directory).iterdir()), [path])

    def test_successful_write_is_utf8_and_readable(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            path = Path(directory) / 'graph.json'
            data = {'name': 'caf\u00e9', 'nested': [None, False, 1.5]}
            persistence.write_document(path, data)
            self.assertEqual(persistence.read_document(path), data)
            self.assertIn('caf\u00e9'.encode('utf-8'), path.read_bytes())
