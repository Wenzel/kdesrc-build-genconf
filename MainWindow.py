import re
import logging

from PyQt5.QtWidgets import QMainWindow,QDesktopWidget,QFileDialog
from PyQt5.QtCore import Qt,QDir

from ui_mainwindow import Ui_MainWindow

class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, tree_model, parent=None):
        super().__init__(parent)
        self.treemodel = tree_model
        self.setupUi(self)
        self.setupActions()
        self.treeview.setModel(tree_model)
        self.center()

    def setupActions(self):
        self.actionLoadConfigFile.triggered.connect(self.handleActionLoadConfigFile)

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        self.resize(screen.width() * 0.5, screen.height() * 0.6)
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

    def handleActionLoadConfigFile(self):
        filename = QFileDialog.getOpenFileName(self,
                                               "Select kdesrc-buildrc configuration file to load",
                                               QDir.homePath(),

                                               "*")
        if filename:
            # getOpenFileName returns a tuple
            filename = filename[0]
            module_set_list = []
            # reset treemodel checked items
            root = self.treemodel.invisibleRootItem()
            self.resetItemCheckState(root)


    def resetItemCheckState(self, item):
        if (item.hasChildren()):
            for row in range(item.rowCount()):
                item.child(row).setCheckState(Qt.Unchecked)
        item.setCheckState(Qt.Unchecked)
