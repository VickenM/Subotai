"""Behavioral integration checks for versioned reconstruction and rollback."""
from copy import deepcopy
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6 import QtCore, QtGui, QtWidgets

import appnode
from appscene import AppScene
import commands
import graph_document as graph
import persistence
import register
import scenetools
from subotai import MainWindow


class GraphDocumentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        register.reload_node_registry()

    def setUp(self):
        self.scene = AppScene()
        self.stack = QtGui.QUndoStack()
        self.context = dict(scene=self.scene, worker=self.app.thread(), current_selection=[], scene_data={})

    def tearDown(self):
        self.stack.clear()
        self.scene.clear()

    def node(self, name):
        with persistence.inert_construction():
            node = appnode.new_node(name)
        self.scene.add_node(node)
        return node

    def test_malformed_roots_and_identity_collisions_are_actionable(self):
        for data in (None, [], {'format': 'subotai.graph', 'schema_version': 1, 'nodes': None},
                     {'format': 'subotai.graph', 'schema_version': 1, 'nodes': [{'type': []}]}):
            with self.subTest(data=data), self.assertRaises(persistence.PersistenceError):
                graph.migrate(data)
        self.node('Counter')
        document = graph.snapshot(self.scene)
        with self.assertRaisesRegex(persistence.PersistenceError, 'collide'):
            scenetools.load_macro(self.context, self.stack, document)
        self.assertEqual(self.stack.count(), 0)
        self.assertEqual(graph.snapshot(self.scene), document)

    def assert_round_trip(self):
        original = graph.snapshot(self.scene)
        staged = graph.stage(graph.migrate(json.loads(json.dumps(original))))
        try:
            self.assertEqual(graph.snapshot(staged), original)
        finally:
            staged.clear()

    def test_every_builtin_default_restores_without_running_resources(self):
        for name in register.node_registry:
            with self.subTest(node=name):
                node = self.node(name)
                if hasattr(node.node_obj, 'loop_thread'):
                    self.assertFalse(node.node_obj.loop_thread.is_alive())
                if name == 'Viewer':
                    self.assertFalse(node.node_obj.widget.isVisible())
                self.assert_round_trip()
                self.scene.clear()

    def test_counter_collector_and_nullable_promoted_state(self):
        counter = self.node('Counter')
        counter.node_obj.get_first_param('value')._value = 37
        collector = self.node('Collector')
        collector.node_obj._items = ['first', 'second']
        promoted = self.node('StringParameter')
        promoted.node_obj.get_first_param('promote state')._value = True
        promoted.node_obj.get_first_param('promote name')._value = None
        self.assert_round_trip()
        saved = graph.snapshot(self.scene)
        collector.node_obj._items.append('later')
        item = next(n for n in saved['nodes'] if n['type'] == 'subotai:Collector')
        self.assertEqual(len(item['state']['pending_items']['data']), 2)

    def test_dynamic_ports_restore_before_edges_and_paste_remaps_ids(self):
        source = self.node('StringParameter')
        target = self.node('FormatString')
        target.node_obj.restoring = False
        for _ in range(12):
            self.stack.push(commands.ConnectPlugs(self.context, source.outputs[0], target.inputs[-1]))
        target.inputs[-1].plug_obj._value = 'unused trailing fallback'
        saved = graph.snapshot(self.scene)
        self.assert_round_trip()
        pasted = scenetools.paste_macro(self.context, self.stack, saved, QtCore.QPointF(800, 500))
        self.assertEqual(len(pasted), 2)
        old_ids = {n['id'] for n in saved['nodes']}
        self.assertTrue(old_ids.isdisjoint({str(n.node_obj.obj_id) for n in pasted}))
        self.assertEqual(len(self.scene.get_all_edges()), 24)
        self.stack.undo()
        self.assertEqual(len(self.scene.get_all_edges()), 12)
        self.stack.redo()
        self.assertEqual(len(self.scene.get_all_edges()), 24)
        graph.validate(graph.snapshot(self.scene))

    def test_connected_fallback_is_saved_without_evaluating_upstream(self):
        source = self.node('StringParameter')
        target = self.node('ConsoleWriter')
        source.node_obj.get_first_param('param')._value = 'upstream'
        target.node_obj.get_first_param('message')._value = 'local fallback'
        self.stack.push(commands.ConnectPlugs(self.context, source.outputs[0], target.inputs[-1]))
        self.assertEqual(target.inputs[-1].plug_obj.value, 'upstream')
        saved = graph.snapshot(self.scene)
        record = next(n for n in saved['nodes'] if n['type'] == 'subotai:ConsoleWriter')
        self.assertEqual(next(p for p in record['parameters'] if p['id'] == 'input:message')['value']['data'], 'local fallback')
        self.assert_round_trip()

    def test_invalid_documents_fail_before_node_construction(self):
        self.node('Counter')
        saved = graph.snapshot(self.scene)
        invalid = []
        data = deepcopy(saved); data['nodes'][0]['type'] = 'missing:Node'; invalid.append(data)
        data = deepcopy(saved); data['nodes'].append(deepcopy(data['nodes'][0])); invalid.append(data)
        data = deepcopy(saved); data['nodes'][0]['parameters'].pop(); invalid.append(data)
        data = deepcopy(saved); data['schema_version'] = 99; invalid.append(data)
        data = deepcopy(saved); data['edges'].append({'id': 'broken', 'source': {'node_id': 'missing', 'port_id': 'missing'}, 'target': {'node_id': 'missing', 'port_id': 'missing'}}); invalid.append(data)
        with patch.object(appnode.AppNode, 'from_event_node', side_effect=AssertionError('must not construct')):
            for document in invalid:
                with self.subTest(document=document), self.assertRaises(persistence.PersistenceError):
                    graph.load_into(self.scene, document)
        self.assertEqual(graph.snapshot(self.scene), saved)

    def test_main_window_keeps_document_and_history_on_failed_load(self):
        window = MainWindow()
        try:
            window.create_new_node('Counter')
            before = window.save_data()
            count = window.undo_stack.count()
            invalid = deepcopy(before)
            invalid['nodes'][0]['type'] = 'missing:Node'
            with self.assertRaises(persistence.PersistenceError):
                window.load_data(invalid)
            self.assertEqual(window.save_data(), before)
            self.assertEqual(window.undo_stack.count(), count)
            with patch.object(appnode.AppNode, 'from_event_node', side_effect=RuntimeError('construction failed')):
                with self.assertRaises(persistence.PersistenceError):
                    window.load_data(before)
            self.assertEqual(window.save_data(), before)
        finally:
            window.parameters.set_node_obj(None)
            window.undo_stack.clear()
            window.deactivate_event_nodes()
            window.exit_app()
            window.deleteLater()
            self.app.sendPostedEvents(None, QtCore.QEvent.Type.DeferredDelete)

    def test_busy_node_rejects_snapshot(self):
        node = self.node('Counter')
        node.node_obj._state_busy = 1
        with self.assertRaises(persistence.PersistenceError):
            graph.snapshot(self.scene)
        node.node_obj._state_busy = 0
        self.assert_round_trip()

    def test_empty_clipboard_selection_is_empty(self):
        self.node('Counter')
        self.assertEqual(graph.snapshot(self.scene, [])['nodes'], [])


if __name__ == '__main__':
    unittest.main()
