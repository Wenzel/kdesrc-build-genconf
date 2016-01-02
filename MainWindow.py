import re
import logging


from PyQt5.QtWidgets import QMainWindow,QDesktopWidget,QFileDialog
from PyQt5.QtCore import Qt,QDir,QAbstractItemModel,QVariant,QModelIndex

from Config import Config
from ui_mainwindow import Ui_MainWindow

class TreeItem(object):

    def __init__(self, data, parent=None):
        self.data = data
        self.parent = parent
        self.children = []

    def dataAt(self, row):
        if (row >= self.columnCount()):
            return ""
        return self.data[row]

    def addChild(self, item):
        item.parent = self
        self.children.append(item)

    def child(self, row):
        return self.children[row]

    def childCount(self):
        return len(self.children)

    def columnCount(self):
        return len(self.data)

    def row(self):
        if self.parent:
            return self.parent.children.index(self)
        return 0

class TreeModel(QAbstractItemModel):

    def __init__(self, header_data, parent=None):
        super().__init__(parent)
        self.parents = []
        self.root = TreeItem(header_data)

    def columnCount(self, parent):
       if parent.isValid():
           return parent.internalPointer().columnCount()
       else:
           return self.root.columnCount()

    def rowCount(self, parent):
       if parent.column() > 0:
           return 0
       if not parent.isValid():
           parentItem = self.root
       else:
           parentItem = parent.internalPointer()
       return parentItem.childCount()

    def flags(self, index):
        if not index.isValid():
           return Qt.NoItemFlags
        return super().flags(index)

    def headerData(self, section, orientation, role=None):
        if (orientation == Qt.Horizontal and role == Qt.DisplayRole):
            return self.root.data[section]

        return QVariant()

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if parent.isValid():
            parent_item = parent.internalPointer()
        else:
            parent_item = self.root

        return self.createIndex(row, column, parent_item.child(row))

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent

        if (parent_item == self.root):
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def data(self, index, role):
        if not index.isValid():
            return None
        if role != Qt.DisplayRole:
            return None

        item = index.internalPointer()

        return QVariant(item.dataAt(index.column()))

    def setupModelData(self, config_root):
        for d in config_root.declarations:
            section_data = [d.type, d.id]
            section_item = TreeItem(section_data)
            for pair in d.content.items():
                sub_item_data = [pair[0], pair[1]]
                sub_item = TreeItem(pair)
                section_item.addChild(sub_item)
            self.root.addChild(section_item)


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, tree_model, parent=None):
        super().__init__(parent)
        self.treemodel = tree_model
        self.config = None
        self.setupUi(self)
        self.setupActions()
        self.project_treeview.setModel(self.treemodel)
        self.center()

    def setupActions(self):
        self.actionLoadConfigFile.triggered.connect(self.handleActionLoadConfigFile)
        self.actionCreateConfigFile.triggered.connect(self.handleActionCreateConfigFile)

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        self.resize(screen.width() * 0.7, screen.height() * 0.6)
        mypos = self.geometry()
        hpos = (screen.width() - mypos.width()) / 2
        vpos = (screen.height() - mypos.height()) / 2
        self.move(hpos, vpos)

    def handleActionGenerate(self):
        root = self.treemodel.invisibleRootItem()
        checked_items = self.find_checked_items(root)
        for item in checked_items:
            print(item)

    def find_checked_items(self, item):
        checked_items = []
        if (item.hasChildren()):
            for row in range(item.rowCount()):
                child = item.child(row)
                checked_items.extend(self.find_checked_items(child))
        if (item.checkState() == Qt.Checked):
            checked_items.append(item.text())
        return checked_items

    def handleActionCreateConfigFile(self):
        filename = QFileDialog.getSaveFileName(self,
                                       "New configuration file",
                                       QDir.homePath(),
                                       "*")
         # getSavedFileName returns a tuple
        filename = filename[0]
        self.config = Config(filename)
        self.displayConfig(self.config)


    def handleActionLoadConfigFile(self):
        filename = QFileDialog.getOpenFileName(self,
                                               "Select kdesrc-buildrc configuration file to load",
                                               QDir.homePath(),
                                               "*")
        # getOpenFileName returns a tuple
        filename = filename[0]
        if filename:
            self.config = Config(filename)
            self.config.load()
            self.displayConfig(self.config)

    def displayConfig(self, config):
        treemodel = TreeModel(["Declaration", "Value"])
        treemodel.setupModelData(config.root)
        self.element_treeview.setModel(treemodel)
        self.statusbar.showMessage(config.masterfile)

    def resetItemCheckState(self, item):
        if (item.hasChildren()):
            for row in range(item.rowCount()):
                item.child(row).setCheckState(Qt.Unchecked)
        item.setCheckState(Qt.Unchecked)
