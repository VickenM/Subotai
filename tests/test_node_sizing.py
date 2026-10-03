"""Content containment and size restoration contracts for graphics nodes."""
import json
import os
import unittest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6 import QtCore, QtGui, QtWidgets

import appnode
from appscene import AppScene
import commands
from eventnodes.base import BaseNode
from pywerlines.pyweritems import PywerNode, PywerPlug
import register
import scenetools


class NodeSizingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        register.reload_node_registry()

    def setUp(self):
        self.scene = AppScene()
        self.stack = QtGui.QUndoStack()
        self.context = dict(scene=self.scene, worker=self.app.thread(),
                            current_selection=[], scene_data={'nodes': [], 'edges': [], 'groups': []})

    def tearDown(self):
        self.stack.clear()
        self.scene.clear()

    def node(self, type_='Counter'):
        node = appnode.new_node(type_)
        self.scene.add_node(node)
        return node

    def assert_content_fits(self, node):
        body = QtCore.QRectF(0, 0, *node.size())
        for plug in node.inputs + node.outputs:
            self.assertTrue(body.contains(plug.mapRectToParent(plug.boundingRect())))
        labels = node._label_rects
        for plug, rect in labels:
            self.assertTrue(body.contains(rect), (plug.type_, rect, body))
            metrics = QtGui.QFontMetricsF(node.content_font)
            self.assertGreaterEqual(rect.width(), metrics.horizontalAdvance(plug.type_))
        for i, (_, rect) in enumerate(labels):
            for _, other in labels[i + 1:]:
                self.assertFalse(rect.intersects(other), (rect, other))
        self.assertLessEqual(node.name.boundingRect().width(), node.width)
        self.assertTrue(body.contains(node.spinner.mapRectToParent(node.spinner.boundingRect())))

    def test_direct_and_interactive_resize_fit_asymmetric_long_labels(self):
        node = self.node()
        for i in range(7):
            node.add_input(PywerPlug(type='long input label ' + str(i), path=PywerPlug.CUBES))
        node.add_output(PywerPlug(type='a very long output label'))
        node.name.setPlainText('A long editable node caption')
        node.setSize(1, 1)
        self.assert_content_fits(node)
        minimum = node.size()
        node.setSize(node.width + 100, node.height + 100)
        node.resizer.setSelected(True)
        node.resizer.setPos(-1000, -1000)
        self.assertEqual(node.size(), minimum)
        self.assert_content_fits(node)

    def test_larger_sizes_survive_adjust_and_content_shrink(self):
        node = self.node()
        node.setSize(900, 600)
        plug = PywerPlug(type='extra input')
        node.add_input(plug)
        node.remove_input(plug)
        self.assertIsNone(plug.scene())
        node.adjust()
        self.assertEqual(node.size(), (900, 600))
        node.setSize(1, 1)
        self.assertLess(node.width, 900)
        self.assertLess(node.height, 600)
        self.assert_content_fits(node)

    def test_empty_node_and_larger_font(self):
        node = PywerNode(type='Long empty node header', node_obj=BaseNode())
        self.scene.addItem(node)
        node.setSize(1, 1)
        small = node.minimumSize()
        node.content_font.setPointSize(24)
        node.adjust()
        self.assertGreater(node.minimumSize().width(), small.width())
        self.assertGreater(node.minimumSize().height(), small.height())
        self.assert_content_fits(node)

    def test_caption_changes_and_embedded_children_grow_node(self):
        node = self.node()
        before = node.width
        node.name.setPlainText('Very long caption ' * 10)
        self.assertGreater(node.width, before)
        child = QtWidgets.QGraphicsRectItem(0, 0, 50, 60, node)
        child.setPos(400, 400)
        node.adjust()
        self.assertTrue(QtCore.QRectF(0, 0, *node.size()).contains(child.mapRectToParent(child.boundingRect())))

    def test_dynamic_plugs_and_connection_history(self):
        source = self.node('StringParameter')
        target = self.node('FormatString')
        original = len(target.inputs)
        for _ in range(4):
            self.stack.push(commands.ConnectPlugs(self.context, source.outputs[0], target.inputs[-1]))
        self.assertEqual(len(target.inputs), original + 4)
        self.assert_content_fits(target)
        saved = json.loads(json.dumps(scenetools.get_scene_data(self.scene)))
        for record in saved['nodes']:
            record['size'] = [1, 1]
        for loader in (scenetools.load_macro, scenetools.paste_macro):
            self.stack.clear()
            self.scene.clear()
            loader(self.context, self.stack, saved)
            restored = next(n for n in self.scene.get_all_nodes() if n.node_obj.type == 'FormatString')
            self.assertEqual(len(restored.inputs), original + 4)
            self.assert_content_fits(restored)

    def test_resizing_updates_connected_edge_endpoints(self):
        source = self.node()
        target = self.node('ConsoleWriter')
        target.setPos(800, 200)
        self.stack.push(commands.ConnectPlugs(self.context, source.outputs[0], target.inputs[0]))
        edge = self.scene.get_all_edges()[0]
        before = edge.start
        source.setSize(source.width + 150, source.height + 50)
        self.assertNotEqual(edge.start, before)
        self.assertEqual(edge.start, source.outputs[0].scenePos() + source.outputs[0].boundingRect().center())

    def test_dynamic_connection_undo_redo(self):
        source = self.node('StringParameter')
        target = self.node('FormatString')
        original = len(target.inputs)
        for _ in range(4):
            self.stack.push(commands.ConnectPlugs(self.context, source.outputs[0], target.inputs[-1]))
        self.stack.undo()
        self.assertEqual(len(target.inputs), original + 3)
        self.assert_content_fits(target)
        self.stack.redo()
        self.assertEqual(len(target.inputs), original + 4)
        self.assert_content_fits(target)

    def test_resize_history_preserves_expanded_sizes(self):
        node = self.node()
        node.setSize(400, 300)
        node.set_old_size(node.size())
        node.setSize(600, 500)
        self.stack.push(commands.ResizeItem(self.context, node))
        self.stack.undo()
        self.assertEqual(node.size(), (400, 300))
        self.stack.redo()
        self.assertEqual(node.size(), (600, 500))
        node.set_old_size(node.size())
        node.setSize(1, 1)
        self.stack.push(commands.ResizeItem(self.context, node))
        small = node.size()
        self.stack.undo()
        self.assertEqual(node.size(), (600, 500))
        self.stack.redo()
        self.assertEqual(node.size(), small)
        self.assert_content_fits(node)

    def test_load_paste_and_round_trip_normalize_legacy_sizes(self):
        source = self.node()
        source.setSize(700, 400)
        expanded = json.loads(json.dumps(scenetools.get_scene_data(self.scene)))
        self.scene.clear()
        scenetools.load_macro(self.context, self.stack, expanded)
        loaded = self.scene.get_all_nodes()[0]
        self.assertEqual(loaded.size(), (700, 400))
        legacy = json.loads(json.dumps(expanded))
        legacy['nodes'][0]['size'] = [1, 1]
        for loader in ('load_macro', 'paste_macro', 'load_scene_data'):
            self.stack.clear()
            self.scene.clear()
            if loader == 'load_scene_data':
                scenetools.load_scene_data(self.scene, legacy)
            else:
                getattr(scenetools, loader)(self.context, self.stack, legacy)
            node = self.scene.get_all_nodes()[0]
            self.assert_content_fits(node)
            normalized = json.loads(json.dumps(scenetools.get_scene_data(self.scene)))
            self.assertNotEqual(normalized['nodes'][0]['size'], [1, 1])
            self.stack.clear()
            self.scene.clear()
            scenetools.load_macro(self.context, self.stack, normalized)
            self.assertEqual(list(self.scene.get_all_nodes()[0].size()), normalized['nodes'][0]['size'])


if __name__ == '__main__':
    unittest.main()
