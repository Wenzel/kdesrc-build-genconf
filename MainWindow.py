import re
import logging

from PyQt5.QtWidgets import QMainWindow,QDesktopWidget,QFileDialog
from PyQt5.QtCore import QDir

from ui_mainwindow import Ui_MainWindow

class ModuleSet():

    def __init__(self):
        self.name = ''
        self.repository = ''
        self.cmake_opts = ''
        self.use_modules = []
        self.branch = ''

    def setName(self, name):
        self.name = name

    def setRepository(self, repository):
        self.repository = repository

    def setCmakeOpts(self, cmake_opts):
        self.cmake_opts = cmake_opts

    def setBranch(self, branch):
        self.branch = branch

    def setUseModules(self, use_modules):
        self.use_modules = use_modules


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setupActions()
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

    def handleActionLoadConfigFile(self):
        filename = QFileDialog.getOpenFileName(self,
                                               "Select kdesrc-buildrc configuration file to load",
                                               QDir.homePath(),
                                               "*")
        if filename:
            # getOpenFileName returns a tuple
            module_set_list = self.configParser(filename[0])


    def configParser(self, filename):
        module_set_list = []
        f = open(filename, 'r')
        lines = f.readlines()
        while(lines):
            next_line = lines.pop(0)
            # test for module-set declaration
            match = re.match(r'^\s*module-set\s*(?P<module_name>.*)\s*$', next_line)
            if match:

                # module-set
                module = ModuleSet()
                name = match.group(1)
                module.setName(name)
                logging.debug('New module-set <{}>'.format(name))
                # until end-module, eat next line
                in_module = True
                while(in_module):
                    next_line = lines.pop(0)
                    # repository ?
                    match = re.match(r'^\s+repository\s+(?P<repository>.*)\s*$', next_line)
                    if match:
                        repo = match.group(1)
                        logging.debug('repository <{}>'.format(repo))
                        module.setRepository(repo)
                    # cmake-options ?
                    match = re.match(r'^\s+cmake-options\s+(?P<cmake_opts>.*)\s*$', next_line)
                    if match:
                        cmake_opts = match.group(1)
                        logging.debug('cmake opts <{}>'.format(cmake_opts))
                        module.setCmakeOpts(cmake_opts)
                    # use-modules ?
                    match = re.match(r'^\s+use-modules\s+(?P<use_modules>.*)\s*$', next_line)
                    if match:
                        use_modules_str = match.group(1)
                        logging.debug('use-modules <{}>'.format(use_modules_str))
                        use_modules_list = use_modules_str.split(' ')
                        module.setUseModules(use_modules_list)
                    # branch
                    match = re.match(r'^\s+branch\s+(?P<branch>.*)\s*$', next_line)
                    if match:
                        branch = match.group(1)
                        logging.debug('branch <{}>'.format(branch))
                        module.setBranch(branch)
                    # end module-set ?
                    match = re.match(r'^\s*end module-set\s*$', next_line)
                    if match:
                        in_module = False
                    continue
                module_set_list.append(module)
        f.close()
        return module_set_list