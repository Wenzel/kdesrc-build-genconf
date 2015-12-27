#!/usr/bin/env python

"""
Usage:
    kdesrc-build-genconf.py [options]

options:
    -h --help           Show this screen.
    --version           Show version.
"""

import sys
import os
import docopt
import requests
import logging
import xml.etree.ElementTree as et

from PyQt5.QtCore import QObject,QDir,QUrl,QAbstractItemModel,Qt
from PyQt5.QtGui import QStandardItemModel,QStandardItem
from PyQt5.QtWidgets import QApplication,QFileSystemModel,QTreeView,QMainWindow,QDesktopWidget,QAction
from PyQt5.QtQml import QQmlApplicationEngine

import utils.git as git
import utils.cmake as cmake
import utils.make as make

VERSION = '0.1'
SCRIPT_PATH = os.path.realpath(__file__)
SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)
KDE_PROJECTS_XML_URL = 'https://projects.kde.org/kde_projects.xml'

class App(QMainWindow):

    def __init__(self, treemodel):
        super().__init__()
        self.center()
        self.treemodel = treemodel
        # actions
        generateAction = QAction("Generate", self)
        generateAction.triggered.connect(self.generateActionHandle)
        # toolbar
        toolbar  = self.addToolBar("tb")
        toolbar.addAction(generateAction)
        # treeview
        treeview = QTreeView(self)
        treeview.setModel(treemodel)
        self.setCentralWidget(treeview)

    def generateActionHandle(self):
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

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        self.resize(screen.width() * 0.5, screen.height() * 0.6)
        mypos = self.geometry()
        hpos = (screen.width() - mypos.width()) / 2
        vpos = (screen.height() - mypos.height()) / 2
        self.move(hpos, vpos)



def update_build_metadata():
    git.update_submodules(SCRIPT_DIR)


def check_kde_projects_xml(source_dir):
    file_path = os.path.join(source_dir, 'kde_projects.xml')
    if not os.path.exists(file_path):
        logging.debug('Downloading kde_projects.xml from {}'.format(KDE_PROJECTS_XML_URL))
        r = requests.get(KDE_PROJECTS_XML_URL)
        with open(file_path, 'wb') as f:
            f.write(r.content)
    return file_path

def load_kde_projects_xml():
    xml_tree = None
    xml_path = check_kde_projects_xml(SCRIPT_DIR)
    with open(xml_path, 'r') as f:
        xml_content = f.read()
        xml_tree = et.fromstring(xml_content)
    return xml_tree

def init_logger():
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)

def setupModelData(xml_tree):
    model = QStandardItemModel()
    root = model.invisibleRootItem()

    for comp in xml_tree.findall('component'):
        comp_item = QStandardItem(comp.attrib['identifier'])
        comp_item.setCheckable(True)
        comp_item.setSelectable(False)
        for mod in comp.findall('module'):
            mod_item = QStandardItem(mod.attrib['identifier'])
            mod_item.setCheckable(True)
            for proj in mod.findall('project'):
                proj_item = QStandardItem(proj.attrib['identifier'])
                proj_item.setCheckable(True)
                mod_item.appendRow(proj_item)
            comp_item.appendRow(mod_item)
        root.appendRow(comp_item)

    return model


def main(cmdline):
    app = QApplication(sys.argv)
    init_logger()
    logging.debug(cmdline)
    # download and load kde_projects.xml
    xml_tree = load_kde_projects_xml()
    # setup model
    model = setupModelData(xml_tree)
    # clone/update kde-build-metadata
    update_build_metadata()

    view = App(model)
    view.show()

    app.exec_()


if __name__ == '__main__':
    cmdline = docopt.docopt(__doc__, version=VERSION)
    excode = main(cmdline)
    sys.exit(excode)
