from PySide2 import QtCore, QtGui, QtWidgets
import sys


class FilterEdit(QtWidgets.QLineEdit):
    def __init__(self):
        super(FilterEdit, self).__init__()
        self.setPlaceholderText("Filter")


class SectionView(QtWidgets.QListView):
    doubleClicked = QtCore.Signal(object)

    def __init__(self, parent=None):
        super(SectionView, self).__init__(parent=parent)
        self.setViewMode(self.ListMode)
        self.setAlternatingRowColors(True)
        self.setWrapping(False)
        self.setResizeMode(self.Adjust)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                 QtWidgets.QSizePolicy.Minimum))
        self.setUniformItemSizes(True)
        self.setMovement(self.Snap)
        self.setSelectionMode(self.NoSelection)
        self.setEditTriggers(self.NoEditTriggers)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    def set_icon_mode(self):
        self.setViewMode(self.IconMode)
        self.setWrapping(True)
        self.setAlternatingRowColors(False)
        self.updateGeometry()

    def set_list_mode(self):
        self.setViewMode(self.ListMode)
        self.setWrapping(False)
        self.setAlternatingRowColors(True)
        self.updateGeometry()

    def sizeHint(self):
        import math

        item_height = self.sizeHintForRow(0)
        item_width = self.sizeHintForColumn(0)

        if not item_width:
            return QtCore.QSize()

        item_count = self.model().rowCount()

        area_width = self.childrenRect().width()
        items_per_row = (area_width - 1) // item_width

        rows = item_count
        if self.viewMode() == self.IconMode:
            rows = math.ceil(item_count / items_per_row)
            height = (rows * item_height) + (self.size().height() - self.childrenRect().height())
        else:
            height = (item_height * item_count) + 5  # TODO: hack to get rid of scrollbar

        size = QtCore.QSize()
        size.setHeight(height)

        return size

    def resizeEvent(self, event):
        super(SectionView, self).resizeEvent(event)
        self.updateGeometry()

    def filterItems(self, filter_text):
        self.model().setFilterRegExp(filter_text)

    def mouseDoubleClickEvent(self, event):
        index = self.indexAt(event.pos())
        if index.isValid():
            self.doubleClicked.emit(index)
            # return super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            return

        proxy_model = index.model()
        source_model = proxy_model.sourceModel()
        source_index = proxy_model.mapToSource(index)
        item_label = source_model.itemFromIndex(source_index).label

        icon = source_model.data(index=source_index, role=QtCore.Qt.DecorationRole)

        mimeData = QtCore.QMimeData()
        mimeData.setText(item_label)
        mimeData.setData('application/x-node', bytearray(item_label.encode()))

        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setPixmap(icon.pixmap(32, 32))

        dropAction = drag.exec_(QtCore.Qt.CopyAction | QtCore.Qt.MoveAction, QtCore.Qt.CopyAction)

        if dropAction == QtCore.Qt.MoveAction:
            self.close()
            self.update()

        return super().mousePressEvent(event)


class Section(QtWidgets.QWidget):
    def __init__(self, label, view):
        super(Section, self).__init__()

        self.label = label
        self.view = view

        self.button = QtWidgets.QToolButton()
        self.button.setText(self.label)
        self.button.setArrowType(QtCore.Qt.DownArrow)
        self.button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.button.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                        QtWidgets.QSizePolicy.Minimum))

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.button)
        layout.addWidget(self.view)

        self.setLayout(layout)

        self.setMinimumSize(QtCore.QSize(0, 0))
        self.button.clicked.connect(self.mousePressEvent)

    def mousePressEvent(self, event):
        self.view.setVisible(not self.view.isVisible())

        arrow = QtCore.Qt.RightArrow
        if self.view.isVisible():
            arrow = QtCore.Qt.DownArrow
        self.button.setArrowType(arrow)

    def filterItems(self, filter_text):
        self.setVisible(self.view.model().rowCount())


class SectionFilterProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self, section):
        super(SectionFilterProxyModel, self).__init__()
        self._section = section

    def filterAcceptsRow(self, sourceRow, sourceParent):
        source_model = self.sourceModel()
        column = 0
        index = source_model.index(sourceRow, column, sourceParent)
        sections = source_model.data(index, role=source_model.SectionRole)
        if self._section not in sections:
            return False

        return super(SectionFilterProxyModel, self).filterAcceptsRow(sourceRow, sourceParent)


class SectionModel(QtGui.QStandardItemModel):
    SectionRole = QtCore.Qt.UserRole + 1

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == self.SectionRole:
            item = self.itemFromIndex(index)
            try:
                return item.sections()
            except AttributeError:
                return []
        # elif role == QtCore.Qt.ToolTipRole:
        #     return

        return super(SectionModel, self).data(index, role)


class ToolItem(QtGui.QStandardItem):
    def __init__(self, icon, label, sections, tooltip=""):
        super(ToolItem, self).__init__(icon, label)
        self.label = label
        self._sections = sections

        self.setSizeHint(QtCore.QSize(50, 50))  # XXX if i dont do this, the SizeListView doesnt adjust correctly

        if tooltip:
            self.setToolTip(tooltip)

    def sections(self):
        return self._sections


class ToolBox(QtWidgets.QWidget):
    itemDoubleClickedSignal = QtCore.Signal(str)

    def __init__(self, sections=None):
        super(ToolBox, self).__init__()
        # XXX This prevents the occasional crashes on exit with the following error:
        #      QObject::startTimer: QTimer can only be used with threads started with QThread
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        main_widget_layout = QtWidgets.QVBoxLayout()
        main_widget_layout.setContentsMargins(0, 0, 0, 0)
        main_widget_layout.setSpacing(0)
        main_widget_layout.addStretch()
        self.main_widget = QtWidgets.QWidget()
        self.main_widget.setLayout(main_widget_layout)

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumSize(QtCore.QSize(0, 0))
        self.scroll_area.setWidget(self.main_widget)

        self.filter_edit = FilterEdit()

        view_mode = QtWidgets.QToolButton()
        view_mode.clicked.connect(self.toggle_view_mode)
        controls = QtWidgets.QWidget()
        controls_layout = QtWidgets.QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(0)
        controls_layout.addWidget(self.filter_edit)
        controls_layout.addSpacing(10)
        controls_layout.addWidget(view_mode)
        controls.setLayout(controls_layout)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(controls)
        self.layout.addWidget(self.scroll_area)
        self.setLayout(self.layout)

        self.model = SectionModel()

        if sections:
            self.addSections(sections)

    def toggle_view_mode(self):
        for section in self.sections():
            if section.view.viewMode() == section.view.ListMode:
                section.view.set_icon_mode()
            else:
                section.view.set_list_mode()

    def sections(self):
        sections = []
        for i in range(self.main_widget.layout().count()):
            widget = self.main_widget.layout().itemAt(i).widget()
            if widget:
                sections.append(widget)
        return sections

    def sectionNames(self):
        return [section.label for section in self.sections()]

    def addSection(self, section_name):
        if section_name in self.sectionNames():
            return

        section_view = SectionView()
        section_view.setIconSize(QtCore.QSize(30, 30))

        proxy_model = SectionFilterProxyModel(section_name)
        proxy_model.setSourceModel(self.model)
        section_view.setModel(proxy_model)

        section_view.doubleClicked.connect(self.itemDoubleClicked)

        section = Section(label=section_name, view=section_view)

        self.filter_edit.textChanged.connect(section_view.filterItems)
        self.filter_edit.textChanged.connect(section.filterItems)

        count = self.main_widget.layout().count()
        self.main_widget.layout().insertWidget(count - 1, section)

    def addSections(self, section_names):
        for section_name in section_names:
            self.addSection(section_name)

    def removeSection(self, section_name):
        for index, section in enumerate(self.sections()):
            if section.label == section_name:
                item = self.main_widget.layout().takeAt(index)
                item = item.layout() or item.widget()
                item.setParent(None)
                return

    def addItem(self, tool):
        self.addSections(tool.sections())
        self.model.appendRow(tool)

    def clear(self):
        self.model.clear()
        for section_name in self.sectionNames():
            self.removeSection(section_name=section_name)

    def itemDoubleClicked(self, index):
        proxy_model = index.model()
        source_index = proxy_model.mapToSource(index)
        item_label = self.model.itemFromIndex(source_index).label
        self.itemDoubleClickedSignal.emit(item_label)


@QtCore.Slot()
def itemSelected(event):
    print("Selected item:", event)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    tools = ['Maya', 'Houdini', 'Nuke', 'Katana', "Fusion", "Qube", "Mari", "Modo"] * 4
    sections = ["General", "Modeling", "Rigging", "Surfacing", "Finaling", "Lighting"]

    tool_library = ToolBox()
    import random

    for tool_name in tools:
        tool_sections = random.sample(sections, random.randint(0, len(sections)))
        tool_icon = QtGui.QIcon('./images/%s.png' % tool_name)
        item = ToolItem(icon=tool_icon, label=tool_name, sections=tool_sections)

        tool_library.addItem(item)

    # tool_library.setStyleSheet("QScrollBar::handle:horizontal{};")
    sshFile = "./css/darkorange.stylesheet"
    with open(sshFile, "r") as fh:
        tool_library.setStyleSheet(fh.read())

    tool_library.resize(250, 800)
    tool_library.show()

    tool_library.itemDoubleClicked.connect(itemSelected)

    sys.exit(app.exec_())
