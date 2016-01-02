import re
import logging


from PyQt5.QtWidgets import QMainWindow,QDesktopWidget,QFileDialog
from PyQt5.QtCore import Qt,QDir

from Config import Config,TreeModel
from ui_mainwindow import Ui_MainWindow

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
