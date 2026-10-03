"""Validate the proposed document contract, not the application's legacy loader."""
import ast
import copy
import json
from pathlib import Path
import re
import unittest

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs' / 'persistence'


class PersistenceSpecificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((DOCS / 'graph-v1.schema.json').read_text(encoding='utf-8'))
        cls.example = json.loads((DOCS / 'example-v1.json').read_text(encoding='utf-8'))
        cls.validator = Draft202012Validator(cls.schema)

    def test_schema_and_example(self):
        Draft202012Validator.check_schema(self.schema)
        self.validator.validate(self.example)
        # Check fixture references as well as structural validity. The schema
        # intentionally cannot establish cross-record referential integrity.
        nodes = {node['id']: node for node in self.example['nodes']}
        for edge in self.example['edges']:
            for end, direction in (('source', 'output'), ('target', 'input')):
                endpoint = edge[end]
                ports = {port['id']: port for port in nodes[endpoint['node_id']]['ports']}
                self.assertEqual(ports[endpoint['port_id']]['direction'], direction)

    def test_typed_values_include_null_enum_nested_lists_and_custom_codec(self):
        data = copy.deepcopy(self.example)
        data['nodes'][0]['state'] = {
            'null': {'codec': 'null', 'data': None},
            'enum': {'codec': 'enum', 'data': 'add'},
            'list': {'codec': 'list', 'data': [
                {'codec': 'string', 'data': 'Unicode: \u00e9\u65e5'},
                {'codec': 'int', 'data': 12},
                {'codec': 'float', 'data': 12.0},
                {'codec': 'bool', 'data': False},
                {'codec': 'object', 'data': {'nested': {'codec': 'null', 'data': None}}}]},
            'custom': {'codec': 'example:asset', 'version': 1, 'data': {'path': 'images/input.png'}},
        }
        self.validator.validate(data)
        self.assertEqual(json.loads(json.dumps(data, allow_nan=False)), data)

    def test_rejects_invalid_value_envelopes(self):
        invalid = [
            {'codec': 'int', 'data': True},
            {'codec': 'int', 'data': 1.5},
            {'codec': 'float', 'data': '1.5'},
            {'codec': 'bool', 'data': 1},
            {'codec': 'null', 'data': ''},
            {'codec': 'enum', 'data': 1},
            {'codec': 'list', 'data': ['untyped item']},
            {'codec': 'object', 'data': {'x': 1}},
            {'codec': 'unknown', 'data': 1},
            {'codec': 'example:custom', 'data': {}},
            {'codec': 'example:custom', 'version': 0, 'data': {}},
        ]
        for value in invalid:
            with self.subTest(value=value):
                data = copy.deepcopy(self.example)
                data['nodes'][0]['parameters'][0]['value'] = value
                self.assertFalse(self.validator.is_valid(data))

    def test_rejects_malformed_documents(self):
        invalid = []
        for field in self.example:
            data = copy.deepcopy(self.example)
            del data[field]
            invalid.append(data)
        for field, value in [('schema_version', 2), ('format', 'other'), ('unknown', True)]:
            data = copy.deepcopy(self.example)
            data[field] = value
            invalid.append(data)
        for field, value in [('id', ''), ('type', 'Counter'), ('size', [0, 10]),
                             ('position', [1]), ('type_version', 0)]:
            data = copy.deepcopy(self.example)
            data['nodes'][0][field] = value
            invalid.append(data)
        data = copy.deepcopy(self.example)
        del data['nodes'][0]['parameters'][0]['value']
        invalid.append(data)
        data = copy.deepcopy(self.example)
        data['edges'][0]['source'] = 'counter-1.event'
        invalid.append(data)
        for index, data in enumerate(invalid):
            with self.subTest(case=index):
                self.assertFalse(self.validator.is_valid(data))

    def test_inventory_covers_every_builtin_type_without_running_nodes(self):
        types = set()
        for path in (ROOT / 'eventnodes').rglob('*.py'):
            for cls in ast.parse(path.read_text(encoding='utf-8')).body:
                if not isinstance(cls, ast.ClassDef):
                    continue
                for statement in cls.body:
                    if isinstance(statement, ast.Assign) and any(
                            isinstance(t, ast.Name) and t.id == 'type' for t in statement.targets):
                        if isinstance(statement.value, ast.Constant) and isinstance(statement.value.value, str):
                            types.add(statement.value.value)
        inventory = (DOCS / 'builtin-inventory.md').read_text(encoding='utf-8')
        self.assertEqual(set(re.findall(r'^## (.+)$', inventory, re.MULTILINE)), types)
        self.assertEqual(len(types), 44)
        contract = (DOCS / 'contract.md').read_text(encoding='utf-8')
        for type_ in types:
            self.assertIn(type_, contract, f'Missing state policy for {type_}')

    def test_documentation_local_links_resolve(self):
        for path in DOCS.glob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
                if target.startswith('https://'):
                    continue
                self.assertTrue((path.parent / target.split('#')[0]).exists(), (path, target))


if __name__ == '__main__':
    unittest.main()
