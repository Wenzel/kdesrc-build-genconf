import re
import os
import logging

from PyQt5.QtCore import Qt,QAbstractItemModel,QVariant,QModelIndex
from PyQt5.QtGui import QStandardItemModel,QStandardItem

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
            item = d.getItem()
            self.root.addChild(item)

class Include():

    def __init__(self, filepath, parent_filepath):
        self.parent_filepath = parent_filepath
        self.filepath = filepath
        # relative
        if filepath[0] == '/':
            self.realpath = filepath
        else:
            self.realpath = os.path.dirname(self.parent_filepath) + '/' + filepath
        self.content = ConfigFile(self.realpath)
        self.content.load()

    def getItem(self):
        item = TreeItem(["include", self.filepath])
        for i in self.content.getItems():
            item.addChild(i)
        return item

class Section():

    def __init__(self, type, content, id=None,):
        self.type = type
        self.id = id
        self.content = content

    def getItem(self):
        item = TreeItem([self.type, self.id])
        for pair in self.content.items():
            subitem = TreeItem(pair)
            item.addChild(subitem)
        return item

class ConfigFile():

    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(self.filepath)
        self.declarations = []

    def getNextLine(self):
        # skip comments
        commented_line = True
        while (commented_line):
            next_line = self.fd.readline()
            if next_line == '': # EOF
                commented_line = False
            elif re.match(r'^\s*#.*$', next_line): # commented
                continue
            elif re.match(r'^\s*$', next_line): # useless
                continue
            else:
                commented_line = False
        next_line = next_line.replace('\n', '')
        # if line ends with \
        match = re.match(r'^.*\\$', next_line)
        if match:
            next_line = next_line[:-1] # remove trailing \
            next_line = next_line + self.getNextLine()
        return next_line

    def load(self):
        self.fd = open(self.filepath, 'r')
        logging.debug('loading new file <{}>'.format(self.filepath))
        next_line = self.getNextLine()
        grammar_sections = ['global', 'module', 'module-set', 'options']
        grammar_key_value = ['include']
        while(next_line):
            # section
            for s in grammar_sections:
                regex = r'^{}(?:\s+(?P<ID>.*))?\s*$'.format(s)
                match = re.match(regex, next_line)
                if match:
                    section_id = match.group(1)
                    logging.debug('new section {}'.format(section_id))
                    next_line = self.getNextLine()
                    content = {}
                    while(not re.match(r'^end\s.*$', next_line)):
                        match = re.match(r'\s+(?P<key>(?:\w|-)+)\s*(?P<value>.*)$', next_line)
                        if match:
                            key = match.group(1)
                            value = match.group(2)
                            logging.debug('found [{}] => [{}]'.format(key, value))
                            content[key] = value
                        # loop
                        next_line = self.getNextLine()
                    section = Section(s, content, section_id)
                    self.declarations.append(section)
            # include ?
            match = re.match(r'^include\s(?P<filepath>.*)$', next_line)
            if match:
                filepath = match.group(1)
                logging.debug('new include {}'.format(filepath))
                include = Include(filepath, self.filepath)
                self.declarations.append(include)
            next_line = self.getNextLine()

    def getItems(self):
        items = []
        for d in self.declarations:
            items.append(d.getItem())
        return items

    def defineNewConfig(self):
        # add global section
        type = "global"
        content = {
            "branch-group" : "kf5-qt5",
            "kdedir" : "",
            "qtdir" : "/usr",
            "source-dir" : "",
            "build-dir" : "",
            "cxxfags" : "",
            "cmake-options" : "",
            "make-options" : "-j4"
        }
        s = Section(type, content)
        self.declarations.append(s)

class Config():

    def __init__(self, masterfile=None):
        self.masterfile = masterfile
        self.root = ConfigFile(self.masterfile)

    def load(self):
        self.root.load()

    def defineNewConfig(self):
        self.root.defineNewConfig()

    def getFileTreeModel(self):
        file_treemodel = QStandardItemModel()
        file_treemodel.setHorizontalHeaderLabels(["config file"])
        root = file_treemodel.invisibleRootItem()
        root.appendRow(self.root.getStandardItem())

        return file_treemodel

