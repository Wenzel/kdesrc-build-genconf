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
        self.setupConnect()
        self.project_treeview.setModel(self.treemodel)
        self.center()

    def setupConnect(self):
        self.actionLoadConfigFile.triggered.connect(self.handleActionLoadConfigFile)
        self.actionCreateConfigFile.triggered.connect(self.handleActionCreateConfigFile)
        self.actionWriteConfigFile.triggered.connect(self.handleActionWriteConfigFile)
        self.element_treeview.clicked.connect(self.handleSignalElementTreeViewClicked)


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
        self.config.defineNewConfig()
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

    def handleActionWriteConfigFile(self):
        self.config.writeConfig()


    def displayConfig(self, config):
        treemodel = TreeModel(["Declaration", "Value"])
        treemodel.setupModelData(config.root)
        self.element_treeview.setModel(treemodel)
        # enable some actions and statusbar
        self.actionWriteConfigFile.setEnabled(True)
        self.statusbar.showMessage(config.masterfile)

    def handleSignalElementTreeViewClicked(self, index):
        data = index.internalPointer().data
        root = self.project_treeview.model().invisibleRootItem()
        # reset the project treeview state anyway
        self.resetItemCheckState(root)
        # use-modules ?
        if data[0] == "use-modules":
            # enable project_treeview and enable correponding project
            self.project_treeview.setEnabled(True)
            # check projects specified by this module-set
            use_modules_str = data[1]
            use_modules = re.split('\s+', use_modules_str)
            logging.debug(use_modules)
            self.checkItem(root, use_modules)
        else:
            self.project_treeview.setEnabled(False)

    def resetItemCheckState(self, item):
        if (item.hasChildren()):
            for row in range(item.rowCount()):
                self.resetItemCheckState(item.child(row))
        item.setCheckState(Qt.Unchecked)

    def checkItem(self, item, projects):
        if not projects:
            return
        try:
            index = projects.index(item.text())
            # set check state
            item.setCheckState(Qt.Checked)
            # set the state of it's parents as partially checked
            parent = item.parent()
            while parent:
                parent.setCheckState(Qt.PartiallyChecked)
                parent = parent.parent()
            # remove from projects
            projects.pop(index)
        except ValueError:
            pass
        # find in children
        for row in range(item.rowCount()):
            self.checkItem(item.child(row), projects)