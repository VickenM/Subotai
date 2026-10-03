"""Qt 6 integration checks; run with python -m unittest discover -s tests -v."""
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import unittest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PIL import Image
from PySide6 import QtCore, QtGui, QtWidgets

import appnode
import commands
import register
from subotai import MainWindow

ROOT = Path(__file__).resolve().parents[1]


class Qt6IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            register.reload_node_registry()
        if output.getvalue():
            raise AssertionError(output.getvalue())

    def setUp(self):
        self.callback_errors = []
        self.old_hook = sys.excepthook
        sys.excepthook = lambda *error: self.callback_errors.append(error)
        self.window = MainWindow()

    def tearDown(self):
        try:
            self.window.parameters.set_node_obj(None)
            self.window.undo_stack.clear()
            self.window.deactivate_event_nodes()
            self.window.exit_app()
            self.window.deleteLater()
            self.app.sendPostedEvents(None, QtCore.QEvent.Type.DeferredDelete)
        finally:
            sys.excepthook = self.old_hook
        self.assertEqual(self.callback_errors, [])

    def load_example(self, path):
        data = json.loads(path.read_text())
        # Loading must not launch the examples' timers, file operations or email.
        for node in data['nodes']:
            node['active'] = False
        self.window.load_data(data)
        return data

    def test_all_builtin_nodes_and_parameter_panels(self):
        self.assertEqual(len(register.node_registry), 44)
        for name in register.node_registry:
            with self.subTest(node=name):
                node = appnode.new_node(name)
                # Give Qt ownership of the graphics items until GUI-thread teardown.
                # Unowned node/runtime cycles can otherwise be collected while the
                # next node is constructing its C++ children.
                self.window.scene.add_node(node)
                self.window.parameters.set_node_obj(node.node_obj)
                self.window.parameters.set_node_obj(None)

    def test_examples_round_trip_and_render(self):
        for path in sorted((ROOT / 'examples').glob('*.json')):
            with self.subTest(example=path.name):
                data = self.load_example(path)
                saved = json.loads(self.window.dump_json())
                for key in ('nodes', 'edges', 'groups'):
                    self.assertEqual(len(saved[key]), len(data[key]))
                image = QtGui.QImage(1000, 700, QtGui.QImage.Format.Format_ARGB32)
                image.fill(QtCore.Qt.GlobalColor.transparent)
                painter = QtGui.QPainter(image)
                try:
                    self.window.scene.render(painter)
                finally:
                    painter.end()
                self.window.undo_stack.clear()
                self.window.scene.clear()
                self.window.load_data(saved)
                self.assertEqual(len(self.window.scene.get_all_edges()), len(data['edges']))
                self.window.undo_stack.clear()
                self.window.scene.clear()

    def test_hello_world_signal_execution(self):
        self.load_example(ROOT / 'examples' / '01helloworld.json')
        timer = next(n.node_obj for n in self.window.scene.get_all_nodes()
                     if n.node_obj.type == 'Timer')
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            timer.calculate.emit()
            # The example's computation executes on the worker QThread.
            from PySide6.QtTest import QTest
            for _ in range(100):
                QTest.qWait(10)
                if 'hello world!' in output.getvalue():
                    break
        self.assertIn('hello world!', output.getvalue())

    def test_add_connect_undo_redo(self):
        stack = self.window.undo_stack
        context = self.window.context
        stack.push(commands.AddNode(context, 'Counter'))
        source = self.window.scene.get_all_nodes()[0]
        stack.push(commands.AddNode(context, 'ConsoleWriter'))
        target = next(n for n in self.window.scene.get_all_nodes() if n is not source)
        stack.push(commands.ConnectPlugs(context, source.outputs[0], target.inputs[0]))
        self.assertEqual(len(self.window.scene.get_all_edges()), 1)
        stack.undo()
        self.assertEqual(len(self.window.scene.get_all_edges()), 0)
        stack.undo()
        self.assertEqual(len(self.window.scene.get_all_nodes()), 1)
        stack.redo()
        stack.redo()
        self.assertEqual(len(self.window.scene.get_all_nodes()), 2)
        self.assertEqual(len(self.window.scene.get_all_edges()), 1)

    def test_boolean_parameter_changes(self):
        node = appnode.new_node('BooleanParameter')
        self.window.scene.add_node(node)
        self.window.parameters.set_node_obj(node.node_obj)
        param = node.node_obj.get_first_param('param')
        checkbox = self.window.parameters.flayout.itemAt(
            1, QtWidgets.QFormLayout.ItemRole.FieldRole).widget()
        self.assertIsInstance(checkbox, QtWidgets.QCheckBox)
        checkbox.setChecked(False)
        self.assertIs(param.value, False)
        checkbox.setChecked(True)
        self.assertIs(param.value, True)

    def test_filter_zoom_and_window_render(self):
        toolbox = self.window.toolbox
        toolbox.filter_edit.setText('Counter')
        count = sum(section.view.model().rowCount() for section in toolbox.sections())
        self.assertEqual(count, 1)
        toolbox.filter_edit.setText('no-such-node')
        self.assertEqual(sum(s.view.model().rowCount() for s in toolbox.sections()), 0)
        toolbox.toggle_view_mode()
        for section in toolbox.sections():
            section.view.sizeHint()
        toolbox.filter_edit.clear()
        self.window.resize(1200, 800)
        self.window.show()
        self.app.processEvents()
        self.assertFalse(self.window.grab().isNull())
        view = self.window.view
        event = QtGui.QWheelEvent(
            QtCore.QPointF(100, 100), QtCore.QPointF(100, 100),
            QtCore.QPoint(), QtCore.QPoint(0, 120),
            QtCore.Qt.MouseButton.NoButton, QtCore.Qt.KeyboardModifier.ControlModifier,
            QtCore.Qt.ScrollPhase.NoScrollPhase, False)
        before = view.transform().m11()
        view.wheelEvent(event)
        self.assertGreater(view.transform().m11(), before)

    def test_pillow_to_qt_image(self):
        node = appnode.new_node('Viewer')
        self.window.scene.add_node(node)
        node.node_obj.get_first_param('image').value = Image.new('RGB', (32, 32), 'red')
        node.node_obj.compute()
        self.assertFalse(node.node_obj.widget.label.pixmap().isNull())


if __name__ == '__main__':
    unittest.main()
